# How hopeless does it have to get before a coach gives up?

In the NBA, some coaches see surrendering as a strategic move to protect their players from injury when a game is hopeless, so they surrender as soon as a game seems out of reach. Other coaches would rather ride their starters through a 40 point deficit than give up. From observation, NBA coaches seem to differ in their tendency to surrender, so in this project I used statistical methods (discrete-time hazard model, likelihood ratio test variance decomposition) to test that hypothesis and to explore some other phenomena in an often overlooked aspect of basketball.

The action of "surrender" is defined here as the moment a coach withdraws all five of his starters and never brings any of them back.

Every game is looked at from both teams' points of view, and each of those is called a team-game. Only trailing team-games are used, meaning ones where the team was behind by at least 6 points with at least a minute left at some point. A team that was never in that position is filtered out, because a coach emptying his bench while being ahead is protecting a result rather than surrendering.

Most games therefore contribute one team-game, and games where both teams spent time well behind contribute two. 
That leaves **42,439 trailing team-games** for the total data.

## The scale

To analyse the differences in coaches' tendency to surrender, we need a common measurement that combines the score and the time left, because for a coach considering surrender, being down 15 with 2 minutes left is a  different situation from being down 15 with 10 minutes left.

That scale is the **required comeback rate (RCR)**. For the trailing team, the severity of a deficit is how many points per minute the team would have to gain on the opponent to tie the game at the buzzer.

```
required comeback rate (RCR) = deficit / minutes remaining      (points per minute)
```

So down 20 with 5 minutes left means the losing team needs to gain 4 points every minute. That can be achieved by outscoring the opponent 6 to 2, or 4 to 0.

We can look at the data to get a better understanding of RCR in context. For each trailing team, find every **RCR** range it was in during the game, and then check whether it went on to win.

This data only uses teams that never surrendered. A team that surrendered has effectively forfeited, so including them would drag the win rates down rather than show a true representation of how winnable a position was.

| RCR faced | Team-games | Came back and won |
| --- | ---: | ---: |
| 0 to 0.5 | 35,237 | 39.6% |
| 0.5 to 1 | 24,604 | 20.7% |
| 1 to 1.5 | 19,866 | 10.3% |
| 1.5 to 2 | 17,983 | 5.9% |
| 2 to 2.5 | 16,815 | 3.7% |
| 2.5 to 3 | 15,885 | 2.3% |
| 3 to 4 | 16,533 | 1.7% |
| 4 to 5 | 15,508 | 1.1% |
| 5 to 7 | 15,520 | 0.6% |
| 7 and above | 12,366 | 0.1% |

An RCR of 1 to 1.5 is roughly 1 in 10, with those teams winning 10.3% of the time. Once the RCR exceeds 5 the comeback becomes very rare at 0.6%, and beyond 7 it has happened only 18 times across 12,366 team-games.

So a coach who surrenders while facing a low RCR can be said to have a much higher tendency to surrender than one who only surrenders at a high RCR. 

The next step is building the data.

*The full 42,439 row dataset, with the RCR, deficit and minutes left for every trailing team-game, is in `comeback_rate_all.csv`.*

### Building the data

The model needs a coach attached to every game, a roster quality figure for every team and a complete substitution log, and it only includes coaches with at least 60 trailing team-games to have a large enough sample. That brings the 42,439 games down to 36,966 team-games across 122 coaches, and within those, the coach surrendered in 10.9%.

My initial idea was to use a simple chi-squared test to compare each coach against that 10.9%. But coaches worked in different decades and with different rosters, and both of those affect how often a team ends up surrendering. Brian Keefe coaching the 18 win Wizards in 2024-25 is going to surrender more than Steve Kerr coaching the 73 win Warriors in 2015-16, simply because Keefe finds himself in more situations where surrender is on the table, even if the two coaches have identical tendencies.

So the true measure is about whether a coach's decisions **would** differ from another coach's in the exact same situation. Same RCR, same time left, same era, same roster quality, and then see whether one pulls his starters while the other keeps playing.

#### 1. Work out the RCR at every event

Play-by-play data records every event in a game: made shots, rebounds, fouls, turnovers, timeouts, substitutions, the last figure being the most important for our analysis. At every event where the team is trailing, we calculate the RCR.

#### 2. Reduce each game to one figure

Those few hundred RCR values per game then get reduced to a single one figure and a flag for whether the coach surrendered.

If he surrendered, the RCR kept is the one at the moment his starters came off, since that is the state of the game when he made the decision. If he did not, the RCR kept is the highest the team faced while at least one his starters were still on the floor, which is the most hopeless position he sat through without acting.

#### 3. Sort each game's RCR into bands

The RCR scale is cut into 13 bands, running from 0-to-0.5 to 25-and-above at the top. They are narrow at the bottom and wide at the top, because almost nothing happens below an RCR of 1 and the decisions cluster between 3 and 10.

Each game's single RCR sorts into one band (for a surrender, the highest band reached by the time the starters came off), so coaches can be compared against others who either surrendered in that band or reached it without surrendering.

Every band below that one then gets filled with a 0. For example, a team that reached an RCR of 4.2 passed through the 1-to-1.5 band, the 2-to-2.5 band and the 3-to-4 band on its way there. It was in those spots and the coach chose not to pull anyone, so marking those rows 0 lets the data reflect a coach who did not act when faced with that RCR.

Each of those rows also records how many minutes were left when the team got to that band, in six ranges, because the same RCR is a different situation for a coach with 2 minutes left than with 8.

So each of the 36,966 team-games becomes several rows, one per band it reached, for a total of 225,807 band-observations, of which 4,018 are a surrender. That gives a baseline surrender chance of 1.78% per band.

| RCR range | Team-games at risk | Surrendered | Hazard |
| --- | ---: | ---: | ---: |
| 0 to 0.5 | 36,966 | 1 | 0.0% |
| 0.5 to 1 | 27,581 | 11 | 0.0% |
| 1 to 1.5 | 23,561 | 53 | 0.2% |
| 1.5 to 2 | 21,743 | 151 | 0.7% |
| 2 to 2.5 | 20,555 | 186 | 0.9% |
| 2.5 to 3 | 19,612 | 220 | 1.1% |
| 3 to 4 | 18,856 | 499 | 2.6% |
| 4 to 5 | 17,450 | 647 | 3.7% |
| 5 to 7 | 15,886 | 983 | 6.2% |
| 7 to 10 | 11,926 | 815 | 6.8% |
| 10 to 15 | 7,585 | 389 | 5.1% |
| 15 to 25 | 3,406 | 60 | 1.8% |
| 25 and above | 680 | 3 | 0.4% |

Reading the columns: **team-games at risk** is how many reached that band, **surrendered** is how many of them surrendered at that point, and **hazard** is the second divided by the first, so the chance a coach pulls his starters at that level given he has not already.

Every team passes through the first band, but only 680 team-games ever exceed an RCR of 25.

The chance of surrendering peaks between 5 and 10 and then falls, which does not mean coaches become more stubborn at extreme deficits. It is selection. The teams still not surrendering when faced with an RCR of 15 are likely coached by someone who was never going to surrender no matter what, so only the most reluctant are left to be counted.

This important characteristic about this table is that the hazard ranges from 0.0% to 6.8% just based on a team's band. Each row, split by time left, is therefore a matched comparison set, and coaches are only ever compared against each other within the same band and time range.

### The model

We first fit a complementary log-log regression, the discrete-time form of a proportional hazards model, on those 225,807 rows, predicting whether a surrender happened:

```
cloglog P(surrender in this band) = intercept + band and time dummies + season dummies + b x team SRS
```

The band and time dummies give every level of hopelessness, at every stage of the game, its own baseline, which is what holds the situation constant. The season dummies account for surrendering becoming more common over the 25 seasons, which is covered later. The SRS term measures roster quality, SRS being Basketball Reference's Simple Rating System, a team's average point margin adjusted for strength of schedule, centred on zero.

In this first model there is no coach variable, so the model is asked to predict as well as it can without knowing who was coaching.

Then fit the same model again with a coach variable added, and see whether knowing the coach helps it predict surrenders better. The measure of how well a model fits is its **log-likelihood**, which is how probable the observed data is under that model. It is always negative, and closer to zero is better.

```
without coach effects:  log-likelihood -14,277.7
with coach effects:     log-likelihood -13,980.5
```

Adding coaches improved the fit by 297 points, but that on its own is not informative. Adding parameters always improves fit. Here the coach variable adds 121 parameters, one for each of the 122 coaches minus one that acts as the reference point. So the improvement has to be measured against what 121 meaningless parameters would have bought, using a likelihood-ratio test:

```
LR chi-square = 2 x 297.2 = 594 on 121 degrees of freedom,  p = 1.4 x 10^-63
```

A parameter carrying no information buys about 1 point on average, so if coaches added nothing the statistic would land near 121. The statistic we got was 594.

### The answer
Yes. Held at the same RCR and time left, in the same era, with the same roster quality, coaches have different tendencies on the decision of surrendering.

Looking at only coaches with 100 or more trailing team-games, hazard ratios vary from 0.35 to 1.88, so a 5.4x difference. Each is shown with its 95% interval, and each is shrunk toward the average by how noisy it is (empirical Bayes), since otherwise the most extreme of 101 noisy estimates would be exaggerated:

| Quickest | HR | 95% interval | Slowest | HR | 95% interval |
| --- | ---: | :---: | --- | ---: | :---: |
| Stephen Silas | 1.88 | 1.44 to 2.46 | George Karl | 0.35 | 0.24 to 0.51 |
| Brian Keefe | 1.88 | 1.35 to 2.60 | Erik Spoelstra | 0.49 | 0.37 to 0.63 |
| Wes Unseld Jr. | 1.83 | 1.37 to 2.44 | Mike D'Antoni | 0.49 | 0.36 to 0.67 |
| Kenny Atkinson | 1.71 | 1.30 to 2.25 | Dwane Casey | 0.51 | 0.38 to 0.68 |
| Jim Boylen | 1.64 | 1.12 to 2.41 | Steve Kerr | 0.55 | 0.41 to 0.73 |
| Tyrone Corbin | 1.58 | 1.17 to 2.14 | David Fizdale | 0.63 | 0.39 to 1.04 |

A hazard ratio is a multiplier on the baseline chance, so against the 1.78% baseline a ratio of 1.88 means a 3.3% chance of acting in any given band, and 0.35 means a 0.6% chance.

In theory then, if Stephen Silas and George Karl were in an identical spot, both needing 4 points per minute to come back with the same time left, coaching a league average roster in the same season, Silas would be roughly five times more likely to surrender.

So coaches do inherently differ in their surrender tendency independent of their team or era, by up to five times.

Now looking at the data for the most known coaches of this era:

| Coach | HR | 95% interval | Rank | Games Sample Size | Comment |
| --- | ---: | :---: | ---: | ---: | --- |
| Joe Mazzulla | 1.29 | 0.86 to 1.91 | 23 | 121 | One of the most modern, analytical minded coaches is also one of the more proactive in surrendering, though on 121 games the interval still includes average. |
| Gregg Popovich | 1.07 | 0.89 to 1.28 | 47 | 1,127 | Slightly quicker than average on 1,127 games. Spurs resting everyone was mostly about resting players for entire games rather than surrendering faster. |
| Doc Rivers | 1.08 | 0.90 to 1.29 | 44 | 1,190 | Dead average, out of 101. |
| Tom Thibodeau | 0.70 | 0.53 to 0.92 | 90 | 509 | Stubborn, which matches exactly with his play starters 48 minutes no matter what reputation. |
| Steve Kerr | 0.55 | 0.41 to 0.73 | 97 | 528 | The dynasty Warriors teams were famous for emptying benches, but that was mostly in blowout wins and not in losses, which is what gets measured here. |
| Erik Spoelstra | 0.49 | 0.37 to 0.63 | 100 | 859 | Second most stubborn in the league. Indicative of the Miami Heat Culture as refusing to concede. |

*The hazard ratios and rankings for all 122 coaches are in `coach_hazard_ratios.csv`.*

With the initial question answered, I wanted to look at some other aspects of the same data.

### Is it the coach or the roster?
The model already removes era and roster when comparing one coach to another, but for a coach like Doc Rivers who moved across several franchises, I wanted to see whether his tendency changes with the team he is coaching.

To measure that, we need a number for comparison first. Seperating the variation in the coaches' hazard ratios into the part that is just small-sample noise, 34% of it, and the part left over, the true coach-to-coach variation is represented by the **standard deviation that works out to 0.35** on the log scale. So a coach one standard deviation above average surrenders about 1.4 times as readily as the average coach, and one below about 0.7 times.

Now, we look at only the 70 coaches who lasted four or more seasons and had a SRS standard deviation of at least 1.5, indicating they had real differences in roster quality. Subtracting each coach's own career average surrender rate, and his own average SRS, gives us only how he moved from year to year:

```
within-coach slope: -0.179 percentage points of surrender rate per SRS point
                    SE 0.061, t = -2.93, n = 628 coach-seasons
```

The slope shows that the same coach with a better roster typically surrenders in fewer of his trailing games than he does with a bad roster, by about 1.8 percentage points per ten SRS points. But a raw rate also depends on how often a team ends up in hopeless positions, and a good team gets blown out far less. Because the model has an effect for every coach, its SRS term measures the same within-coach change at the same RCR and time left:

```
hazard ratio 1.093 per SRS point, 95% CI [1.083, 1.102]
```

So in the same situation the same coach surrenders more readily with a better roster, about 1.56 times as readily per five SRS points. 

Now we take the forty-six coaches who coached two or more franchises with at least 60 trailing team-games at each. Pair each coach's surrender ratio at his main franchise, meaning the one where he coached most, against the same ratio pooled over his other franchises. The surrender ratio is how many times he surrendered divided by how many times the model without coach effects expects from his situations, era and rosters. Then correlate those pairs across all forty-six coaches:

```
r = +0.306, 95% CI [+0.040, +0.543], 3,000 bootstrap resamples over coaches
```

The interval excludes zero, so something inherent does travel with the coach. But +0.306 is only moderate, and noise alone would hold even a perfectly consistent tendency to about +0.72 with samples this size, so only part of it travels, because some coaches stay very consistent across very different rosters, and others shift their willingness to surrender based on their players.

To see that, looking at the 20 coaches who had both a real change in roster quality between clubs, meaning at least 5 SRS points, and big enough sample size, meaning at least 250 trailing team-games. Then sort by how much their surrender ratio moved.

In the tables below, each cell reads as team, then that team's SRS, then his surrender ratio there. So "CLE -9.4 -> 0.22" means he surrendered 0.22 times as often as the model expects of an average coach in his spots, with a Cleveland roster rated 9.4 points below average. The change is the strong-roster ratio divided by the weak one, adding half a surrender at each club so that a club with none still gives a figure, and p tests whether the change is bigger than noise.

**The most stable coaches**

| Coach | Weak roster | Strong roster | SRS gap | Change | p |
| --- | --- | --- | ---: | ---: | ---: |
| Dwane Casey | DET -5.2 -> 0.41 | TOR +2.3 -> 0.41 | 7.5 | 1.02x | 1.000 |
| Scott Brooks | WAS -1.9 -> 1.24 | OKC +3.6 -> 1.15 | 5.4 | 0.94x | 0.883 |
| Lionel Hollins | BKN -4.6 -> 1.53 | MEM +0.9 -> 1.35 | 5.5 | 0.87x | 0.742 |
| Frank Vogel | ORL -5.8 -> 1.49 | IND +1.7 -> 1.19 | 7.5 | 0.79x | 0.411 |
| Jacque Vaughn | ORL -6.4 -> 1.14 | BKN -0.7 -> 1.48 | 5.7 | 1.30x | 0.491 |
| Larry Brown | NYK -6.3 -> 0.84 | DET +4.2 -> 0.55 | 10.5 | 0.70x | 0.740 |
| Nick Nurse | PHI -2.4 -> 1.23 | TOR +2.8 -> 0.83 | 5.1 | 0.67x | 0.158 |
| Don Nelson | GSW -1.4 -> 0.84 | DAL +5.5 -> 0.49 | 6.9 | 0.59x | 0.238 |

**Coaches whose tendency changed dramatically depending on team**

| Coach | Weak roster | Strong roster | SRS gap | Change | p |
| --- | --- | --- | ---: | ---: | ---: |
| Larry Drew | CLE -9.4 -> 0.22 | ATL +0.2 -> 1.96 | 9.6 | 7.41x | < 0.001 |
| George Karl | SAC -2.5 -> 0.00 | DEN +3.3 -> 0.27 | 5.8 | 6.92x | 0.082 |
| Mike D'Antoni | LAL -2.6 -> 0.27 | HOU +5.4 -> 0.77 | 8.0 | 2.63x | 0.048 |
| Byron Scott | LAL -7.7 -> 0.56 | NJN +0.7 -> 1.48 | 8.4 | 2.52x | 0.062 |
| Terry Stotts | ATL -4.5 -> 2.62 | POR +1.6 -> 1.16 | 6.2 | 0.43x | 0.004 |
| Monty Williams | DET -9.1 -> 0.49 | PHX +3.7 -> 1.11 | 12.7 | 2.16x | 0.040 |
| Stan Van Gundy | DET -0.6 -> 1.31 | ORL +4.8 -> 0.59 | 5.4 | 0.46x | 0.027 |
| Flip Saunders | WAS -6.1 -> 1.12 | DET +5.4 -> 2.09 | 11.5 | 1.95x | 0.244 |

Dwane Casey is the clearest case of a coach whose tendency is intrinsic. He coached Detroit at -5.2 SRS and Toronto at +2.3, so a seven and a half point difference in roster quality, and his surrender ratio did not move at all despite that. Scott Brooks is nearly as consistent, moving from 1.24 to 1.15 across a five point swing, and Larry Brown held to within 0.84 and 0.55 across a ten and a half point change in roster quality.

Larry Drew is the opposite being one of the most fluctuating, at 0.22 with Cleveland and 1.96 with Atlanta. For him his surrender tendency is  not a fixed trait, but instead a reaction to whatever situation he walked into.

Only 5 of the 20 changes are bigger than noise alone would produce at p < 0.05, where 1 would be expected by chance. So for the typical coach who changes teams the move is within what noise produces, and only a handful, Larry Drew and Terry Stotts most clearly, look like a tendency that really depends on the team.

As for Doc Rivers, who was the name I was originally curious about, he is absent from both tables (just like he is absent from in-game adjustments). All five of the teams he coached were at or above league average, giving him an SRS gap of only 3.7, which is below the threshold for either table. Within that narrow range his ratio still moved from 0.87 with a +4.1 SRS Clippers team to 1.41 with a +3.9 SRS Philadelphia team, though that is within what noise produces (p = 0.080).

*The per-franchise and per-season breakdowns behind these tables are in `coach_team.csv` and `coach_team_season.csv`.*

### How surrendering has increased over time

I mentioned that I noticed surrendering has increased over time when building the model to measure coach tendency, and it is something worth diving deeper into.

Across the first five seasons, 2000-01 to 2004-05, coaches surrendered in **7.9%** of trailing team-games. Across the last five, 2020-21 to 2024-25, the surrender rate became **15.8%**. The surrender rate has doubled, and correlating each season's rate against the year gives **+0.909**.

| Season | Trailing games | Surrendered | Rate | Median RCR when surrendering |
| --- | ---: | ---: | ---: | ---: |
| 2000-01 | 1,645 | 128 | 7.8% | 4.63 |
| 2001-02 | 1,635 | 142 | 8.7% | 4.75 |
| 2002-03 | 1,652 | 140 | 8.5% | 4.72 |
| 2003-04 | 1,658 | 116 | 7.0% | 5.20 |
| 2004-05 | 1,728 | 129 | 7.5% | 5.60 |
| ... | ... | ... | ... | ... |
| 2020-21 | 1,543 | 226 | 14.6% | 5.38 |
| 2021-22 | 1,775 | 269 | 15.2% | 5.15 |
| 2022-23 | 1,789 | 257 | 14.4% | 5.31 |
| 2023-24 | 1,768 | 308 | 17.4% | 5.39 |
| 2024-25 | 1,752 | 302 | 17.2% | 5.72 |

The last column shows that **the median RCR at which coaches surrender has actually increased**, going from 4.98 across the first five seasons to 5.39 across the last five, a correlation with the year of +0.516.

A higher median does not mean coaches are waiting until games are *more* hopeless before acting. Holding the RCR and time left fixed, with the same roster quality, the chance of surrendering per band in the last five seasons was **1.92 times** that of the first five (95% CI 1.73 to 2.14), and 1.81 times for the same coach. Meanwhile the share of trailing team-games reaching an RCR of 5 barely moved, from 43.5% to 42.6% (46.7% to 49.3% counting moments after a surrender). If the last five seasons had been met with the per-band readiness of the first five, the model puts their surrender rate at 8.3% instead of 15.5%, against 7.6% in the first five (all three among the team-games in the model). So coaches have lowered their standards, and that accounts for roughly nine tenths of the rise. How often games reach that state changed far less. The median still rose because readiness rose least at the bottom of the scale, 1.3 times between an RCR of 1.5 and 2 against about 2 times or more from 2.5 upwards.

The rise also correlates with particular league trends. From 2000-01 to 2012-13 the rate averaged 8.7%, and although it drifted slightly upward it did so weakly and unevenly, at a correlation of +0.622. From 2013-14 onwards it averaged 13.4% and climbed steadily at +0.886. The timing lines up with the three point era. A league taking far more threes at a faster pace produces a wider spread of outcomes, with the good teams being able to get ahead on the bad teams much more quickly, though as above that explains only a small part of the rise. 

So this is mostly a measurement of coaches becoming more willing to quit rather than games becoming less competitive.

*The full season by season series is in `comeback_rate_all.csv`, grouped by the season column.*

## Conclusion

So coaches do inherently differ in how readily they surrender. Faced with the same RCR and time left, in the same era, with a roster of the same quality, the quickest coach is roughly five times more likely to pull his starters than the slowest. Stephen Silas acts at 3.3% of moments where George Karl acts at 0.6%.

That tendency travels with the coach across different franchises at r = +0.306, and coaches like Dwane Casey and Scott Brooks barely move at all even when their roster changes by five to seven SRS points. Other coaches, like Larry Drew and Terry Stotts, have their tendencies swing by more than noise can explain depending on their players and roster, though only 5 of the 20 coaches who changed rosters do. So a coach's number is a general tendency rather than a fixed trait.

The behaviour is also becoming much more common, with the surrender rate doubling over 25 seasons from 7.9% to 15.8%, and coaches are giving up earlier than they used to, about twice as readily in the same situation, rather than there being far more games reaching the point where giving up makes sense.

## Limitations

**Intent is only inferred.** No coach announces that he is giving up. The last permanent exit of five starters is indicative of surrender, but could also be due to injury, ejection, foul trouble, or minute management unrelated to the score.

**The era control is a set of season dummies**, which absorbs everything that moved with time, including the three point revolution, pace and rule changes, without separating them. It removes era as a confounder but treats it as a black box.

**Each coach gets one hazard ratio applied at every band**, which assumes his effect is constant across all levels of hopelessness. A coach who is quick at an RCR of 3 but stubborn at 10 would be averaged into the middle.

**SRS is not a clean control.** It is built from point margin, and point margin is affected by surrendering itself, so the control variable and the outcome are not fully independent. It is also a season-level figure, meaning it describes the roster a coach had rather than the team he actually had available for a particular game. And it captures quality but not team depth.

**Play-by-play substitution data is less complete in earlier seasons.** Team-games with fewer than 15 recorded substitutions, or with substitutions logged in fewer than four periods, were excluded, which affects 2000-01 more than 2024-25, with pass rates of 76.7% and 98.0% respectively and median substitutions logged rising from 18 to 24. Since missing substitutions make a surrender undetectable, this could falsify the stated historical trend of surrendering becoming more common. However, dropping the thinnest logs actually shows a stronger trend. The per-band rise over the 24 seasons is 1.95x unrestricted, 2.20x with that filter, 2.37x among games with 18 or more substitutions, 2.35x at 20 or more, and 2.40x at 22 or more.

**A number of thresholds were chosen to be reasonable but still arbitrarily:** a deficit of at least 6 points and a minute remaining to count as trailing, 60 trailing games to enter the model and 100 to appear in the ranking, six time-left ranges, and for the roster tests 4 seasons, an SRS spread above 1.5, an SRS gap of 5 between clubs and 250 games. I tested if changing the 100 game floor would alter rankings, and the results came back negative. The rest are stated where used but their sensitivity is untested.

**2025-26 is excluded**, because that season uses an incompatible feed format requiring a separate parser.

## Data sources

Play-by-play comes from the NBA's own stats API, the playbyplayv2 endpoint at stats.nba.com, accessed through a GitHub mirror. Every event in every game: shots, rebounds, fouls, turnovers, timeouts, substitutions.

Team strength (SRS) and coach records come from Basketball Reference. The coach records give games coached per team-season, which is what lets mid-season sackings be split correctly.

Since the play-by-play came through a mirror rather than direct from the league, I checked nothing had been lost. Season minute totals rebuilt from the substitution events matched officially published minutes at a correlation of 1.0000 across eleven teams in four eras, with the largest discrepancy 0.15%.

I also conducted a series of random checks against the NBA's official scorer's report, to verify minutes data and confirm surrender flags. All checks passed.
