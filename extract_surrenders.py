"""
Pulls the surrender measure out of raw NBA play-by-play.

For every trailing team in every regular season game this works out the required
comeback rate, which is the deficit divided by the minutes remaining, and records
either the rate at the moment the coach pulled all five starters or, if he never
did, the worst rate his team faced while they were still on.

Run a few seasons at a time:

    python extract_surrenders.py 2022-23 2023-24

Each season goes to its own file under cb_parts/ so a long run can be stopped and
picked up again later.
"""

import sys
import os
import zipfile
import shutil

import numpy as np
import pandas as pd


PBP_COLUMNS = [
    'GAME_ID',
    'EVENTNUM',
    'EVENTMSGTYPE',
    'PERIOD',
    'PCTIMESTRING',
    'SCOREMARGIN',
    'HOMEDESCRIPTION',
    'PLAYER1_ID',
    'PLAYER1_TEAM_ABBREVIATION',
    'PLAYER2_ID',
    'PLAYER2_TEAM_ABBREVIATION',
]

SUBSTITUTION = 8
MIN_SECONDS_LEFT = 60
MIN_DEFICIT = 6
FIRST_SEASON = 2001
ARCHIVE = 'repo.zip'
OUTPUT_DIR = 'cb_parts'


def period_length(period):
    if period <= 4:
        return 720
    return 300


def period_start(period):
    if period <= 4:
        return (period - 1) * 720
    return 2880 + (period - 5) * 300


def is_regular_season(game_id):
    # third character of the game id is the competition code, 2 is regular season
    digits = str(int(game_id)).zfill(10)
    return digits[2] == '2'


def add_timestamps(plays):
    clock = plays.PCTIMESTRING.astype(str).str.extract(r'(\d+):(\d+)')
    has_clock = clock[0].notna()

    minutes = clock[0].astype(float)
    seconds = clock[1].astype(float)
    seconds_remaining = minutes * 60 + seconds

    plays = plays.copy()
    plays['has_clock'] = has_clock

    # the feed gives time left in the period, we want seconds elapsed
    elapsed_in_period = []
    elapsed_in_game = []
    for period, remaining, valid in zip(plays.PERIOD, seconds_remaining, has_clock):
        if not valid:
            elapsed_in_period.append(np.nan)
            elapsed_in_game.append(np.nan)
            continue
        within = period_length(period) - remaining
        elapsed_in_period.append(within)
        elapsed_in_game.append(period_start(period) + within)

    plays['period_clock'] = elapsed_in_period
    plays['game_clock'] = elapsed_in_game
    return plays[plays.has_clock].drop(columns='has_clock')


def add_running_margin(plays):
    # SCOREMARGIN only gets filled in on scoring plays so carry it forward
    plays = plays.copy()
    margin = plays.SCOREMARGIN.replace('TIE', '0')
    plays['margin'] = pd.to_numeric(margin, errors='coerce')
    plays['margin'] = plays.groupby('GAME_ID').margin.ffill().fillna(0)
    return plays


def find_home_team(game):
    # the home team is whoever shows up in the HOMEDESCRIPTION column
    described = game[game.HOMEDESCRIPTION.notna() & game.PLAYER1_TEAM_ABBREVIATION.notna()]
    if described.empty:
        return None
    common = described.PLAYER1_TEAM_ABBREVIATION.mode()
    if common.empty:
        return None
    return common.iloc[0]


def find_teams(game):
    first = set(game.PLAYER1_TEAM_ABBREVIATION.dropna())
    second = set(game.PLAYER2_TEAM_ABBREVIATION.dropna())
    return sorted(first | second)


def players_on_court_at_period_start(period_plays, team):
    """
    Who was already out there when the period began.

    Has to be based on each player's first event. A starter who goes off and comes
    back in the same quarter turns up as an incoming substitute later on, so
    the code needs to ensure he isn't dropped dropped.
    """
    first_role = {}

    for event_type, player_out, team_out, player_in, team_in in zip(
        period_plays.EVENTMSGTYPE,
        period_plays.PLAYER1_ID,
        period_plays.PLAYER1_TEAM_ABBREVIATION,
        period_plays.PLAYER2_ID,
        period_plays.PLAYER2_TEAM_ABBREVIATION,
    ):
        if event_type == SUBSTITUTION:
            substitution_team = team_out if isinstance(team_out, str) else team_in
            if substitution_team != team:
                continue
            if pd.notna(player_out) and player_out != 0:
                first_role.setdefault(player_out, 'out')
            if pd.notna(player_in) and player_in != 0:
                first_role.setdefault(player_in, 'in')
        else:
            if team_out == team and pd.notna(player_out) and player_out != 0:
                first_role.setdefault(player_out, 'active')

    return [player for player, role in first_role.items() if role != 'in']


def collect_substitutions(period_plays, team):
    moves = {}
    substitutions = period_plays[period_plays.EVENTMSGTYPE == SUBSTITUTION]

    for clock, player_out, team_out, player_in, team_in in zip(
        substitutions.period_clock,
        substitutions.PLAYER1_ID,
        substitutions.PLAYER1_TEAM_ABBREVIATION,
        substitutions.PLAYER2_ID,
        substitutions.PLAYER2_TEAM_ABBREVIATION,
    ):
        substitution_team = team_out if isinstance(team_out, str) else team_in
        if substitution_team != team:
            continue
        if pd.notna(player_out) and player_out != 0:
            moves.setdefault(player_out, []).append((float(clock), 'out'))
        if pd.notna(player_in) and player_in != 0:
            moves.setdefault(player_in, []).append((float(clock), 'in'))

    return moves


def pair_into_spells(moves, on_at_start, length):
    if on_at_start:
        moves = [(0.0, 'in')] + moves
    if moves and moves[-1][1] == 'in':
        moves = moves + [(float(length), 'out')]

    spells = []
    index = 0
    while index < len(moves) - 1:
        this_move = moves[index]
        next_move = moves[index + 1]
        if this_move[1] == 'in' and next_move[1] == 'out':
            spells.append((this_move[0], next_move[0]))
            index += 2
        else:
            index += 1
    return spells


def starter_spells(game, team, starters):
    """
    On court spells for each starter, in game clock seconds.

    Done period by period on purpose. The feed never logs the outgoing half of a
    substitution at a period break, so a player who finishes a quarter on the floor
    and does not start the next one simply stops appearing. Closing any open spell
    at the end of each period stops him being credited with minutes he never played.
    """
    spells = {starter: [] for starter in starters}

    for period, period_plays in game.groupby('PERIOD', sort=True):
        offset = period_start(period)
        length = period_length(period)
        on_at_start = set(players_on_court_at_period_start(period_plays, team))
        moves = collect_substitutions(period_plays, team)

        for starter in starters:
            player_moves = list(moves.get(starter, []))
            started_period = starter in on_at_start
            if not player_moves and not started_period:
                continue
            for start, end in pair_into_spells(player_moves, started_period, length):
                spells[starter].append((offset + start, offset + end))

    return spells


def surrender_time(spells, game_end, tolerance=1.0):
    """
    When the last starter left for good, or None if the team never surrendered.

    The None case is the important bit. Without requiring that nobody comes back
    this would fire on the ordinary second quarter bench rotation, where all five
    happen to be off together in a game still being contested.
    """
    final_exits = []

    for starter, player_spells in spells.items():
        if not player_spells:
            return None
        last_exit = max(end for _, end in player_spells)
        if last_exit >= game_end - tolerance:
            return None
        final_exits.append(last_exit)

    if len(final_exits) != 5:
        return None
    return max(final_exits)


def margin_from_this_teams_view(game, team, home_team):
    # SCOREMARGIN is home minus away so it needs flipping for the away side
    if team == home_team:
        return game.margin.values.astype(float)
    return -game.margin.values.astype(float)


def worst_position_faced(deficits, seconds_left):
    # only count moments where the team was properly behind with real time left
    live = (deficits <= -MIN_DEFICIT) & (seconds_left >= MIN_SECONDS_LEFT)
    if not live.any():
        return None

    minutes_left = np.maximum(seconds_left[live] / 60.0, 1e-9)
    rates = np.abs(deficits[live]) / minutes_left
    worst = int(np.argmax(rates))

    return {
        'rate': float(rates[worst]),
        'deficit': float(abs(deficits[live][worst])),
        'minutes_left': float(seconds_left[live][worst] / 60.0),
    }


def position_at_surrender(game_clock, deficits, moment, game_end):
    """
    The deficit and clock when the starters came off.

    Two different lookups here. The clock comes from the substitution's own
    timestamp, since that substitution is the event. The score comes from the last
    row at or before it in EVENTNUM order, which is the league's own sequence.

    Note the timestamp column is not sorted. Play clock runs backwards somewhere in
    about 90% of games, so a binary search returns the wrong row.
    """
    at_or_before = np.flatnonzero(game_clock <= moment)
    if len(at_or_before) == 0:
        return None

    last_row = int(at_or_before[-1])
    deficit = deficits[last_row]
    minutes_left = (game_end - moment) / 60.0

    if deficit > -MIN_DEFICIT:
        return None
    if minutes_left * 60 < MIN_SECONDS_LEFT:
        return None

    return {
        'rate': float(abs(deficit) / max(minutes_left, 1e-9)),
        'deficit': float(abs(deficit)),
        'minutes_left': float(minutes_left),
    }


def process_season(path, season):
    plays = pd.read_csv(path, usecols=PBP_COLUMNS)
    plays = add_timestamps(plays)
    plays = plays[[is_regular_season(game_id) for game_id in plays.GAME_ID]]
    plays = plays.sort_values(['GAME_ID', 'PERIOD', 'EVENTNUM'], kind='mergesort')
    plays = add_running_margin(plays)

    rows = []

    for game_id, game in plays.groupby('GAME_ID', sort=False):
        game_end = float(game.game_clock.max())
        home_team = find_home_team(game)
        if home_team is None:
            continue

        game_clock = game.game_clock.values.astype(float)
        seconds_left = game_end - game_clock

        for team in find_teams(game):
            opening_period = game[game.PERIOD == 1]
            starters = players_on_court_at_period_start(opening_period, team)

            # if we cannot pin down exactly five, skip rather than guess
            if len(starters) != 5:
                continue

            spells = starter_spells(game, team, starters)
            moment = surrender_time(spells, game_end)
            deficits = margin_from_this_teams_view(game, team, home_team)

            if moment is None:
                position = worst_position_faced(deficits, seconds_left)
                surrendered = 0
            else:
                position = position_at_surrender(game_clock, deficits, moment, game_end)
                surrendered = 1

            # nothing to record if the team was never meaningfully behind
            if position is None:
                continue

            rows.append({
                'game_id': game_id,
                'team': team,
                'event': surrendered,
                'rate': position['rate'],
                'margin': position['deficit'],
                'min_left': position['minutes_left'],
                'season': season,
            })

    return pd.DataFrame(rows)


def extract_season_file(archive, season, destination):
    matches = [name for name in archive.namelist() if name.endswith(f'{season}_pbp.csv')]
    if not matches:
        return False
    with archive.open(matches[0]) as source, open(destination, 'wb') as target:
        shutil.copyfileobj(source, target)
    return True


def main(seasons):
    if not os.path.exists(ARCHIVE):
        print(f'Cannot find {ARCHIVE} in this directory.')
        print()
        print('This script rebuilds the measure from raw play-by-play, which is not')
        print('shipped here because it runs to a couple of gigabytes. Download')
        print('github.com/sumitrodatta/nba-alt-awards as a zip, rename it to')
        print(f'{ARCHIVE}, and put it alongside this script.')
        print()
        print('If you only want to reproduce the results, comeback_rate_all.csv is')
        print('already built. Run analyse_coaches.py or coach_vs_roster.py instead.')
        return

    if not seasons:
        print('Give it one or more seasons, for example:')
        print('    python extract_surrenders.py 2022-23 2023-24')
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    archive = zipfile.ZipFile(ARCHIVE)

    for season in seasons:
        end_year = int(season[:4]) + 1
        if end_year < FIRST_SEASON:
            print(f'  {season}: before the study period, skipping')
            continue

        output_path = os.path.join(OUTPUT_DIR, f'{season}.csv')
        if os.path.exists(output_path):
            print(f'  {season}: already done')
            continue

        temporary_path = f'/tmp/{season}.csv'
        if not extract_season_file(archive, season, temporary_path):
            print(f'  {season}: not in archive')
            continue

        results = process_season(temporary_path, season)
        results.to_csv(output_path, index=False)
        os.remove(temporary_path)

        surrendered = int(results.event.sum())
        print(f'  {season}: {len(results)} trailing team-games, {surrendered} surrendered')


if __name__ == '__main__':
    main(sys.argv[1:])
