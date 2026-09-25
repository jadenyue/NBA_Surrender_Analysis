"""
Tests whether coaches differ in how readily they surrender once you hold the
situation, the era and the roster constant.

Reads the per-season files from extract_surrenders.py, attaches a coach and a team
rating to every game, expands everything into bands of the required comeback rate,
then fits two logistic regressions and compares them.

    python analyse_coaches.py
"""

import glob

import numpy as np
import pandas as pd
from scipy.stats import chi2


# narrow at the bottom, wide at the top, since almost nothing happens below 1
BAND_EDGES = [0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 7, 10, 15, 25, 1000000]

MIN_TRAILING_GAMES = 60
MIN_FOR_RANKING = 100

# Basketball Reference spells a few teams differently to the play-by-play
BBREF_TO_FEED = {
    'BRK': 'BKN',
    'CHO': 'CHA',
    'PHO': 'PHX',
    'NOH': 'NOP',
    'NOK': 'NOP',
    'CHH': 'CHA',
    'WSB': 'WAS',
}


def load_seasons():
    # use the per season files if extract_surrenders.py has been run, otherwise
    # fall back on the combined file that ships with this
    parts = sorted(glob.glob('cb_parts/*.csv'))
    if parts:
        data = pd.concat([pd.read_csv(p) for p in parts], ignore_index=True)
    else:
        data = pd.read_csv('comeback_rate_all.csv')
    data['season_end_year'] = data.season.str[:4].astype(int) + 1
    return data


def number_games_within_season(data):
    # number each team's games in play order so coaches can be matched to a stretch
    order = data[['team', 'season_end_year', 'game_id']].drop_duplicates()
    order = order.sort_values(['team', 'season_end_year', 'game_id'])
    order['team_game'] = order.groupby(['team', 'season_end_year']).cumcount() + 1
    return data.merge(order, on=['team', 'season_end_year', 'game_id'], how='left')


def build_coach_lookup(records):
    # the records give the range of games each coach was in charge for
    lookup = {}
    for record in records.itertuples():
        first = int(record.team_game_first)
        last = int(record.team_game_last)
        for game_number in range(first, last + 1):
            lookup[(record.team, int(record.season_end_year), game_number)] = record.coach
    return lookup


def attach_coaches(data):
    """
    Attribution comes from the coach records, not from the surrender events.

    Joining on the events would throw away every game where the coach refused,
    which is most of the data and exactly the part that identifies the stubborn
    ones.
    """
    records = pd.read_csv('05_coach_records.csv')
    records['team'] = records.team_bbref.replace(BBREF_TO_FEED)

    data = number_games_within_season(data)
    lookup = build_coach_lookup(records)

    coaches = []
    for team, year, game_number in zip(data.team, data.season_end_year, data.team_game):
        if pd.isna(game_number):
            coaches.append(None)
        else:
            coaches.append(lookup.get((team, int(year), int(game_number))))

    data['coach'] = coaches
    return data


def attach_team_strength(data):
    strength = pd.read_csv('11_team_strength.csv')
    strength = strength[['team', 'season_end_year', 'srs']]
    return data.merge(strength, on=['team', 'season_end_year'], how='left')


def which_band(rate):
    for index in range(len(BAND_EDGES) - 1):
        if BAND_EDGES[index] <= rate < BAND_EDGES[index + 1]:
            return index
    return len(BAND_EDGES) - 2


def band_label(index):
    low = BAND_EDGES[index]
    high = BAND_EDGES[index + 1]
    if high > 100000:
        return f'{low:g} and above'
    return f'{low:g} to {high:g}'


def expand_into_bands(data):
    """
    One row per team-game becomes one row per band the team reached.

    A team that got to an RCR of 4.2 passed through every band below it on the way
    and the coach chose not to act in any of them, so those all get a 0. Only the
    band the game ended in can be a 1.
    """
    rows = []

    for rate, surrendered, coach, srs, year in zip(
        data.rate, data.event, data.coach, data.srs, data.season_end_year
    ):
        top_band = which_band(rate)
        for band in range(top_band + 1):
            if surrendered == 1 and band == top_band:
                marked = 1
            else:
                marked = 0
            rows.append({
                'band': band,
                'surrendered': marked,
                'coach': coach,
                'srs': srs,
                'year': year,
            })

    return pd.DataFrame(rows)


def summarise_bands(panel):
    summary = panel.groupby('band').agg(
        at_risk=('surrendered', 'size'),
        surrendered=('surrendered', 'sum'),
    ).reset_index()
    summary['hazard'] = (summary.surrendered / summary.at_risk * 100).round(1)
    summary['rcr_range'] = [band_label(b) for b in summary.band]
    return summary[['rcr_range', 'at_risk', 'surrendered', 'hazard']]


def fit_logistic(design, outcome):
    """
    Logistic regression by Newton-Raphson.

        b  <-  b + (X'WX)^-1 X'(y - p),   W = diag( p(1-p) )

    No closed form for this the way there is for ordinary regression, so it has to
    be searched for. The log-likelihood is a single smooth hill with one peak, which
    is why it lands in about nine steps from a standing start.
    """
    # small ridge keeps the solve stable when two dummy columns are nearly identical
    ridge = 1e-9
    coefficients = np.zeros(design.shape[1])

    for iteration in range(100):
        linear = design @ coefficients
        predicted = 1 / (1 + np.exp(-linear))
        predicted = np.clip(predicted, 1e-12, 1 - 1e-12)

        weights = predicted * (1 - predicted)
        hessian = (design * weights[:, None]).T @ design
        hessian = hessian + np.eye(design.shape[1]) * ridge
        gradient = design.T @ (outcome - predicted)

        step = np.linalg.solve(hessian, gradient)
        coefficients = coefficients + step

        if np.max(np.abs(step)) < 1e-11:
            break

    linear = design @ coefficients
    predicted = np.clip(1 / (1 + np.exp(-linear)), 1e-12, 1 - 1e-12)
    log_likelihood = np.sum(
        outcome * np.log(predicted) + (1 - outcome) * np.log(1 - predicted)
    )

    return coefficients, float(log_likelihood)


def build_design_matrix(panel, include_coaches):
    """
    Band dummies hold the situation constant, season dummies hold the era constant,
    SRS holds roster quality constant. The first model leaves the coach out so it
    predicts as well as it can while blind to who was in charge.
    """
    band_dummies = pd.get_dummies(panel.band, prefix='band', drop_first=True)
    season_dummies = pd.get_dummies(panel.year, prefix='season', drop_first=True)

    pieces = [
        np.ones((len(panel), 1)),
        band_dummies.values.astype(float),
        season_dummies.values.astype(float),
        panel.srs.values.reshape(-1, 1),
    ]

    coach_names = []
    if include_coaches:
        coach_dummies = pd.get_dummies(panel.coach, prefix='coach', drop_first=True)
        pieces.append(coach_dummies.values.astype(float))
        coach_names = [column[6:] for column in coach_dummies.columns]

    return np.column_stack(pieces), coach_names


def compare_models(panel):
    """
    Fit with and without the coach, then check the improvement against what the
    extra parameters would have bought on their own.

    Adding parameters always improves fit, because part of any dataset is noise and
    noise is partly fittable. A parameter carrying nothing is worth about one point
    of the statistic, so the count of parameters is the benchmark.
    """
    outcome = panel.surrendered.values.astype(float)

    without_design, _ = build_design_matrix(panel, include_coaches=False)
    _, without_fit = fit_logistic(without_design, outcome)

    with_design, coach_names = build_design_matrix(panel, include_coaches=True)
    coefficients, with_fit = fit_logistic(with_design, outcome)

    statistic = 2 * (with_fit - without_fit)
    degrees_of_freedom = len(coach_names)
    p_value = chi2.sf(statistic, degrees_of_freedom)

    print()
    print(f'  without coach effects:  log-likelihood {without_fit:,.1f}')
    print(f'  with coach effects:     log-likelihood {with_fit:,.1f}')
    print(f'  improvement:            {with_fit - without_fit:,.1f} points')
    print()
    print(f'  LR chi-square {statistic:.0f} on {degrees_of_freedom} degrees of freedom')
    print(f'  p = {p_value:.1e}')

    return coefficients, coach_names


def hazard_ratios(coefficients, coach_names, panel):
    """
    One coach has to be dropped as the reference, so his effect is zero by
    definition. Adding him back and recentring on the mean makes 1.00 the league
    average rather than whoever happened to be left out.
    """
    count = len(coach_names)
    effects = list(coefficients[-count:]) + [0.0]

    reference = sorted(set(panel.coach.dropna()) - set(coach_names))
    names = coach_names + reference

    effects = np.array(effects)
    effects = effects - effects.mean()

    table = pd.DataFrame({'coach': names, 'hazard_ratio': np.exp(effects)})
    return table.sort_values('hazard_ratio', ascending=False).reset_index(drop=True)


def expected_counts(data):
    """
    What each coach's era and rosters imply, from a model that never sees the coach.

    This is the plain language version of the same comparison, one row per game
    rather than one per band.
    """
    season_dummies = pd.get_dummies(data.season_end_year, prefix='season',
                                    drop_first=True)
    design = np.column_stack([
        np.ones((len(data), 1)),
        season_dummies.values.astype(float),
        data.srs.values.reshape(-1, 1),
    ])
    coefficients, _ = fit_logistic(design, data.event.values.astype(float))
    predicted = 1 / (1 + np.exp(-(design @ coefficients)))
    return pd.Series(predicted, index=data.index)


def variance_decomposition(data):
    """
    Split the spread in surrender rates into era and roster, sampling noise, and
    what is left for the coach.

    Sampling noise has a known size. For a proportion p on n games it is p(1-p)/n,
    so averaging that across coaches and subtracting it, along with the variance
    the era and roster model already explains, leaves the coach.
    """
    grouped = data.groupby('coach').agg(
        games=('event', 'size'),
        surrendered=('event', 'sum'),
        expected=('expected', 'sum'),
    )
    grouped = grouped[grouped.games >= MIN_TRAILING_GAMES]

    baseline = grouped.surrendered.sum() / grouped.games.sum()
    observed = np.var(grouped.surrendered / grouped.games, ddof=1)
    circumstance = np.var(grouped.expected / grouped.games, ddof=1)
    noise = np.mean(baseline * (1 - baseline) / grouped.games)
    coach = max(observed - circumstance - noise, 0)

    print()
    print(f'  league mean surrender rate {baseline * 100:.1f}%')
    print(f'  era and roster  {circumstance:.5f}  {circumstance / observed * 100:.0f}%')
    print(f'  sampling noise  {noise:.5f}  {noise / observed * 100:.0f}%')
    print(f'  the coach       {coach:.5f}  {coach / observed * 100:.0f}%')
    print(f'  total observed  {observed:.5f}')
    print(f'  coach-attributable SD {np.sqrt(coach) * 100:.1f} percentage points')


def main():
    data = load_seasons()
    print(f'{len(data):,} trailing team-games loaded, '
          f'{data.season.min()} to {data.season.max()}')

    data = attach_coaches(data)
    data = attach_team_strength(data)
    data = data[data.coach.notna() & data.srs.notna()]

    game_counts = data.groupby('coach').size()
    enough = game_counts[game_counts >= MIN_TRAILING_GAMES].index
    data = data[data.coach.isin(enough)].reset_index(drop=True)

    print(f'{len(data):,} with a coach and a team rating attached')
    print(f'{data.coach.nunique()} coaches with {MIN_TRAILING_GAMES}+ trailing games')
    print(f'surrendered in {data.event.mean() * 100:.1f}% of them')

    panel = expand_into_bands(data)
    baseline = panel.surrendered.mean() * 100
    print()
    print(f'expanded into {len(panel):,} band-observations')
    print(f'{int(panel.surrendered.sum()):,} of them are a surrender')
    print(f'baseline chance per band {baseline:.2f}%')
    print()
    print(summarise_bands(panel).to_string(index=False))

    coefficients, coach_names = compare_models(panel)
    ratios = hazard_ratios(coefficients, coach_names, panel)

    data['expected'] = expected_counts(data)
    variance_decomposition(data)

    by_coach = data.groupby('coach')
    ratios['trailing_games'] = ratios.coach.map(by_coach.size())
    ratios['surrendered'] = ratios.coach.map(by_coach.event.sum())
    ratios['pct_per_band'] = (ratios.hazard_ratio * baseline).round(2)
    ratios['expected'] = ratios.coach.map(by_coach.expected.sum()).round(1)
    ratios['obs_over_exp'] = (ratios.surrendered / ratios.expected).round(3)
    ratios['mean_srs'] = ratios.coach.map(by_coach.srs.mean()).round(2)
    ratios['mean_season'] = ratios.coach.map(by_coach.season_end_year.mean()).round(0)
    ratios['hazard_ratio'] = ratios.hazard_ratio.round(3)

    ranked = ratios[ratios.trailing_games >= MIN_FOR_RANKING]
    spread = ranked.hazard_ratio.max() / ranked.hazard_ratio.min()

    print()
    print(f'coaches with {MIN_FOR_RANKING}+ trailing games: {len(ranked)}')
    print(f'hazard ratios {ranked.hazard_ratio.min():.2f} to '
          f'{ranked.hazard_ratio.max():.2f}, a {spread:.1f} fold range')

    columns = ['coach', 'hazard_ratio', 'pct_per_band', 'trailing_games', 'surrendered']
    print()
    print('  quickest to surrender')
    print(ranked.head(6)[columns].to_string(index=False))
    print()
    print('  slowest to surrender')
    print(ranked.tail(6).iloc[::-1][columns].to_string(index=False))

    ratios.to_csv('coach_hazard_ratios.csv', index=False)
    print()
    print('written to coach_hazard_ratios.csv')


if __name__ == '__main__':
    main()
