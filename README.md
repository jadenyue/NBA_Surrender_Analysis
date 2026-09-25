# How hopeless does it have to get before a coach gives up?

In the NBA, some coaches see surrendering as a strategic move to protect their players from injury when a game is hopeless, so they surrender as soon as a game seems out of reach. Other coaches would rather ride their starters through a 40 point deficit than give up. From observation, NBA coaches seem to differ in their tendency to surrender, so in this project I used statistical methods (discrete-time hazard model, likelihood ratio test variance decomposition) to test that hypothesis and to explore some other phenomena in an often overlooked aspect of basketball.

The action of "surrender" is defined here as the moment a coach withdraws all five of his starters and never brings any of them back.

Every game is looked at from both teams' points of view, and each of those is called a team-game. Only trailing team-games are used, meaning ones where the team was behind by at least 6 points with at least a minute left at some point. A team that was never in that position is filtered out, because a coach emptying his bench while being ahead is protecting a result rather than surrendering.

Most games therefore contribute one team-game, and games where both teams spent time well behind contribute two. 
That leaves **40,325 trailing team-games** for the total data.

## The scale

To analyse the differences in coaches' tendency to surrender, we need a common measurement that combines the score and the time left, because for a coach considering surrender, being down 15 with 2 minutes left is a  different situation from being down 15 with 10 minutes left.

That scale is the **required comeback rate (RCR)**. For the trailing team, the severity of a deficit is how many points per minute the team would have to gain on the opponent to tie the game at the buzzer.

```
required comeback rate (RCR) = deficit / minutes remaining      (points per minute)
```

So down 20 with 5 minutes left means the losing team needs to gain 4 points every minute. That can be achieved by outscoring the opponent 6 to 2, or 4 to 0.

We can look at the data to get a better understanding of RCR in context. For each trailing team, find the **peak RCR**, meaning the worst position it faced all game, and then check whether it went on to win.

This data only uses teams that never surrendered. A team that surrendered has effectively forfeited, so including them would drag the win rates down rather than show a true representation of how winnable a position was.

| Peak RCR faced | Team-games | Came back and won |
| --- | ---: | ---: |
| 0 to 0.5 | 9,431 | 81.6% |
| 0.5 to 1 | 4,835 | 66.6% |
| 1 to 1.5 | 2,006 | 51.1% |
| 1.5 to 2 | 1,028 | 37.7% |
| 2 to 2.5 | 718 | 26.9% |
| 2.5 to 3 | 515 | 15.1% |
| 3 to 4 | 889 | 8.1% |
| 4 to 5 | 950 | 5.1% |
| 5 to 7 | 3,291 | 0.7% |
| 7 and above | 12,040 | 0.0% |

An RCR of 1 to 1.5 is roughly 50/50, with those teams winning 51.1% of the time. Once the RCR exceeds 5 the comeback becomes very rare at 0.7%, and beyond 7 it has never happened once across 12,040 team-games.

So a coach who surrenders while facing a low RCR can be said to have a much higher tendency to surrender than one who only surrenders at a high RCR. 

The next step is building the data.

*The full 40,325 row dataset, with the RCR, deficit and minutes left for every trailing team-game, is in `comeback_rate_all.csv`.*

### Building the data

The model needs a coach attached to every game and a roster quality figure for every team, and it only includes coaches with at least 60 trailing team-games to have a large enough sample. That brings the 40,325 games down to 36,859 team-games across 123 coaches, and within those, the coach surrendered in 11.5%.

My initial idea was to use a simple chi-squared test to compare each coach against that 11.5%. But coaches worked in different decades and with different rosters, and both of those affect how often a team ends up surrendering. Brian Keefe coaching the 18 win Wizards in 2024-25 is going to surrender more than Steve Kerr coaching the 73 win Warriors in 2015-16, simply because Keefe finds himself in more situations where surrender is on the table, even if the two coaches have identical tendencies.

So the true measure is about whether a coach's decisions **would** differ from another coach's in the exact same situation. Same RCR, same era, same roster quality, and then see whether one pulls his starters while the other keeps playing.

#### 1. Work out the RCR at every event

Play-by-play data records every event in a game: made shots, rebounds, fouls, turnovers, timeouts, substitutions, the last figure being the most important for our analysis. At every event where the team is trailing, we calculate the RCR.

#### 2. Reduce each game to one figure

Those few hundred RCR values per game then get reduced to a single one figure and a flag for whether the coach surrendered.

If he surrendered, the RCR kept is the one at the moment his starters came off, since that is the state of the game when he made the decision. If he did not, the RCR kept is the highest the team faced while at least one his starters were still on the floor, which is the most hopeless position he sat through without acting.

#### 3. Sort each game's RCR into bands

The RCR scale is cut into 13 bands, running from 0-to-0.5 to 25-and-above at the top. They are narrow at the bottom and wide at the top, because almost nothing happens below an RCR of 1 and the decisions cluster between 3 and 10.

Each game's single RCR sorts into one band, so coaches can be compared against others who either surrendered in that band or reached it without surrendering.

Every band below that one then gets filled with a 0. For example, a team that reached an RCR of 4.2 passed through the 1-to-1.5 band, the 2-to-2.5 band and the 3-to-4 band on its way there. It was in those spots and the coach chose not to pull anyone, so marking those rows 0 lets the data reflect a coach who did not act when faced with that RCR.

So each of the 36,859 team-games becomes several rows, one per band it reached, for a total of 227,782 band-observations, of which 4,236 are a surrender. That gives a baseline surrender chance of 1.86% per band.

| RCR range | Team-games at risk | Surrendered | Hazard |
| --- | ---: | ---: | ---: |
| 0 to 0.5 | 36,859 | 6 | 0.0% |
| 0.5 to 1 | 28,187 | 26 | 0.1% |
| 1 to 1.5 | 23,726 | 102 | 0.4% |
| 1.5 to 2 | 21,787 | 230 | 1.1% |
| 2 to 2.5 | 20,608 | 249 | 1.2% |
| 2.5 to 3 | 19,700 | 269 | 1.4% |
| 3 to 4 | 18,958 | 567 | 3.0% |
| 4 to 5 | 17,583 | 595 | 3.4% |
| 5 to 7 | 16,124 | 966 | 6.0% |
| 7 to 10 | 12,158 | 781 | 6.4% |
| 10 to 15 | 7,793 | 379 | 4.9% |
| 15 to 25 | 3,565 | 63 | 1.8% |
| 25 and above | 734 | 3 | 0.4% |

Reading the columns: **team-games at risk** is how many reached that band, **surrendered** is how many of them surrendered at that point, and **hazard** is the second divided by the first, so the chance a coach pulls his starters at that level given he has not already.

Every team passes through the first band, but only 734 team-games ever exceed an RCR of 25.

The chance of surrendering peaks between 5 and 10 and then falls, which does not mean coaches become more stubborn at extreme deficits. It is selection. The teams still not surrendering when faced with an RCR of 15 are likely coached by someone who was never going to surrender no matter what, so only the most reluctant are left to be counted.

This important characteristic about this table is that the hazard ranges from 0.0% to 6.4% just based on a team's band. Each row is therefore a matched comparison set, and coaches are only ever compared against each other within the same band.

### The model

We first fit a logistic regression on those 227,782 rows, predicting whether a surrender happened:

```
logit P(surrender in this band) = intercept + band dummies + season dummies + b x team SRS
```

The band dummies give every level of hopelessness its own baseline, which is what holds the situation constant. The season dummies account for surrendering becoming more common over the 25 seasons, which is covered later. The SRS term measures roster quality, SRS being Basketball Reference's Simple Rating System, a team's average point margin adjusted for strength of schedule, centred on zero.

In this first model there is no coach variable, so the model is asked to predict as well as it can without knowing who was coaching.

Then fit the same model again with a coach variable added, and see whether knowing the coach helps it predict surrenders better. The measure of how well a model fits is its **log-likelihood**, which is how probable the observed data is under that model. It is always negative, and closer to zero is better.

```
without coach effects:  log-likelihood -18,282.3
with coach effects:     log-likelihood -18,023.0
```

Adding coaches improved the fit by 259 points, but that on its own is not informative. Adding parameters always improves fit. Here the coach variable adds 122 parameters, one for each of the 123 coaches minus one that acts as the reference point. So the improvement has to be measured against what 122 meaningless parameters would have bought, using a likelihood-ratio test:

```
LR chi-square = 2 x 259.3 = 519 on 122 degrees of freedom,  p = 2.5 x 10^-50
```

A parameter carrying no information buys about 1 point on average, so if coaches added nothing the statistic would land near 122. The statistic we got was 519.

### The answer
Yes. Held at the same RCR, in the same era, with the same roster quality, coaches have different tendencies on the decision of surrendering.

Looking at only coaches with 100 or more trailing team-games, hazard ratios vary from 0.27 to 2.09, so a 7.6x difference:

| Quickest | HR | Slowest | HR |
| --- | ---: | --- | ---: |
| Stephen Silas | 2.09 | George Karl | 0.27 |
| Paul Silas | 2.07 | Mike D'Antoni | 0.41 |
| Wes Unseld | 1.97 | Erik Spoelstra | 0.44 |
| Rudy Tomjanovich | 1.83 | Isiah Thomas | 0.45 |
| Terry Porter | 1.79 | Dwane Casey | 0.47 |
| Kurt Rambis | 1.76 | Doug Collins | 0.55 |

A hazard ratio is a multiplier on the baseline chance, so against the 1.86% baseline a ratio of 2.09 means a 3.9% chance of acting in any given band, and 0.27 means a 0.5% chance.

In theory then, if Stephen Silas and George Karl were in an identical spot, both needing 4 points per minute to come back, coaching a league average roster in the same season, Silas would be roughly eight times more likely to surrender.

So coaches do inherently differ in their surrender tendency independent of their team or era, by up to eight times.

Now looking at the data for the most known coaches of this era:

| Coach | HR | Rank | Games Sample Size | Comment |
| --- | ---: | ---: | ---: | --- |
| Joe Mazzulla | 1.47 | 18 | 108 | One of the most modern, analytical minded coaches is also one of the most proactive in surrendering. |
| Gregg Popovich | 1.16 | 44 | 996 | Slightly quicker than average on 996 games. Spurs resting everyone was mostly about resting players for entire games rather than surrendering faster. |
| Doc Rivers | 1.10 | 49 | 1,076 | Dead average, out of 106. |
| Tom Thibodeau | 0.71 | 91 | 562 | Stubborn, which matches exactly with his play starters 48 minutes no matter what reputation. |
| Steve Kerr | 0.65 | 94 | 453 | The dynasty Warriors teams were famous for emptying benches, but that was mostly in blowout wins and not in losses, which is what gets measured here. |
| Erik Spoelstra | 0.44 | 104 | 790 | Fourth most stubborn in the league. Indicative of the Miami Heat Culture as refusing to concede. |

*The hazard ratios and rankings for all 123 coaches are in `coach_hazard_ratios.csv`.*

With the initial question answered, I wanted to look at some other aspects of the same data.

### Is it the coach or the roster?
The model already removes era and roster when comparing one coach to another, but for a coach like Doc Rivers who moved across several franchises, I wanted to see whether his tendency changes with the team he is coaching.

To measure that, we need a number for comparison first. Seperating the variation in surrender rates between coaches into the part explained by era and roster, the part that is just small-sample noise, and the part left over, the true coach-to-coach variation is represented by the **standard deviation that works out to 3.3 percentage points** around the league average of 11.5%. So a coach one standard deviation above average surrenders in about 15% of his trailing games, and one below in about 8%.

Now, we look at only the 69 coaches who lasted four or more seasons and had a SRS standard deviation of at least 1.5, indicating they had real differences in roster quality. Subtracting each coach's own career average surrender rate, and his own average SRS, gives us only how he moved from year to year:

```
within-coach slope: -0.116 percentage points of surrender rate per SRS point
                    SE 0.064, t = -1.81, n = 584 coach-seasons
```

At t = -1.81, the test is statistically significant only at the 10% significance level, but it's still indicative of something interesting. The slope shows that the same coach with a better roster typically surrenders less than he does with a bad roster, by about 1.2 percentage points per ten SRS points. The reasoning would be that a good team that is behind has more reason to think it can come back, so the coach leaves his starters out there. 

Now we take the forty-nine coaches who coached two or more franchises with at least 60 trailing team-games at each. Pair each coach's surrender rate at his main franchise, meaning the one where he coached most, against the average of his other franchises weighted by how many games he had at each. Then correlate those pairs across all forty-nine coaches:

```
r = +0.290, 95% CI [+0.039, +0.507], 3,000 bootstrap resamples over coaches
```

The interval excludes zero, so something inherent does travel with the coach. But +0.290 is only moderate because some coaches stay very consistent across very different rosters, and others completely shift their willingness to surrender based on their players.

To see that, looking at the 20 coaches who had both a real change in roster quality between clubs, meaning at least 5 SRS points, and big enough sample size, meaning at least 250 trailing team-games. Then sort by how much their surrender rate moved.

In the tables below, each cell reads as team, then that team's SRS, then his surrender rate there. So "NYK -4.8 -> 5%" means he surrendered in 5% of his trailing games with a New York roster rated 4.8 points below average.

**The most stable coaches**

| Coach | Weak roster | Strong roster | SRS gap | Rate change |
| --- | --- | --- | ---: | ---: |
| Isiah Thomas | NYK -4.8 -> 5% | IND +0.5 -> 5% | 5.3 | 0.0 pt |
| Rick Adelman | MIN -0.5 -> 15% | SAC +4.6 -> 14% | 5.1 | 1.4 pt |
| Don Nelson | GSW -1.5 -> 8% | DAL +5.4 -> 5% | 6.9 | 2.4 pt |
| Quin Snyder | ATL -1.9 -> 8% | UTA +3.8 -> 11% | 5.7 | 2.5 pt |
| Mike Budenholzer | ATL -0.4 -> 19% | MIL +5.6 -> 16% | 6.0 | 2.6 pt |
| Dwane Casey | DET -5.2 -> 7% | TOR +1.8 -> 4% | 7.0 | 2.9 pt |
| George Karl | SAC -2.3 -> 0% | DEN +3.3 -> 3% | 5.6 | 3.7 pt |
| Flip Saunders | WAS -6.0 -> 11% | DET +5.3 -> 12% | 11.3 | 3.8 pt |

**Coaches whose tendency changed dramatically depending on team**

| Coach | Weak roster | Strong roster | SRS gap | Rate change |
| --- | --- | --- | ---: | ---: |
| Larry Drew | CLE -9.4 -> 3% | ATL +0.2 -> 20% | 9.6 | 17.1 pt |
| Jacque Vaughn | ORL -6.3 -> 14% | BKN -1.1 -> 24% | 5.2 | 10.4 pt |
| Lionel Hollins | BKN -4.7 -> 22% | MEM +1.7 -> 12% | 6.4 | 9.4 pt |
| Nick Nurse | PHI -2.6 -> 21% | TOR +2.6 -> 12% | 5.3 | 9.3 pt |
| Stan Van Gundy | DET -0.5 -> 13% | ORL +4.9 -> 5% | 5.3 | 9.2 pt |
| Dave Joerger | SAC -3.9 -> 19% | MEM +1.2 -> 11% | 5.1 | 8.7 pt |
| Mike D'Antoni | LAL -2.6 -> 5% | HOU +5.2 -> 11% | 7.9 | 8.2 pt |
| Larry Brown | NYK -6.3 -> 10% | DET +4.2 -> 3% | 10.5 | 7.5 pt |

Isiah Thomas is the clearest case of a coach whose tendency is intrinsic. He coached New York at -4.8 SRS and Indiana at +0.5, so a five point difference in roster quality, and his surrender rate did not move at all despite that. Rick Adelman is nearly as consistent, moving 1.4 points across a similar swing, and Flip Saunders held to within 3.8 points across an eleven point change in roster quality.

Larry Drew is the opposite being one of the most fluctuating, at 3% with Cleveland and 20% with Atlanta. For him his surrender tendency is  not a fixed trait, but instead a reaction to whatever situation he walked into.

The median rate change across all 20 is 5.3 percentage points, which is larger than the 3.3 point standard deviation between coaches. So the typical coach who changes teams moves more than the whole league varies, and only the top of the first table looks like a tendency that really belongs to the man.

As for Doc Rivers, who was the name I was originally curious about, he is absent from both tables (just like he is absent from in-game adjustments). All four of the teams he coached were at or above league average, giving him an SRS gap of only 3.6, which is below the threshold for either table. Within that narrow range his rate still moved 7.3 points, from 8.9% with a +1.6 SRS Boston team to 16.2% with a +3.9 SRS Philadelphia team.

*The per-franchise and per-season breakdowns behind these tables are in `coach_team.csv` and `coach_team_season.csv`.*

### How surrendering has increased over time

I mentioned that I noticed surrendering has increased over time when building the model to measure coach tendency, and it is something worth diving deeper into.

Across the first five seasons, 2000-01 to 2004-05, coaches surrendered in **8.1%** of trailing team-games. Across the last five, 2020-21 to 2024-25, the surrender rate became **16.9%**. The surrender rate has doubled, and correlating each season's rate against the year gives **+0.909**.

| Season | Trailing games | Surrendered | Rate | Median RCR when surrendering |
| --- | ---: | ---: | ---: | ---: |
| 2000-01 | 1,585 | 128 | 8.1% | 4.61 |
| 2001-02 | 1,580 | 139 | 8.8% | 4.60 |
| 2002-03 | 1,594 | 140 | 8.8% | 4.80 |
| 2003-04 | 1,620 | 116 | 7.2% | 5.22 |
| 2004-05 | 1,677 | 129 | 7.7% | 5.60 |
| ... | ... | ... | ... | ... |
| 2020-21 | 1,423 | 221 | 15.5% | 5.49 |
| 2021-22 | 1,633 | 264 | 16.2% | 5.13 |
| 2022-23 | 1,680 | 252 | 15.0% | 5.32 |
| 2023-24 | 1,622 | 304 | 18.7% | 5.29 |
| 2024-25 | 1,595 | 300 | 18.8% | 5.54 |

The last column shows that **the median RCR at which coaches surrender has actually increased**, going from 4.97 across the first five seasons to 5.36 across the last five, a correlation with the year of +0.502.

A higher RCR threshold means coaches are waiting until games are *more* hopeless before acting. So coaches have not lowered their standards at all, and if anything have become marginally more stubborn. The rate still doubled. What changed is how often games reach that state, meaning more games are becoming blowouts that require a coach to consider surrendering.

The rise also correlates with particular league trends. From 2000-01 to 2012-13 the rate averaged 9.0%, and although it drifted slightly upward it did so weakly and unevenly, at a correlation of +0.624. From 2013-14 onwards it averaged 14.2% and climbed steadily at +0.885. The timing lines up with the three point era. A league taking far more threes at a faster pace produces a wider spread of outcomes, with the good teams being able to get ahead on the bad teams much more quickly. 

If coaches were getting softer, the RCR threshold would have fallen. It rose. So this is a measurement of games becoming less competitive rather than coaches becoming more willing to quit.

*The full season by season series is in `comeback_rate_all.csv`, grouped by the season column.*

## Conclusion

So coaches do inherently differ in how readily they surrender. Faced with the same RCR, in the same era, with a roster of the same quality, the quickest coach is roughly eight times more likely to pull his starters than the slowest. Stephen Silas acts at 3.9% of moments where George Karl acts at 0.5%.

That tendency travels with the coach across different franchises at r = +0.290, and coaches like Isiah Thomas and Rick Adelman barely move at all even when their roster changes immensely by five SRS points. Other coaches have their tendencies swing by 8 to 17 percentage points depending on their players and roster, and the median coach who changes clubs moves more than the 3.3 point spread between coaches league-wide. So a coach's number is a general tendency rather than a fixed trait.

The behaviour is also becoming much more common, with the surrender rate doubling over 25 seasons from 8.1% to 16.9%, but coaches are not giving up any earlier than they used to, there are just far more games reaching the point where giving up makes sense.

## Limitations

**Intent is only inferred.** No coach announces that he is giving up. The last permanent exit of five starters is indicative of surrender, but could also be due to injury, ejection, foul trouble, or minute management unrelated to the score.

**The era control is a set of season dummies**, which absorbs everything that moved with time, including the three point revolution, pace and rule changes, without separating them. It removes era as a confounder but treats it as a black box.

**Each coach gets one hazard ratio applied at every band**, which assumes his effect is constant across all levels of hopelessness. A coach who is quick at an RCR of 3 but stubborn at 10 would be averaged into the middle.

**SRS is not a clean control.** It is built from point margin, and point margin is affected by surrendering itself, so the control variable and the outcome are not fully independent. It is also a season-level figure, meaning it describes the roster a coach had rather than the team he actually had available for a particular game. And it captures quality but not team depth.

**Play-by-play substitution data is less complete in earlier seasons.** Team-games with fewer than 15 recorded substitutions were excluded, which affects 2000-01 more than 2024-25, with pass rates of 76.7% and 98.0% respectively and median substitutions logged rising from 18 to 24. Since missing substitutions make a surrender undetectable, this could falsify the stated historical trend of surrendering becoming more common. However, dropping the thinnest logs actually shows a stronger trend. The correlation between surrenders and year is +0.909 unrestricted, +0.909 among games with 18 or more substitutions, +0.911 at 20 or more, and +0.909 at 22 or more.

**A number of thresholds were chosen to be reasonable but still arbitrarily:** a deficit of at least 6 points and a minute remaining to count as trailing, 60 trailing games to enter the model and 100 to appear in the ranking, and for the roster tests 4 seasons, an SRS spread above 1.5, an SRS gap of 5 between clubs and 250 games. I tested if changing the 100 game floor would alter rankings, and the results came back negative. The rest are stated where used but their sensitivity is untested.

**2025-26 is excluded**, because that season uses an incompatible feed format requiring a separate parser.

## Data sources

Play-by-play comes from the NBA's own stats API, the playbyplayv2 endpoint at stats.nba.com, accessed through a GitHub mirror. Every event in every game: shots, rebounds, fouls, turnovers, timeouts, substitutions.

Team strength (SRS) and coach records come from Basketball Reference. The coach records give games coached per team-season, which is what lets mid-season sackings be split correctly.

Since the play-by-play came through a mirror rather than direct from the league, I checked nothing had been lost. Season minute totals rebuilt from the substitution events matched officially published minutes at a correlation of 1.0000 across eleven teams in four eras, with the largest discrepancy 0.15%.

I also conducted a series of random checks against the NBA's official scorer's report, to verify minutes data and confirm surrender flags. All checks passed. 
