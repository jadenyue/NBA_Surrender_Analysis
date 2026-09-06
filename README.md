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

It can be shown that as an NBA coach, once the opponent has emptied his bench, you become substantially more likely to empty yours as well.

Counts of games surrendered when one of the coaches surrender

|                       | surrendered | did not |  rate |
|-----------------------|------------:|--------:|------:|
| Opponent surrendered  |       6,584 |   6,412 | 50.7% |
| Opponent did not      |       6,412 |  51,678 | 11.0% |

(By strictly looking at count data, it initially seems like the odds ratio is 8.28, from (6,584 × 51,678) / (6,412 × 6,412). However, this ratio would create positive bias and overestimate the true effect of one coach surrendering on the other coaches decision, as time left in the game is not considered. 
I learned to think about it like this: Imagine two coaches that are completely ignorant to what the other coach does, each independently flipping a coin every thirty seconds to determine whether to surrender. In a game decided with 20 minutes left they get 40 flips each, while in one decided with 5 minutes left, only 10 flips. The long games will show "both quit" far more often, and show that one coach surrendering influences the other coach to do the same when there is no effect.)


A discrete-time hazard model fixes this. Every settled team-game is split into 30 second intervals, and each interval is marked as 1 or 0 based on if the coach pulled the starters during this one, given the coach hadn't yet? Because every interval is the same length, having more of them cannot inflate the effect.

|                                        |             Value |
|----------------------------------------|------------------:|
| Settled team-games                     |            23,328 |
| Half-minute intervals                  |           311,080 |
| Intervals ending in a pull             |            11,245 |
| Baseline chance per interval           |             3.61% |
| Intervals with the opponent already gone |    65,030 (20.9%) |


The model fitted to those intervals:
```
logit(chance of pulling in interval k) = α_k + β × [opponent already gone]
```

Fitting gives:
```
Odds Ratio: 1.487, 95% CI [1.423, 1.554], z = +17.6.
```
Which means coaches whose opponent has already pulled his starters are 1.487 times more likely, in odds, to pull their own.





Additionally, Adding an interaction between the indicator and the length of the settled window, we can see the effect weakening sharply when the window widens. When a game is settled with 2 to 4 minutes left, the opponent's bench emptying doubles the odds of following. While in games that are settled with more than twelve minutes, the effect is almost nonexistent. A narrow window forces a decision and the other coach going first makes it acceptable, whereas with twenty minutes left, there's no urgency and no need to commit. 


| Settled window | Odds ratio |       95% CI |
|----------------|-----------:|-------------:|
| 1 minute       |       2.29 | [2.10, 2.49] |
| 2 minutes      |       2.17 | [2.01, 2.35] |
| 4 minutes      |       1.96 | [1.83, 2.09] |
| 8 minutes      |       1.59 | [1.52, 1.66] |
| 12 minutes     |       1.29 | [1.23, 1.36] |
| 16 minutes     |       1.05 | [0.98, 1.13] |
| 20 minutes     |       0.86 | [0.77, 0.95] |



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

##Different coaches differ in their tendency to surrender enormously 
This was the question that initially inspired this study: finding 








