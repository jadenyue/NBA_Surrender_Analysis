# NBA Surrender Analysis - When coaches give up
A study and statistical analysis of NBA coaches' tendency to "surrender " in games. Built from substitution-level play-by-play records across 30 seasons: 12,996 events, 1996-97 to 2025-26, across 108 coaches. 
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

It can also be noted that at every min remaining point, the leading coach waits two to three points longer than the trailing one. The reason is asymmetric risk: conceding a loss costs nothing, but calling off a win you might still lose can be punished.

## Surrendering in the NBA happens far more than it used to
During the 5 seasons spanning the 1996-97 season to the 2000-01 season, 22.8% of games involved at least one team surrendering. 25 years later however (2020-21 to 2025-26), a surrender event now happens in 36.6% of all games. Correlation with season +0.880.

| Season |   n | Events per game | Median margin | Median min left |
|--------|----:|----------------:|--------------:|----------------:|
| 1996-97   | 339 |           0.285 |            21 |             3.9 |
| 1997-98   | 347 |           0.292 |            21 |             3.4 |
| 1998-99   | 211 |           0.291 |            20 |             3.0 |
| 1999-00   | 365 |           0.307 |            20 |             3.7 |
| 2000-01   | 326 |           0.274 |            20 |             3.9 |

| 2021-22   | 620 |           0.504 |            21 |             3.5 |
| 2022-23   | 553 |           0.450 |            20 |             3.4 |
| 2023-24   | 705 |           0.573 |            21 |             3.5 |
| 2024-25   | 677 |           0.550 |            21 |             3.4 |
| 2025-26   | 673 |           0.545 |            21 |             3.7 |

What is surprising is that the median margin at surrender has sat at roughly 21 points for thirty years. Coaches are not quitting earlier within a given blowout as their threshold is identical, the number of situations calling for it grew. This could support the argument that the league as a whole is getting less competitive as more games result in blowouts.








