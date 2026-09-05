# NBA Surrender Analysis - When coaches give up
A study and statistical analysis of NBA coach's tendency to "surrender " in games. Built from substitution-level play-by-play records across 30 seasons: 12,996 events, 1996-97 to 2025-26, across 108 coaches. 
The moment a coach makes the decision to surrender is observable. It is when the **last of his five starters leaves the floor and does not come back**. Analysing the accumulated data on this event revealed several interesting phenomena and trends that point towards where the league is headed. 
# What I found
## The Surrender Curve - Coaches quit relative to the clock
NBA coaches decide to quit not at a fixed deficit, but make their decision based on score differential and time left in the game. The margin they need scales with how much time is left to erase it. 
By modelling the relationship, we create the surrender curve to represent the typical point differential at which a coach decides to surrender for each time remaining. 
| Min remaining |     n | Trailing | Leading |
|---------------|------:|---------:|--------:|
| 0-2           | 3,166 |       14 |      16 |
| 2-3           | 2,223 |       18 |      20 |
| 3-4           | 1,718 |       20 |      22 |
| 4-5           | 1,253 |       21 |      24 |
| 5-6           | 1,018 |       23 |      26 |
| 6-8           | 1,198 |       25 |      27 |
| 8-10          |   694 |       26 |      29 | 
| 10-12         |   231 |       27 |      29 |
| 12+           | 1,495 |       25 |      28 |

The full derivation of these counts can be found in XXXXX

It can also be noted that at every min remaining point, the leading coach waits two to three points longer than the trailing one. The reason is asymmetric risk: conceding a loss costs nothing, but losing after calling off a lead is never a good look.

## Surrendering in the NBA happens far more than it used to
During the 5 seasons spanning the 1996-97 season to the 2000-01 season, 22.8% of games involved at least one team surrendering. 25 years later however (2020-21 to 2025-26), a surrender event now happens in 36.6% of all games. Correlation with season +0.880.

| Season |   n | Events per game | Median margin | Median min left |
|--------|----:|----------------:|--------------:|----------------:|
| 1996-97   | 339 |           0.285 |            21 |             3.9 |
| 1997-98   | 347 |           0.292 |            21 |             3.4 |
| 1998-99   | 211 |           0.291 |            20 |             3.0 |
| 1999-00   | 365 |           0.307 |            20 |             3.7 |
| 2000-01   | 326 |           0.274 |            20 |             3.9 |
| ...       | ... |           ... |           ...|             ... |
| 2021-22   | 620 |           0.504 |            21 |             3.5 |
| 2022-23   | 553 |           0.450 |            20 |             3.4 |
| 2023-24   | 705 |           0.573 |            21 |             3.5 |
| 2024-25   | 677 |           0.550 |            21 |             3.4 |
| 2025-26   | 673 |           0.545 |            21 |             3.7 |

What is surprising is that the median margin at surrender has been at roughly 21 points for thirty years. Coaches are not quitting earlier within a given blowout as their threshold is identical, its just that the number of situations calling for it grew. This could support the argument that the league as a whole is getting less competitive as more games result in blowouts.

## The Action of Surrendering is Contagious

From the data it can be shown that as an NBA coach, once the opponent has emptied his bench, you become substantially more likely to empty yours as well.

Odds ratio 1.35, 95% CI [1.29, 1.42], z = +13.0.

Which was obtained first using counts of games surrendered when one of the coaches surrender

|                   | surrendered | did not |  rate |
|-------------------|---------:|--------:|------:|
| Opponent surrendered |    6,068 |   5,177 | 54.0% |
| Opponent did not  |    5,177 |   6,906 | 42.8% |

(By strictly looking at count data, it initially seems like the odds ratio is 1.56 by simply doing (6068 × 6906) / (5177 × 5177). However, this ratio would create positive bias and overestimate the true effect of one coach surrendering on the other coaches decision, as time left in the game is not considered. 
I learned to think about it like this: Imagine two coaches that are completely ignorant to what the other coach does, each independently flipping a coin every thirty seconds to determine whether to surrender. In a game decided with 20 minutes left they get 40 flips each, while in one decided with 5 minutes left, only 10 flips. The long games will show "both quit" far more often, and show that one coach surrendering influences the other coach to do the same when there is no effect.)

This problem can be mitigated using the Mantel-Haenszel estimator. Rather than one count per game, by splitting the settled time into multiple bands of equal **count** (unequal widths), then taking a weighted average, we can adjust for the differences in time settled, and weight each stratum by how much information it holds about the odds ratio. 
Additionally, a filter of only looking at games settled with at least  4 minutes remaining was implemented to as if the game only stopped being competitive with a minute left, the coach had no window to act, and you can't measure how readily a coach quits in a game where quitting was never an option. 

By using 5 bands (found little marginal gain in eliminating confounding through increasing bands), we get: 

| Settled band |      n |     a |     b |     c |     d |    OR |  a·d/n |  b·c/n | 
|--------------|-------:|------:|------:|------:|------:|------:|-------:|-------:|
| 3.99–5.13    |  4,660 |   628 |   809 |   809 | 2,414 | 2.316 |  325.3 |  140.4 |
| 5.13–6.70    |  4,680 |   950 | 1,023 | 1,023 | 1,684 | 1.529 |  341.8 |  223.6 |
| 6.70–8.77    |  4,690 | 1,296 | 1,086 | 1,086 | 1,222 | 1.343 |  337.7 |  251.5 |
| 8.77–12.20   |  4,634 | 1,476 | 1,113 | 1,113 |   932 | 1.110 |  296.9 |  267.3 |
| 12.20–31.08  |  4,664 | 1,718 | 1,146 | 1,146 |   654 | 0.856 |  240.9 |  281.6 |
| **TOTAL**    | 23,328 |       |       |       |       |       | 1542.6 | 1164.4 |

Where 
|            | Meaning                                                        |
|------------|----------------------------------------------------------------|
| Settled band | how long the game had been decided for, in minutes           |
| `n`        | team-games in that band                                        |
| `a`        | opponent quit and I quit                                       |
| `b`        | opponent quit, I did not                                       |
| `c`        | I quit, opponent did not                                       |
| `d`        | neither quit                                                   |
| `OR`       | the odds ratio for that band alone = `a·d / b·c`                |
| `a·d/n`, `b·c/n` | the two parts that get summed to combine bands     |

Note the counts within each band slightly deviates from being exactly equal due to multiple instances of games being settled at the same time. However, the effect can be considered negligible. 

From this, we get a odds ratio of 1.325 (1542.6/1164.4), which means coaches whose opponent has already pulled his starters are 1.325 times more likely, in odds, to pull their own.

Additionally, from the 'OR' column of table, we can also interpret the gradient. When a game is settled with four or five minutes left, the opponent's bench emptying doubles the odds of following. While in games that are settled with more than twelve minutes, the effect is nonexistent. A narrow window forces a decision and the other coach going first makes it acceptable, whereas with twenty minutes left, there's no urgency and no need to commit. 

The findings align with former coach and TNT analyst Mike Fratello's comments from 2018, where he noted how coaches often think about ["Does the other team pull their starters out, and if they do, do you pull yours out?" and how "All of that goes into a coach's decision process."](https://bleacherreport.com/articles/2762927-the-truths-about-garbage-time-in-the-nba)

##Variables that do and don't matter in determining surrender odds

By identifying three variables that potentially influence a coach's decision to surrender and conducting statistical analysis on the effects, it can be seen that only one of the three parameters can be shown to have a real effect.

| Predictor                        |    OR |        95% CI |     z | Real effect? |
|----------------------------------|------:|--------------:|------:|--------------|
| Own team strength (per SRS point) | 1.101 | [1.094, 1.109] | +28.9 | yes         |
| Playing at home                   | 1.026 | [0.967, 1.088] |  +0.8 | no          |
| Opponent strength (per SRS point) | 0.998 | [0.991, 1.004] |  -0.7 | no          |

 Playing at home has no effect on coach's decision to surrender. Which is surprising as home-court advantage is one of the most studied aspects in all of sports. It raises scoring rates (Ribeiro et al., 2016), inflates subjective stat-keeping (Bommela et al.,2021), and bends officiating (Price, Remer & Stone, 2012). Home court advantage turns up almost everywhere, but does not change a coach's tendency to surrender. On average, theres no embarrassment effect in front of your own crowd, no extra push for the home fans who bought tickets. 

Opponent quality is irrelevant too as coaches respond to their own position rather than to who is beating them. What does matter is the strength of your own team. Coaches of good teams give up on games more quickly than bad ones, which may seem counterintuitive at first, but a good team's bench is deeper, so emptying it costs less, and the star player of a good team would be more valuable to rest and protect.









