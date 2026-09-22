# How hopeless does it have to get before a coach gives up?

Some coaches see surrendering as a strategic move to protect their players from injury when a game is hopeless, so they surrender as soon as a game seems out of reach. Others would rather ride their starters through a 40 point deficit than give up. From observation, NBA coaches seem to differ in their tendency to surrender, so in this project I used statistical methods to test that hypothesis and to explore some other phenomena in an often overlooked aspect of basketball.

To "surrender" is defined here as the moment a coach withdraws all five of his starters and never brings any of them back.

The analysis covers 29 seasons of play-by-play data, 1996-97 to 2024-25, across 139 coaches with at least 60 trailing team-games each.

## The scale

To measure differences in a coach's tendency to surrender, we need a common measurement that combines the score and the time left, because being down 15 with 2 minutes left is a completely different situation from being down 15 with 10 minutes left.

That scale is the **required comeback rate (RCR)**. For the trailing team, the severity of a deficit is how many points per minute the team would have to gain on the opponent to tie the game at the buzzer.

```
required comeback rate (RCR) = deficit / minutes remaining      (points per minute)
```

Down 20 with 5 minutes left means the losing team needs to gain 4 points every minute. That can be achieved by outscoring the opponent 6 to 2, or 4 to 0. It is a net rate, so what matters is the gap closing rather than how many points either side scores.

An NBA team scores about 2.4 points per minute, so an RCR of 2.4 means the losing team would need to gain a whole team's worth of scoring every minute, on top of whatever the opponent scores.

Rather than guess at what each level means, we can look at what actually happened. Taking every trailing team that never pulled its starters, finding the worst position it faced, and checking the final score:

| Peak RCR faced | Team-games | Came back and won |
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

An RCR of 1 to 1.5 is roughly a coin flip, with those teams winning 50.5% of the time. Once the RCR exceeds 5 the comeback becomes very rare at 0.8%, and beyond 7 it has never happened once across 13,855 team-games.

So a coach who surrenders while facing a low RCR can be said to have a much higher tendency to surrender than one who only surrenders at a high RCR. That gives us the scale. The next step is building the data.

*The full 46,059 row dataset, with the RCR, deficit and minutes left for every trailing team-game, is in `comeback_rate_all.csv`.*

### Building the data

Across 139 coaches covering 42,278 trailing team-games, the coach surrendered in 11.1% of them.

My initial idea was to compare each coach against that 11.1%. But coaches worked in different decades and with different rosters, and both of those affect how often a team ends up conceding. Brian Keefe coaching the 18 win Wizards in 2024-25 is going to concede more than Steve Kerr coaching the 73 win Warriors in 2015-16, simply because Keefe finds himself in more situations where surrender is on the table, even if the two coaches have identical tendencies.

So the fairer measure is whether a coach's decisions **would** differ from another coach's in the exact same situation. Same RCR, same era, same roster quality, and then see whether one pulls his starters while the other keeps playing.

#### 1. Work out the RCR at every event

Play-by-play data records every event in a game: made shots, rebounds, fouls, turnovers, timeouts, substitutions. A typical NBA game logs 400 to 500 of them, so about 200 per team. At every event where the team is trailing, we calculate the RCR.

Only moments with a deficit of at least 6 points and at least a minute remaining are considered. Below 6 points is not a hopeless position, and inside the final minute the RCR explodes, since being down 6 with 2 seconds left reads 180 points per minute.

#### 2. Reduce each game to one figure

Every trailing team-game is reduced to two data points: an RCR and a flag for whether the coach surrendered.

If he surrendered, the RCR is the one at the moment his starters came off. If he did not, the RCR is the highest the team faced while they were still on the floor, which is the most hopeless position he sat through without acting.

#### 3. Sort each game's RCR into bands

Each game's RCR is sorted into a band, so that coaches can be compared against others who either surrendered in that band or allowed that band to occur without surrendering.

Every band below the sorted band is then filled with a 0, because a team that reached an RCR of 4.2 passed through 1.2, and 2.9, and 3.7 on the way. The team was in those spots and the coach chose not to pull anyone, so marking those rows 0 lets the data reflect a coach who did not act when faced with that RCR.

This is why the count expands. Each of the 42,278 team-games becomes several rows, one per band it reached, for a total of 261,696 band-observations, of which 4,681 are a surrender. That gives a baseline surrender chance of 1.79% per band.

| RCR range | Teams at risk | Surrendered | Hazard |
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

Reading the columns: **teams at risk** is how many team-games reached that band, **surrendered** is how many of them ended there, and **hazard** is the second divided by the first, so the chance a coach pulls his starters at that level given he has not already.

Every team passes through the first band, but only 848 ever exceed an RCR of 25, mostly because games finish long before it gets that bad. The chance of surrendering peaks between 5 and 10 and then falls, which does not mean coaches become more stubborn at extreme deficits. It is selection. The teams still holding out at an RCR of 15 belong to coaches who were probably never going to surrender no matter what, so only the most reluctant are left to be counted.

The important thing about this table is that the hazard runs from 0.0% to 6.1%, meaning a team's band changes the chance of a surrender more than a hundredfold. Each row is therefore a matched comparison set, and coaches are only ever compared against each other within the same band.

### The model

Fit a logistic regression on those 261,696 rows, predicting whether a surrender happened:

```
logit P(surrender in this band) = intercept + band dummies + season dummies + b x team SRS
```

The band dummies give every level of hopelessness its own baseline, which is what holds the situation constant. The season dummies account for surrendering becoming more common over the 29 seasons (More on that later). The SRS term handles roster quality, SRS being Basketball Reference's Simple Rating System, which is a team's average point margin adjusted for strength of schedule, centred on zero.

In this first model there is no coach variable at all, so it predicts as well as it can without knowing who was in charge.

Then fit the same model again with a coach variable added, and see whether knowing the coach helps it predict surrenders better.

```
without coach effects:  log-likelihood -20,374.4
with coach effects:     log-likelihood -20,073.2
```

Adding coaches improved the fit by 301 points, but that on its own proves nothing. Adding 138 parameters improves fit regardless of what they contain, because part of any dataset is noise and noise is partly fittable. The improvement has to be measured against what 138 meaningless parameters would have bought:

```
LR chi-square = 2 x 301.2 = 602 on 138 degrees of freedom,  p = 2.9 x 10^-59
```

A parameter carrying no information buys about 1 point on average, so if coaches added nothing the statistic would land near 138. It lands at 602.

### The answer

Yes. Held at the same RCR, in the same era, with the same roster quality, coach identity still predicts the decision to surrender.

Looking at only coaches with 100 or more trailing team-games, hazard ratios vary from 0.34 to 2.12, a 6.3 fold range:

| Quickest | HR | Slowest | HR |
| --- | ---: | --- | ---: |
| Stephen Silas | 2.12 | George Karl | 0.34 |
| Paul Silas | 2.11 | Butch Carter | 0.43 |
| Wes Unseld | 2.04 | Mike D'Antoni | 0.44 |
| Rudy Tomjanovich | 1.99 | Rick Pitino | 0.44 |
| Terry Porter | 1.85 | Isiah Thomas | 0.46 |
| Jim Boylen | 1.79 | Erik Spoelstra | 0.47 |

A hazard ratio is a multiplier on the baseline chance, so against the 1.79% baseline a ratio of 2.12 means a 3.8% chance of acting at any given RCR, and 0.34 means a 0.6% chance.

In theory then, if Stephen Silas and George Karl were in an identical spot, both needing 4 points per minute to come back, coaching a league average roster in the same season, Silas is roughly six times more likely to have surrendered.

The 100 game floor matters here. Without it the range widens to 15.7 fold, but every coach at either extreme has fewer than 95 trailing team-games, which is too few to trust. George Karl at 0.34 across 823 games is the most solid entry in the table.

So coaches do inherently differ in their surrender tendency independent of their team or era, by up to six times. With the initial question answered, I wanted to look at some other aspects of the same data.

*The hazard ratios for all 139 coaches are in `coach_hazard_ratios.csv`.*

### Is it the coach or the roster?

The model already removes era and roster when comparing one coach to another, but for a coach like Doc Rivers who moved across several franchises, it is worth seeing whether his tendency changes with the team he is coaching.

Start with 76 coaches who lasted four or more seasons and had real variation in roster quality. Subtracting each coach's own average leaves only how he moved from year to year:

```
within-coach slope: -0.143 percentage points of surrender rate per SRS point
                    SE 0.057, t = -2.49, n = 675 coach-seasons
```

The sign is the interesting part. The same coach with a better roster surrenders less than he does with a bad one, by about 1.4 percentage points per ten SRS points. The reasoning would be that a good team that is behind has more reason to think it can come back, so the coach leaves his starters out there.

Now take the sixty coaches who coached two or more franchises with at least 60 trailing team-games at each. Pair each coach's rate at his main franchise against the weighted average of his others, then correlate across coaches:

```
r = +0.306, 95% CI [+0.084, +0.502], 3,000 bootstrap resamples over coaches
```

The interval excludes zero, so something inherent does travel with the coach. For comparison, the correlation of roster strength across the same coaches' clubs is +0.233, meaning a coach's tendency follows him slightly better than his luck with rosters does.

But +0.306 is only moderate, and the individual cases show why. Some coaches stay remarkably consistent across very different rosters, and others do not.

To see that, take the 22 coaches who had both a real change in roster quality between clubs, meaning at least 5 SRS points, and enough games for the rates to mean something, meaning at least 250 trailing team-games. Then sort by how much their surrender rate moved.

**The most stable coaches**

| Coach | Weak roster | Strong roster | SRS gap | Rate change |
| --- | --- | --- | ---: | ---: |
| Isiah Thomas | NYK -4.8 -> 5% | IND +0.5 -> 5% | 5.3 | 0.0 pt |
| Doug Collins | WAS -1.5 -> 6% | DET +3.7 -> 7% | 5.3 | 0.9 pt |
| Quin Snyder | ATL -1.9 -> 8% | UTA +3.8 -> 11% | 5.7 | 2.5 pt |
| Mike Budenholzer | ATL -0.4 -> 19% | MIL +5.6 -> 16% | 6.0 | 2.6 pt |
| Dwane Casey | DET -5.2 -> 7% | TOR +1.8 -> 4% | 7.0 | 2.9 pt |
| Brian Hill | VAN -7.6 -> 8% | ORL -0.4 -> 5% | 7.2 | 2.9 pt |
| Mike Dunleavy | LAC -3.6 -> 7% | POR +4.1 -> 3% | 7.7 | 4.4 pt |
| Byron Scott | LAL -7.6 -> 12% | NJN +0.3 -> 11% | 7.9 | 4.7 pt |

**Coaches whose tendency changed dramatically depending on team**

| Coach | Weak roster | Strong roster | SRS gap | Rate change |
| --- | --- | --- | ---: | ---: |
| Larry Drew | CLE -9.4 -> 3% | ATL +0.2 -> 20% | 9.6 | 17.1 pt |
| Rick Adelman | GSW -4.9 -> 24% | SAC +3.9 -> 13% | 8.8 | 11.0 pt |
| Jacque Vaughn | ORL -6.3 -> 14% | BKN -1.1 -> 24% | 5.2 | 10.4 pt |
| Lionel Hollins | BKN -4.7 -> 22% | MEM +1.7 -> 12% | 6.4 | 9.4 pt |
| Nick Nurse | PHI -2.6 -> 21% | TOR +2.6 -> 12% | 5.3 | 9.3 pt |
| Stan Van Gundy | DET -0.5 -> 13% | ORL +4.9 -> 5% | 5.3 | 9.2 pt |
| Dave Joerger | SAC -3.9 -> 19% | MEM +1.2 -> 11% | 5.1 | 8.7 pt |
| Mike D'Antoni | LAL -2.6 -> 5% | HOU +5.2 -> 11% | 7.9 | 8.2 pt |

Isiah Thomas is the cleanest case of a coach whose tendency is his own. New York at -4.8 SRS and Indiana at +0.5, so a five point swing in roster quality, and his surrender rate did not move at all. Doug Collins is nearly as consistent, moving 0.9 points across the same size of swing.

Larry Drew is the opposite, at 3% with Cleveland and 20% with Atlanta. For him the number is clearly not a fixed trait, it is a reaction to whatever he walked into.

The median rate change across all 22 is 5.4 percentage points, which is larger than the genuine spread between coaches across the whole league. So the typical coach who changes clubs moves more than the league varies, and only the top of the first table looks like a tendency that really belongs to the man.

As for Doc Rivers, who was the name I was originally curious about, he is absent from both tables, just like he is absent from in-game adjustments. All four of the teams he coached were at or above league average, giving him an SRS gap of only 3.6, which is below the threshold for either table. He does look stable within that narrow range though, going from 9.9% with a +0.4 SRS Orlando team to 11.7% with a +4.0 SRS Clippers team, a change of under 2 percentage points.

*The per-franchise and per-season breakdowns behind these tables are in `coach_team.csv` and `coach_team_season.csv`.*

### How surrendering has increased over time

I mentioned that I noticed surrendering has increased over time when building the model to measure coach tendency, and it's something worth diving deeper into. 

Across the first five seasons, 1996-97 to 2000-01, coaches surrendered in **8.3%** of trailing team-games. Across the last five, 2020-21 to 2024-25, that figure is **16.9%**. The surrender rate has doubled, and it correlates with season at **+0.886**.

| Season | Trailing games | Surrendered | Rate | Median RCR when surrendering |
| --- | ---: | ---: | ---: | ---: |
| 1996-97 | 1,613 | 122 | 7.6% | 4.60 |
| 1997-98 | 1,569 | 135 | 8.6% | 5.51 |
| 1998-99 | 958 | 79 | 8.2% | 5.90 |
| 1999-00 | 1,594 | 145 | 9.1% | 5.11 |
| 2000-01 | 1,585 | 128 | 8.1% | 4.61 |
| ... | ... | ... | ... | ... |
| 2020-21 | 1,423 | 221 | 15.5% | 5.49 |
| 2021-22 | 1,633 | 264 | 16.2% | 5.13 |
| 2022-23 | 1,680 | 252 | 15.0% | 5.32 |
| 2023-24 | 1,622 | 304 | 18.7% | 5.29 |
| 2024-25 | 1,595 | 300 | 18.8% | 5.54 |

The last column shows that **The median RCR at which coaches surrender has not changed substatially**, going from 5.14 across the first five seasons to 5.36 across the last five, with a correlation to season of only +0.241.

So coaches have not lowered their threshold. They still wait until a comeback needs roughly 5.2 points per minute, which historically wins under 1% of the time. What has changed is how often games reach that state: more games are blowouts that require a coach to consider surrendering.

From 1996-97 to 2012-13 the rate averaged 8.7% and barely trended at all, with a correlation to season of +0.459. From 2013-14 onwards it averaged 14.0% and climbed steadily at +0.876. Something changed around 2013, and the timing lines up with the three point era rather than with any rule change or shift in coaching philosophy. A league taking far more threes at a faster pace produces a wider spread of outcomes, so leads that used to take a quarter to build now can be built in minutes.

If coaches were getting softer, the RCR threshold would have fallen. It did not. So this is a measurement of games becoming less competitive rather than coaches becoming more willing to quit.

*The full season by season series is in `comeback_rate_all.csv`, grouped by the season column.*

## Limitations

**Intent is inferred, not observed.** No coach announces that he is giving up. The last permanent exit of five starters is consistent with surrender, but also with injury, ejection, foul trouble, or minute management unrelated to the score. What the data establishes is that these games were effectively over, not what anyone was thinking.

**The RCR recorded for a surrender is not always the worst faced.** If a coach survives an RCR of 5, claws back to 4, then pulls his starters, the record says 4. It is necessary to measure it this way to make the analysis focused on the moment that coaches surrender.

**Values for non-surrenders are floors, not thresholds.** Saying Mike D'Antoni held at an RCR of 48.8 means he tolerated at least that much. It does not mean that is his limit, because his games may have ran out of time before it got worse.

**The era control is a set of season dummies**, which absorbs everything that moved with time, including the three point revolution, pace and rule changes, without separating them. It removes era as a confounder but treats it as a black box.

**Each coach gets one hazard ratio applied at every band**, which assumes his effect is constant across all levels of hopelessness. A coach who is quick at an RCR of 3 but stubborn at 10 would be averaged into the middle. That assumption is untested.

**Rows within a team-game are not independent**, since the same coach on the same night produces correlated observations. The point estimates are unaffected, but the confidence intervals are somewhat narrower than they should be.


** SRS is not a clean control. It is built from point margin, and point margin is affected by surrendering itself, so the control variable and the outcome are not fully independent. It is also a season-level figure, meaning it describes the roster a coach had rather than the team he actually had available on a given night. And it captures quality but not depth, which is arguably the thing that should drive this decision, since the whole question is whether the bench is good enough to finish the game.

**Play-by-play substitution data is less complete in older seasons.** Team-games with fewer than 15 recorded substitutions were excluded, which affects 1996-97 far more than 2024-25. Since missing substitutions suppress detection, this could bias the historical trend, though two separate checks suggest the trend survives.

**2025-26 is excluded**, because that season uses an incompatible feed format requiring a separate parser.
