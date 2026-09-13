# How hopeless does it have to get before a coach gives up?

Some coaches empty the bench the moment a game slips away. Others ride their starters through a forty point deficit. This is a measure of that difference, built from 29 seasons of NBA play-by-play, 1996-97 to 2024-25.


## The scale

AS the trailing team, the deficit severity is measured by how many points per minute the team would have to gain on the opponent to tie the game at the buzzer.

```
required comeback rate = deficit / minutes remaining      (points per minute)
```

Down 20 with 5 minutes left means the losing team needs to gain 4 points every minute. This can be achieved by either outscoring the opposing team 6 to 2, or 4 to 0.

An NBA team scores about 2.4 points per minute, so a rate of 2.4 means you need to gain a whole team's worth of scoring every minute, on top of whatever they score.

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

The initial idea would be to test and compare each coach against that 11.1%. But coaches worked in different decades and with different rosters, and both of those affect how often a team ends up conceding. Brian Keefe coaching the 17 win Wizards in 2025-26 is going to concede more than Steve Kerr coaching the 73 win Warriors in 2016-17, just because Keefe would be in more situations where surrender would be considered, even if the two men actually think about the decision identically. Comparing both to this single league average would measure that difference as coaching.

So the fairer measure is not whether a coach's surrender tendancy differs from the league. It is whether he differs from what his own circumstances predict.

### Building each coach's expectation

To get that, we fit a model that predicts the chance of conceding using only the season and the team's SRS:

Note: SRS Simple Rating System is the team strength measurement developed by Basketball Reference. It looks at margin of victory/loss adjusted for opponent strength. The highest SRS of a team was the 1970-71 Bucks with 11.92. 

```
logit P(concede) = intercept + season dummies + b x team SRS
```

The season dummies give every year its own baseline, which soaks up the fact that conceding became much more common over thirty seasons. The SRS term handles roster quality. Critically, the model has no coach variable in it at all. It is being asked to predict as well as it can while blind to who was in charge.

Every one of the 42,278 games then gets its own predicted probability. A game in 2025 on a bad roster might come out at 21%, and one in 2006 on a decent roster at 9%.

Add up those predictions for a single coach and you get the number of concessions his circumstances imply:

| Coach | Games | Conceded | Expected | Mean SRS | Mean year |
| --- | ---: | ---: | ---: | ---: | ---: |
| George Karl | 823 | 27 | 73.3 | +2.32 | 2006 |
| Mike D'Antoni | 727 | 33 | 70.1 | +1.26 | 2010 |
| Erik Spoelstra | 790 | 48 | 99.3 | +2.90 | 2016 |
| Gregg Popovich | 1,157 | 140 | 125.6 | +2.82 | 2012 |
| Rick Adelman | 759 | 111 | 66.7 | +1.90 | 2006 |
| Stephen Silas | 201 | 53 | 34.1 | −7.80 | 2022 |
| Brian Keefe | 93 | 31 | 19.2 | −11.31 | 2025 |

You can see the adjustment doing its job. Brian Keefe coached in 2025 on a roster eleven points below average, which is about the most concede-prone combination there is, so he is expected to concede 19 times rather than the 10 a flat league rate would have implied. George Karl worked earlier with better teams, so his expectation drops to 73.

### The test

Now compare each coach's actual count against his own expectation:

```
chi-square = 433 on 138 degrees of freedom,  p = 3.0 x 10^-32
```

The number to compare against is 138, which is what this statistic would land near if coaches added nothing beyond era and roster. It lands at 433 instead, so coaches clearly do carry information of their own.

But it is worth asking where that 433 comes from, because the answer changes how you read it. Six coaches account for 147 of it:

| Coach | Conceded | Expected | Contribution |
| --- | ---: | ---: | ---: |
| Rick Adelman | 111 | 66.7 | 29.4 |
| George Karl | 27 | 73.3 | 29.2 |
| Erik Spoelstra | 48 | 99.3 | 26.5 |
| Dwane Casey | 42 | 90.2 | 25.7 |
| Mike D'Antoni | 33 | 70.1 | 19.7 |
| Chuck Daly | 17 | 6.6 | 16.1 |

So this is not 139 coaches each being a little bit different. It is a handful of real outliers, with most coaches landing close to what their circumstances predict. Karl conceding 27 times where 73 was expected, and Spoelstra 48 where 99 was expected, are gaps that noise does not produce.

## How much of the difference is real

The chi-square tells you the differences exist. It says nothing about how big they are.

For that, split the observed variation in concede rates into three parts:

| Source | Variance | Share |
| --- | ---: | ---: |
| Era and roster | 0.00098 | 36% |
| Sampling noise | 0.00056 | 20% |
| The coach | 0.00123 | 44% |
| Total observed | 0.00277 | 100% |

Just over a third of the raw spread between coaches comes from era and roster. Another fifth is small samples. What is left over, 44%, is the coach.

Converting that back to a rate gives a genuine between-coach standard deviation of 3.5 percentage points, around a league mean of 11.1%. In plain terms, a coach one standard deviation above average concedes about 15% of the time, and one standard deviation below about 8%.

## Most willing to concede

These rankings use conceded divided by expected, so 1.66 means a coach conceded two thirds more often than his era and rosters imply. Restricted to coaches with 100 or more trailing games.

| Coach | Conceded | Expected | Obs / exp | Games | Mean SRS | Mean year |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rick Adelman | 111 | 66.7 | 1.66 | 759 | +1.9 | 2006 |
| Rudy Tomjanovich | 56 | 34.3 | 1.63 | 413 | −0.0 | 2001 |
| Paul Silas | 34 | 21.4 | 1.59 | 220 | −5.6 | 2008 |
| Stephen Silas | 53 | 34.1 | 1.55 | 201 | −7.8 | 2022 |
| Wes Unseld | 44 | 28.8 | 1.53 | 168 | −4.0 | 2023 |
| Lenny Wilkens | 54 | 35.7 | 1.51 | 424 | −0.9 | 2001 |
| Kurt Rambis | 23 | 15.2 | 1.51 | 165 | −6.2 | 2009 |
| Jim Boylen | 20 | 13.3 | 1.50 | 101 | −6.1 | 2020 |

## Least willing to concede

| Coach | Conceded | Expected | Obs / exp | Games | Mean SRS | Mean year |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| George Karl | 27 | 73.3 | 0.37 | 823 | +2.3 | 2006 |
| Larry Bird | 4 | 9.4 | 0.43 | 120 | +4.8 | 1999 |
| Dwane Casey | 42 | 90.2 | 0.47 | 704 | −1.8 | 2016 |
| Mike D'Antoni | 33 | 70.1 | 0.47 | 727 | +1.3 | 2010 |
| Erik Spoelstra | 48 | 99.3 | 0.48 | 790 | +1.7 | 2017 |
| Isiah Thomas | 13 | 26.9 | 0.48 | 287 | −2.0 | 2005 |
| Butch Carter | 5 | 10.3 | 0.49 | 119 | −2.4 | 1999 |
| Rick Pitino | 8 | 15.7 | 0.51 | 185 | −1.7 | 1999 |

George Karl is the most solid entry in either table. On 823 trailing games, the largest sample here, he conceded at just over a third of the rate his circumstances imply. Mike D'Antoni once sat through a position requiring 48.8 points per minute, which is roughly down 49 with a minute to play, and still did not pull his starters.

The adjustment changes who appears. Chauncey Billups and Taylor Jenkins were near the top on raw rates but drop out here, because most of what looked like willingness was really just coaching recent teams. Stephen Silas and Wes Unseld stay, because their rates are high even after allowing for weak modern rosters.

## Where the halfway point falls

A Kaplan-Meier curve tracks what share of a coach's trailing games are still unconceded as the required comeback rate climbs. Its median is the rate at which half his trailing games have ended in surrender.

Only 10 of 139 coaches ever reach a median. For the other 129 the curve never falls to half, because more than half their trailing games end with the starters still on the floor no matter how hopeless it got.

| Coach | KM median (pts/min) | % conceded | n |
| --- | ---: | ---: | ---: |
| Joe Mazzulla | 8.47 | 18% | 108 |
| Darvin Ham | 10.91 | 23% | 108 |
| Ime Udoka | 10.91 | 19% | 128 |
| Chris Finch | 13.33 | 18% | 226 |
| Brian Keefe | 13.43 | 33% | 93 |
| Wes Unseld | 13.85 | 26% | 168 |
| Taylor Jenkins | 14.16 | 23% | 293 |
| Mike Budenholzer | 14.79 | 19% | 444 |
| Tom Thibodeau | 20.00 | 11% | 562 |
| James Borrego | 26.90 | 15% | 238 |

That 129 of 139 never reach a median is the finding, not a hole in the data. Most NBA coaches essentially never concede while trailing, at any deficit, and the ones who do are exceptions.

These medians are raw rather than adjusted, so some of the pattern is era. Mazzulla, Ham, Udoka, Finch, Keefe, Unseld, Jenkins and Borrego are almost all currently active, which fits the idea that conceding while behind is a modern behaviour.

## Is it the coach or the roster?

The adjustment above already removes era and roster when comparing one coach to another. A different question is whether a coach's tendency is stable at all, or whether the same man behaves differently as his circumstances change.

Three tests look at that, each using a different kind of variation within a single coach.

### The same coach with a stronger or weaker roster

Take 76 coaches who lasted four or more seasons and had real variation in roster quality. Subtract each coach's own average, so all that remains is how he moved from year to year:

```
within-coach slope: -0.143 percentage points of concede rate per SRS point
                    SE 0.057, t = -2.49, n = 675 coach-seasons
```

The sign is the interesting part. Give the same coach a better roster and he concedes less often when trailing, by about 1.4 percentage points per ten SRS points. That makes sense. A good team that is behind has more reason to think it can come back, so the coach leaves his starters out there.

This might look like it contradicts the familiar idea that strong teams empty their benches more. It does not, because that idea is about all decided games including the ones being won. The two behaviours run in opposite directions. A strong team concedes less readily when behind and calls off wins more readily when ahead. Only the trailing half is measured here.

### The same coach at different franchises

Sixty coaches worked at two or more clubs with at least 60 trailing games at each. Pair each coach's rate at his main club against the weighted average of his others, then correlate across coaches:

```
r = +0.306, 95% CI [+0.084, +0.502], 3,000 bootstrap resamples over coaches
```

The interval excludes zero, so something personal does travel with the man. For comparison, the correlation of roster strength across the same coaches' clubs is +0.233, meaning a coach's tendency follows him slightly better than his luck with rosters does.

The effect is moderate though, and the individual cases show why:

| Coach | Weak roster | Strong roster | SRS gap |
| --- | --- | --- | ---: |
| Monty Williams | DET −9.1 → 11% | PHX +3.5 → 16% | 12.6 |
| Avery Johnson | NJN −6.3 → 14% | DAL +5.9 → 10% | 12.3 |
| Flip Saunders | WAS −6.0 → 11% | DET +5.3 → 12% | 11.3 |
| Larry Brown | NYK −6.3 → 10% | DET +4.2 → 3% | 10.5 |
| Larry Drew | CLE −9.4 → 3% | ATL +0.2 → 20% | 9.6 |
| George Karl | SAC −2.3 → 0% | SEA +6.6 → 5% | 8.9 |
| Paul Silas | CHA −10.3 → 18% | CLE −1.5 → 14% | 8.8 |
| Rick Adelman | GSW −4.9 → 24% | SAC +3.9 → 13% | 8.8 |

Flip Saunders is the cleanest case of a coach whose tendency is his own. He ran 11% on a −6.0 Washington roster and 12% on a +5.3 Detroit one, so an eleven point swing in team quality moved him by a single point.

Larry Drew is the opposite, at 3% with Cleveland and 20% with Atlanta. Larry Brown ran 10% in New York and 3% in Detroit. For these two the number is clearly not a fixed trait.

Across all 60 movers, the average absolute change between clubs is 4.5 percentage points, against a coach-attributable standard deviation of 3.5. So changing clubs typically moves a coach more than the entire league varies.

### The same coach at the same club over many years

This is the cleanest test available. Hold both the man and the franchise fixed, and let the roster change underneath him. Fifty-two coach-franchise spells have four or more seasons, 200 or more trailing games, and a real swing in roster quality.

| Coach | Team | Seasons | Games | SRS range | Concede range | Overall |
| --- | --- | ---: | ---: | --- | --- | ---: |
| Gregg Popovich | SAS | 26 | 1,134 | −9.8 to +10.3 | 11% to 27% | 12.0% |
| Erik Spoelstra | MIA | 16 | 790 | −2.9 to +7.0 | 10% to 11% | 6.1% |
| Jerry Sloan | UTA | 15 | 719 | −3.7 to +8.0 | 3% to 5% | 9.2% |
| Rick Carlisle | DAL | 12 | 615 | −2.7 to +4.9 | 8% to 11% | 14.3% |
| Phil Jackson | LAL | 11 | 497 | +0.2 to +8.4 | 5% to 9% | 7.4% |
| Pat Riley | MIA | 10 | 483 | −8.5 to +5.6 | 0% to 6% | 7.9% |
| Steve Kerr | GSW | 10 | 453 | −8.1 to +10.4 | 4% to 6% | 9.3% |
| Doc Rivers | BOS | 9 | 428 | −3.7 to +9.3 | 6% to 6% | 8.9% |
| Michael Malone | DEN | 9 | 418 | −2.8 to +5.2 | 2% to 16% | 15.3% |

Read the concede range against the SRS range beside it. Doc Rivers went 6% to 6% while Boston's roster swung thirteen points. Spoelstra ran 10% to 11% while Miami moved ten. Steve Kerr held 4% to 6% while Golden State swung eighteen and a half points, from the pre-Curry era to the 73 win team. These are coaches whose tendency is genuinely their own.

Michael Malone is the counterexample, running 2% to 16% at a single club. Popovich spans 11% to 27%, though over twenty-six seasons that is a career rather than a tendency.

Averaged across all 52 spells, the correlation between a season's roster strength and that season's concede rate is +0.116, which is close to nothing. Roster quality is not what moves a coach's number within a club.

### What the three tests say together

The tendency is partly personal and substantially circumstantial.

It travels between clubs at r = +0.306, which is real but moderate. Roster strength moves a coach only slightly, and in the opposite direction to what you might guess. And then there is the figure that settles it. The average season to season swing within one coach at one club is 14.0 percentage points, while the coach-attributable spread across the whole league is 3.5.

One man at one club varies far more between seasons than the league varies between men. So reading any single coach's number as a fixed personal trait is overreaching. What the data supports is that coaches differ on average, that a few like Rivers, Spoelstra, Kerr and Sloan are strikingly consistent, and that most are not.

## The most hopeless positions ever tolerated

| Season | Team | Down by | Min left | Rate needed |
| --- | --- | ---: | ---: | ---: |
| 2021-22 | OKC | 75 | 1.07 | 70.3 |
| 2023-24 | POR | 62 | 1.03 | 60.0 |
| 2023-24 | POR | 57 | 1.00 | 57.0 |
| 2022-23 | POR | 56 | 1.00 | 56.0 |
| 2020-21 | OKC | 57 | 1.07 | 53.4 |

Oklahoma City sat through being down 75 with a minute left, starters still on the floor. That is the Memphis 152-79 game, the largest margin of victory in NBA history.

## What statistics this uses

Very little, deliberately.

| Step | Method |
| --- | --- |
| Required comeback rate | division |
| Peak rate for non-conceders | a maximum |
| Share conceded | a proportion |
| Expected count per coach | logistic regression on season and SRS, no coach term |
| Do coaches differ | one chi-square test |
| How much spread is real | variance subtraction |
| Where the halfway point falls | Kaplan-Meier, non-parametric |

The only fitted model is the one that builds each coach's expectation, and it exists for one reason, which is to compare coaches against their own circumstances rather than against a league average. Everything else is arithmetic you could check by hand from the counts.

One design choice is worth flagging. Adjusting for how much opportunity a coach had usually needs a model, but here it is built into the definition instead. Recording the worst position a coach faced, rather than just how long he waited, puts a coach whose games never got hopeless on the same footing as one whose did. That works in practice: the correlation between how often a coach concedes and how severe his trailing games got is -0.058, which is essentially zero.

## Validation

Every conceded row was cross-checked against an independently built surrender-event file. On the 5,103 events present in both, the score margin and the clock reading match exactly, at 100% on each with a maximum difference of zero. The 378 reference events absent here are all explained by the two stated filters, being 49 below a 6 point deficit and 329 inside the final minute. None is unexplained, and there are no rows here that the reference lacks.

That audit also caught two real errors. Time is not monotonic in the feed's own event ordering, running backwards at some point in 90% of games. An early version used a binary search on the timestamp column, which assumes sorted input, so it returned the wrong row and corrupted 6% of margins by up to 17 points. The fix separates the two lookups. The score as of the surrender comes from the last row at or before it in the league's own event sequence, while the clock reading comes from the substitution's own timestamp rather than from a neighbouring event.

## Limitations

1. Intent is inferred rather than observed. The last permanent exit of five starters is consistent with conceding, but also with injury, ejection or foul trouble.

2. Censored values are floors rather than estimates. Saying D'Antoni held at 48.8 means he tolerated at least that much. It does not mean that is his threshold, because his games may simply never have got worse.

3. The adjustment covers era and roster, but not opponent quality or schedule. A coach who faced stronger opponents more often was in more hopeless positions for reasons that are not him, and that is still sitting inside the residual.

4. The era term is a set of season dummies, which absorbs everything that moved with time including the three point revolution, pace and rule changes, without separating them. It removes era as a confounder but treats it as a black box.

5. There is no uncertainty attached to any individual coach. The chi-square shows that coaches differ overall and the variance subtraction says by how much, but neither gives a range for one man. A rate built on 93 games should be read far more loosely than one built on 823.

6. The measure covers trailing teams only. Calling off a win is a different decision with different incentives, and is not included here.

7. 2025-26 is excluded, because that season uses an incompatible feed format requiring a separate parser.
