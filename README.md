# How hopeless does it have to get before a coach gives up?

Some coaches empty the bench the moment a game slips away. Others ride their starters through a forty point deficit. This is a measure of that difference, built from 29 seasons of NBA play-by-play, 1996-397 to 2024-25.


## The scale

AS the trailing team, the deficit severity is measured by how many points per minute the team would have to gain on the opponent to tie the game at the buzzer.

```
required comeback rate = deficit / minutes remaining      (points per minute)
```

Down 20 with 5 minutes left means the losing team needs to gain 4 points every minute. This can be achieved by either outscoring the opposing team 6 to 2, or 4 to 0.

An NBA team scores about 2.4 points per minute, so a rate of 2.4 means the losing team would need to gain a whole team's worth of scoring every minute, on top of whatever the opponent scores.

By looking at the final score of every trailing team that never pulled its starters and finding the worst position it faced, we can see the proportion that came back and won:

| Peak rate faced | Team-games | Came back and won |
| --- | ---: | ---: |
| 0 to 0.5 | 10,862 | 81.5% |
| 0.5 to 1 | 5,496 | 66.6% |
| 1 to 1.5 | 2,254 | 50.5% |
| 1.5 to 2 | 1,161 | 36.6% |
| 2 to 2.5 | 834 | 26.6% |
| 2.5 to 3 | 583 | 16.0% |
| 3 to 4 | 1,005 | 7.5% |
| 4 to 5 | 1,091 | 4.6% |
| 5 to 7 | 3,815 | 0.8% |
| 7 and above | 13,855 | 0.0% |

A required comeback rate of 1 to 1.5 is a coin flip, whereas when the required comback rate exceeds 5, the comeback becomes substantially rarer.


## Do coaches differ in their tendency to surrender?

Across 139 coaches with at least 60 trailing games, covering 42,278 team-games, at least one team surrenders in 11.1% of them.

The initial idea was to test and compare each coach against that 11.1%. But coaches worked in different decades and with different rosters, and both of those affect how often a team ends up conceding. Brian Keefe coaching the 17 win Wizards in 2025-26 is going to concede more than Steve Kerr coaching the 73 win Warriors in 2016-17, simply just because Keefe would be in more situations where surrender would be considered, even if the two coach's actually have the same tendency. 

So the fairer measure is to see whether a coach's surrender decisions **would** differ from other coaches in the exact same situation. Where they were facing the same required comeback rate, coaching a team of the same quality in the same era, and see if one coach would pull his starters while the other kept playing.


### Building the data

#### 1. Work out the Required Comeback Rate at every moment

Play-by-play data records every event in a game: made shots, rebounds, fouls, turnovers, timeouts, substitutions. A typical NBA game logs 400 to 500 of them, so about 200 per team.
At every event where the team is trailing, we calculate the Required Comeback Rate.

#### 2. Reducing data log into one figure per game

Every trailing team-game is given two data points: a required rate and a flag for whether the coach conceded.

If he conceded, the row is marked 1 and the rate is the required comeback rate at the moment his starters came off. If he didn't, the rate is the highest the team faced while they were still on the floor. 


#### 3. Sorting each game Required Comeback Rate  into bands 

We sort each game's final required comeback rate statistic into a band to be able to compare with other coaches that surrendered at the same band, or allowed that band to occur without surrendering. 

Then, every band below the decided band gets filled with 0, as a team that reached 4.2 passed through 1.5, and 2.8, and 3.6 on the way. The team was in those spots and the coach didn't pull anyone, so marking the rows with 0 allows the data to reflect a coach that did not act when faced with that required comeback rate.

That gives 42,278 team-games expanded into 261,696 band-observations, of which 4,681 are a concession, for a baseline of 1.79% per band.


| Rate range | Teams at risk | Conceded | Hazard |
| --- | ---: | ---: | ---: |
| 0 to 0.5 | 42,278 | 7 | 0.0% |
| 0.5 to 1 | 32,256 | 27 | 0.1% |
| 1 to 1.5 | 27,167 | 109 | 0.4% |
| 1.5 to 2 | 24,991 | 244 | 1.0% |
| 2 to 2.5 | 23,674 | 271 | 1.1% |
| 2.5 to 3 | 22,636 | 304 | 1.3% |
| 3 to 4 | 21,792 | 630 | 2.9% |
| 4 to 5 | 20,242 | 669 | 3.3% |
| 5 to 7 | 18,579 | 1,069 | 5.8% |
| 7 to 10 | 14,018 | 852 | 6.1% |
| 10 to 15 | 9,047 | 424 | 4.7% |
| 15 to 25 | 4,168 | 72 | 1.7% |
| 25 and above | 848 | 3 | 0.4% |

Every team passes through the first rung, but only 848 ever climb past 25, because most games end long before it gets that bad. The chance of conceding peaks between 5 and 10 and then falls, which is selection rather than a change in behaviour. The teams still on the ladder at a rate of 15 belong to coaches who were never going to concede in the first place.

Each row of that table is a matched comparison set. Coaches are only ever compared against each other within the same rung.

### The model

Fit a logistic regression on those 261,696 rows, predicting whether a concession happened:

```
logit P(concede at this rung) = intercept + rung dummies + season dummies + b x team SRS
```

The rung dummies give every level of hopelessness its own baseline, which is what holds the situation constant. The season dummies absorb the fact that conceding became much more common over 29 seasons. The SRS term handles roster quality. Deliberately, there is no coach variable, so the model predicts as well as it can while blind to who was in charge.

Then fit the same model again with coach effects added, and see whether knowing the coach improves it.

```
without coach effects:  log-likelihood -20,374.4
with coach effects:     log-likelihood -20,073.2
```

Adding coaches improved the fit by 301 points. The problem is that adding 138 parameters always improves fit, even if coaches are irrelevant, because noise is partly fittable. So the improvement has to be measured against what chance alone would buy:

```
LR chi-square = 2 x 301.2 = 602 on 138 degrees of freedom,  p = 2.9 x 10^-59
```

If coaches added nothing, each useless parameter would buy about 1 point on average and the statistic would land near 138. It lands at 602, so roughly 464 points of it is genuine signal.

### The answer

Yes. Held at the same required comeback rate, in the same era, with the same roster quality, coach identity still predicts the decision overwhelmingly.

Hazard ratios span 0.20 to 3.18, a 15.7 fold range:

| Quickest | HR | Slowest | HR |
| --- | ---: | --- | ---: |
| Chuck Daly | 3.18 | Jim Boylan | 0.20 |
| Leonard Hamilton | 2.43 | Mike Dunlap | 0.23 |
| Brian Keefe | 2.42 | Don Casey | 0.29 |
| Stephen Silas | 2.12 | George Karl | 0.34 |
| Paul Silas | 2.11 | M.L. Carr | 0.34 |
| Wes Unseld | 2.04 | Bill Hanzlik | 0.34 |

Against the 1.79% baseline, a hazard ratio of 3.18 works out to a 5.7% chance of acting at any given rung, and 0.34 works out to 0.6%.

So put Chuck Daly and George Karl in the identical spot, both needing 4 points per minute to come back, coaching a league average roster in the same season, and Daly is roughly nine times more likely to have his starters off.

One caution on the extremes. Jim Boylan and Mike Dunlap sit on roughly 80 games each, so their numbers are loosely estimated. George Karl at 0.34 across 823 trailing games is the entry to trust, and it is worth noting he lands on the same figure from a sample ten times larger.

### What this does not tell you

The test is an omnibus one. It says coaches differ, but not which ones or by how much, and 602 would look the same whether all 139 differ slightly or six differ enormously.

Each coach also gets a single number applied at every rung, which assumes his effect is constant. A coach who is quick at a rate of 3 but stubborn at 10 would be averaged into the middle, and that is untested.

Finally, the required comeback rate is not a complete description of a situation. Down 12 with 3 minutes and down 20 with 5 both read 4.0, but the first needs fewer total points to erase. Neither accounts for the pace of the game, though the season dummies absorb some of that.
