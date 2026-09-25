"""
Everything in the report that the main model does not produce.

Four parts:

  1. The peak RCR table, meaning how often teams came back from a given position
  2. Whether a coach's rate moves when his own roster changes
  3. Whether his rate travels with him between franchises
  4. The season trend, and the checks that it is not a data artefact

    python coach_vs_roster.py
"""

import numpy as np
import pandas as pd


RCR_BANDS = [(0, 0.5), (0.5, 1), (1, 1.5), (1.5, 2), (2, 2.5),
             (2.5, 3), (3, 4), (4, 5), (5, 7), (7, 1000000)]

MIN_SEASONS = 4
MIN_SRS_SPREAD = 1.5        # a coach needs his rosters to actually have varied
MIN_GAMES_PER_CLUB = 60
MIN_GAMES_FOR_STABILITY = 250
MIN_SRS_GAP = 5
BOOTSTRAP_DRAWS = 3000

BBREF_TO_FEED = {
    'BRK': 'BKN',
    'CHO': 'CHA',
    'PHO': 'PHX',
    'NOH': 'NOP',
    'NOK': 'NOP',
    'CHH': 'CHA',
    'WSB': 'WAS',
}


def load_all():
    # the league level tables do not need a coach, so they use every row
    return pd.read_csv('comeback_rate_all.csv')


def load_with_coaches():
    data = pd.read_csv('comeback_rate_all.csv')

    records = pd.read_csv('05_coach_records.csv')
    records['team'] = records.team_bbref.replace(BBREF_TO_FEED)

    order = data[['team', 'season_end_year', 'game_id']].drop_duplicates()
    order = order.sort_values(['team', 'season_end_year', 'game_id'])
    order['team_game'] = order.groupby(['team', 'season_end_year']).cumcount() + 1
    data = data.merge(order, on=['team', 'season_end_year', 'game_id'], how='left')

    lookup = {}
    for record in records.itertuples():
        for number in range(int(record.team_game_first), int(record.team_game_last) + 1):
            lookup[(record.team, int(record.season_end_year), number)] = record.coach

    coaches = []
    for team, year, number in zip(data.team, data.season_end_year, data.team_game):
        if pd.isna(number):
            coaches.append(None)
        else:
            coaches.append(lookup.get((team, int(year), int(number))))
    data['coach'] = coaches

    strength = pd.read_csv('11_team_strength.csv')[['team', 'season_end_year', 'srs']]
    data = data.merge(strength, on=['team', 'season_end_year'], how='left')

    data = data[data.coach.notna() & data.srs.notna()]
    counts = data.groupby('coach').size()
    return data[data.coach.isin(counts[counts >= 60].index)].reset_index(drop=True)


def peak_rcr_table(data):
    """
    How often a team came back from a given position, using only teams that never
    surrendered. A team that surrendered has effectively forfeited, so including
    them would drag the win rates down for reasons unrelated to how winnable the
    position was.
    """
    held_on = data[data.event == 0]

    print()
    print('PEAK RCR FACED, AND HOW OFTEN THEY CAME BACK')
    print()
    print(f"  {'Peak RCR faced':<16}{'Team-games':>12}{'Came back and won':>20}")

    for low, high in RCR_BANDS:
        in_band = held_on.rate.between(low, high, inclusive='left')
        if high > 100000:
            label = f'{low:g} and above'
        else:
            label = f'{low:g} to {high:g}'
        won = held_on[in_band].won_game.mean() * 100
        print(f'  {label:<16}{int(in_band.sum()):>12,}{won:>19.1f}%')


def coach_season_table(data):
    # one row per coach per team per season, dropping the very short stints
    table = data.groupby(['coach', 'team', 'season_end_year']).agg(
        games=('event', 'size'),
        surrendered=('event', 'sum'),
        srs=('srs', 'first'),
    ).reset_index()
    table = table[table.games >= 20].copy()
    table['surrender_pct'] = table.surrendered / table.games * 100
    return table


def coach_club_table(coach_seasons):
    rows = []
    for (coach, team), group in coach_seasons.groupby(['coach', 'team']):
        rows.append({
            'coach': coach,
            'team': team,
            'games': group.games.sum(),
            'surrendered': group.surrendered.sum(),
            'srs': np.average(group.srs, weights=group.games),
        })
    table = pd.DataFrame(rows)
    table['surrender_pct'] = table.surrendered / table.games * 100
    return table[table.games >= MIN_GAMES_PER_CLUB]


def least_squares(design, outcome):
    coefficients, *_ = np.linalg.lstsq(design, outcome, rcond=None)
    residuals = outcome - design @ coefficients
    dof = len(outcome) - design.shape[1]
    variance = float(residuals @ residuals) / dof
    standard_errors = np.sqrt(np.diag(np.linalg.pinv(design.T @ design)) * variance)
    return coefficients, standard_errors


def within_coach_slope(coach_seasons):
    """
    Does the same coach change when his roster changes?

    Subtracting each coach's own averages leaves only his year to year movement, so
    differences between coaches cannot contribute. Only coaches whose rosters
    actually varied are included, since a coach whose teams were all the same
    quality says nothing about how quality matters.
    """
    def usable(group):
        return len(group) >= MIN_SEASONS and group.srs.std() > MIN_SRS_SPREAD

    subset = coach_seasons.groupby('coach').filter(usable).copy()
    subset['srs_demeaned'] = subset.srs - subset.groupby('coach').srs.transform('mean')
    subset['pct_demeaned'] = (subset.surrender_pct
                              - subset.groupby('coach').surrender_pct.transform('mean'))

    design = np.column_stack([np.ones(len(subset)), subset.srs_demeaned.values])
    coefficients, standard_errors = least_squares(design, subset.pct_demeaned.values)

    slope = coefficients[1]
    error = standard_errors[1]

    print()
    print('WITHIN-COACH, ACROSS ROSTER STRENGTH')
    print()
    print(f'  {subset.coach.nunique()} coaches with {MIN_SEASONS}+ seasons and real '
          f'roster variation')
    print(f'  slope {slope:+.3f} percentage points per SRS point')
    print(f'  SE {error:.3f}, t = {slope / error:+.2f}, n = {len(subset)} coach-seasons')
    print(f'  so about {slope * 10:+.1f} points per ten SRS points')


def pair_main_club_against_others(coach_clubs, column):
    """
    For each coach who worked at two or more clubs, pair his figure at his biggest
    stop against the weighted average of his others.
    """
    pairs = []
    movers = coach_clubs.groupby('coach').filter(lambda group: len(group) >= 2)

    for coach, group in movers.groupby('coach'):
        group = group.sort_values('games', ascending=False)
        main = group.iloc[0][column]
        others = np.average(group.iloc[1:][column], weights=group.iloc[1:].games)
        pairs.append((main, others))

    return np.array(pairs)


def bootstrap_correlation(pairs, draws=BOOTSTRAP_DRAWS, seed=0):
    # resample coaches rather than games, since the coach is the unit here
    generator = np.random.default_rng(seed)
    estimates = []
    for _ in range(draws):
        picked = generator.integers(0, len(pairs), len(pairs))
        estimates.append(np.corrcoef(pairs[picked, 0], pairs[picked, 1])[0, 1])
    return np.percentile(estimates, 2.5), np.percentile(estimates, 97.5)


def travels_between_clubs(coach_clubs):
    rate_pairs = pair_main_club_against_others(coach_clubs, 'surrender_pct')
    srs_pairs = pair_main_club_against_others(coach_clubs, 'srs')

    correlation = np.corrcoef(rate_pairs[:, 0], rate_pairs[:, 1])[0, 1]
    low, high = bootstrap_correlation(rate_pairs)
    srs_correlation = np.corrcoef(srs_pairs[:, 0], srs_pairs[:, 1])[0, 1]

    print()
    print('DOES THE TENDENCY TRAVEL BETWEEN FRANCHISES')
    print()
    print(f'  {len(rate_pairs)} coaches at 2+ clubs with '
          f'{MIN_GAMES_PER_CLUB}+ trailing games each')
    print(f'  r = {correlation:+.3f}, 95% CI [{low:+.3f}, {high:+.3f}], '
          f'{BOOTSTRAP_DRAWS} bootstrap draws')
    print(f'  same pairing on roster strength gives r = {srs_correlation:+.3f}')


def stability_tables(coach_clubs):
    """
    Coaches who had a real change of roster between clubs, sorted by how much their
    rate moved. Both filters matter: without a real SRS gap there is nothing to
    respond to, and without enough games the rates are noise.
    """
    rows = []
    movers = coach_clubs.groupby('coach').filter(lambda group: len(group) >= 2)

    for coach, group in movers.groupby('coach'):
        group = group.sort_values('srs')
        weakest = group.iloc[0]
        strongest = group.iloc[-1]
        rows.append({
            'coach': coach,
            'games': group.games.sum(),
            'srs_gap': strongest.srs - weakest.srs,
            'rate_change': group.surrender_pct.max() - group.surrender_pct.min(),
            'weak': f'{weakest.team} {weakest.srs:+.1f} -> {weakest.surrender_pct:.0f}%',
            'strong': f'{strongest.team} {strongest.srs:+.1f} '
                      f'-> {strongest.surrender_pct:.0f}%',
        })

    table = pd.DataFrame(rows)
    table = table[(table.srs_gap >= MIN_SRS_GAP)
                  & (table.games >= MIN_GAMES_FOR_STABILITY)]

    print()
    print(f'ROSTER CHANGED, DID THE COACH  ({len(table)} coaches qualify)')

    for title, ordered in [('most stable', table.nsmallest(8, 'rate_change')),
                           ('least stable', table.nlargest(8, 'rate_change'))]:
        print()
        print(f'  {title}')
        print(f"  {'Coach':<18}{'Weak roster':<22}{'Strong roster':<22}"
              f"{'gap':>6}{'change':>9}")
        for _, row in ordered.iterrows():
            print(f"  {row.coach:<18}{row.weak:<22}{row.strong:<22}"
                  f"{row.srs_gap:>6.1f}{row.rate_change:>8.1f}pt")

    print()
    print(f'  median rate change across all {len(table)}: '
          f'{table.rate_change.median():.1f} points')


def season_trend(data):
    by_season = data.groupby('season').agg(
        games=('event', 'size'),
        surrendered=('event', 'sum'),
    ).reset_index()
    by_season['rate'] = by_season.surrendered / by_season.games * 100

    surrenders_only = data[data.event == 1]
    by_season['median_rcr'] = by_season.season.map(
        surrenders_only.groupby('season').rate.median()
    )
    by_season['year'] = by_season.season.str[:4].astype(int) + 1

    first_five = by_season.head(5)
    last_five = by_season.tail(5)

    print()
    print('SURRENDERING OVER TIME')
    print()
    print(f"  {'Season':<10}{'Trailing':>10}{'Surrendered':>13}{'Rate':>8}"
          f"{'Median RCR':>13}")
    for _, row in by_season.iterrows():
        print(f'  {row.season:<10}{int(row.games):>10,}{int(row.surrendered):>13}'
              f'{row.rate:>7.1f}%{row.median_rcr:>13.2f}')

    print()
    print(f'  first five seasons {first_five.surrendered.sum() / first_five.games.sum() * 100:.1f}%'
          f'   last five {last_five.surrendered.sum() / last_five.games.sum() * 100:.1f}%')
    print(f'  rate against year r = {np.corrcoef(by_season.year, by_season.rate)[0, 1]:+.3f}')
    print(f'  median RCR {first_five.median_rcr.mean():.2f} -> '
          f'{last_five.median_rcr.mean():.2f}, '
          f'r = {np.corrcoef(by_season.year, by_season.median_rcr)[0, 1]:+.3f}')

    early = by_season[by_season.year <= 2013]
    late = by_season[by_season.year >= 2014]
    print()
    print(f'  through 2012-13: mean {early.surrendered.sum() / early.games.sum() * 100:.1f}%, '
          f'trend r = {np.corrcoef(early.year, early.rate)[0, 1]:+.3f}')
    print(f'  2013-14 onwards: mean {late.surrendered.sum() / late.games.sum() * 100:.1f}%, '
          f'trend r = {np.corrcoef(late.year, late.rate)[0, 1]:+.3f}')


def completeness_checks(data):
    """
    The trend would be an artefact if early logs were simply thinner, since a
    missing substitution makes a surrender undetectable. Tightening the filter
    should flatten the trend if that is what is happening.
    """
    logs = pd.read_csv('log_completeness.csv')[['game_id', 'team', 'n_subs_logged']]
    merged = data.merge(logs, on=['game_id', 'team'], how='left')

    print()
    print('IS THE TREND JUST BETTER RECORD KEEPING')
    print()
    print(f"  {'filter':<24}{'team-games':>12}{'rate against year':>20}")

    for threshold, label in [(0, 'no filter'), (18, '18+ substitutions'),
                             (20, '20+ substitutions'), (22, '22+ substitutions')]:
        subset = merged[merged.n_subs_logged >= threshold]
        by_season = subset.groupby('season').agg(
            games=('event', 'size'),
            surrendered=('event', 'sum'),
        ).reset_index()
        by_season['rate'] = by_season.surrendered / by_season.games * 100
        by_season['year'] = by_season.season.str[:4].astype(int) + 1
        correlation = np.corrcoef(by_season.year, by_season.rate)[0, 1]
        print(f'  {label:<24}{len(subset):>12,}{correlation:>+19.3f}')

    passed = pd.read_csv('log_completeness.csv')
    by_season = passed.groupby('season').agg(
        pass_rate=('log_complete', 'mean'),
        median_subs=('n_subs_logged', 'median'),
    )
    print()
    print(f'  pass rate {by_season.pass_rate.iloc[0] * 100:.1f}% in '
          f'{by_season.index[0]} rising to '
          f'{by_season.pass_rate.iloc[-1] * 100:.1f}% in {by_season.index[-1]}')
    print(f'  median substitutions logged {by_season.median_subs.iloc[0]:.0f} -> '
          f'{by_season.median_subs.iloc[-1]:.0f}')


def main():
    everything = load_all()
    attributed = load_with_coaches()
    print(f'{len(everything):,} trailing team-games, '
          f'{len(attributed):,} with a coach and a team rating')

    peak_rcr_table(everything)

    coach_seasons = coach_season_table(attributed)
    coach_clubs = coach_club_table(coach_seasons)

    within_coach_slope(coach_seasons)
    travels_between_clubs(coach_clubs)
    stability_tables(coach_clubs)

    season_trend(everything)
    completeness_checks(everything)


if __name__ == '__main__':
    main()
