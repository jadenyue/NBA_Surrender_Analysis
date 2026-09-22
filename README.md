# How hopeless does it have to get before a coach gives up?

Some coaches see surrendering as a strategical move to protect their players from injury when a game is hopeless, so they surrender as soon as a game seems out of reach. While others would rather ride their starters through a 40 point deficit than to give up. From observation, NBA coaches seem to differ in their tendency to surrender, so in this project, I used statistical methods to answer that hypothesis and to also explore other interesting phenomena of an often overlooked aspect of basketball.   

In this case, the act to "surrender" is defined as when a coach withdraws all five of his starters and never having them return. 

## The scale
To measure the differences in coach's tendency to surrender, a common measurement representing the time left, and the score of each game is needed, as being down 15 when there is 2 minutes left is a completely different situation than if there was 10. 

That scale is measured by the **required comeback rate (RCR)** 

As the trailing team, the deficit severity is measured by how many points per minute the team would have to gain on the opponent to tie the game at the buzzer.

```
required comeback rate (RCR) = deficit / minutes remaining      (points per minute)
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

A RCR of 1 to 1.5 is roughly coin flip, whereas when the RCR exceeds 5, the comeback becomes substantially rarer, and therefore, a coach surrendering when they face a low peak RCR can be said to have a much high tendency to surrender than a coach who only surrenders when they face a high RCR. 
The next step would be to build the complete data to be able to analyse a coach's tendency. 

### Building the data

Across 139 coaches with at least 60 trailing games, covering 42,278 team-games, at least one team surrenders in 11.1% of them.

The initial idea was to test and compare each coach against that 11.1%. But coaches worked in different decades and with different rosters, and both of those factors affect how often a team ends up conceding. Brian Keefe coaching the 17 win Wizards in 2025-26 is going to concede more than Steve Kerr coaching the 73 win Warriors in 2015-16, simply just because Keefe would be in more situations where surrender would be considered, even if the two coach's actually have the same tendency.

So the fairer measure is to see whether a coach's surrender decisions **would** differ from other coaches in the exact same situation. Where they were facing the same RCR, coaching a team of the same quality in the same era, and see if one coach would pull his starters while another kept playing.


#### 1. Work out the RCR at every moment

Using play-by-play data, the record every event in a game: made shots, rebounds, fouls, turnovers, timeouts, substitutions, can be constructed. A typical NBA game logs 400 to 500 of them, so about 200 per team.
At every event where the team is trailing, we calculate the RCR.

#### 2. Reducing database into one figure per game
Every trailing team-game is given two data points: a required rate and a flag for whether the coach conceded.
If he conceded, the row is marked 1 and the rate is the RCR at the moment his starters came off. If he didn't, the rate is the highest the team faced while they were still on the floor. 

#### 3. Sorting each game RCR into bands 
We sort each game's final RCR statistic into a band to be able to compare with other coaches that surrendered at the same band, or allowed that band to occur without surrendering. 
Then, every band below the decided band gets filled with 0, as a team that reached 4.2 passed through 1.2, and 2.9, and 3.7 on the way. The team was in those spots and the coach make the decision to not pull anyone, so marking the rows with 0 allows the data to reflect a coach that did not act when faced with that RCR.

Doing so gives 42,278 team-games expanded into 261,696 band-observations, of which 4,681 are a surrender, for a baseline of 1.79% per band.


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

Every team passes through the first band, but only 848 exceed 25, because for most coaches, they surrender before it ever gets that bad.  The chance of conceding peaks between 5 and 10 and then falls, which does not mean that coaches are becoming more stubborn at extreme deficits, but rather a feature of selection, as the teams still not surrendering when raced with a RCR of 15 are coaches that probably would never surrender no matter what.

Each row of that table is a matched comparison set. Coaches are only ever compared against each other within the same band.

### The model

Fit a logistic regression on those 261,696 rows, predicting whether a concession happened:

```
logit P(concede at this rung) = intercept + rung dummies + season dummies + b x team SRS
```

The band dummies give every level of hopelessness its own baseline, which is what holds the situation constant. The season dummies account for the fact that conceding became much more common over time across 29 seasons. The SRS term handles roster quality. In this model, there is no coach variable, so the model predicts as well as it can while not knowing the coach.

(Simple Rating System by Basketball Reference, read more here)


Then we fit the same model again with it now having a  coach variable, and see whether knowing the coach helps the model predict whether a surrender occured better. 

```
without coach effects:  log-likelihood -20,374.4
with coach effects:     log-likelihood -20,073.2
```

Adding coaches improved the fit by 301 points. The problem is that adding 138 parameters always improves fit, even if coaches are irrelevant, because noise is partly fittable. So the improvement has to be measured against what chance alone would buy:

```
LR chi-square = 2 x 301.2 = 602 on 138 degrees of freedom,  p = 2.9 x 10^-59
```

If coaches added nothing, each useless parameter would add about 1 point on average and the statistic would land near 138. It is 602, so roughly 464 points of it is genuine signal.

### The answer

Yes. Held at the same RCR, in the same era, with the same roster quality, coach identity still predicts the decision to surrender overwhelmingly.

Looking at only coaches with 100 or more trailing games, hazard ratios vary from 0.34 to 2.12, a 6.3 fold range:

| Quickest | HR | Slowest | HR |
| --- | --- | --- | --- |
| Stephen Silas | 2.12 | George Karl | 0.34 |
| Paul Silas | 2.11 | Butch Carter | 0.43 |
| Wes Unseld | 2.04 | Mike D'Antoni | 0.44 |
| Rudy Tomjanovich | 1.99 | Rick Pitino | 0.44 |
| Terry Porter | 1.85 | Isiah Thomas | 0.46 |
| Jim Boylen | 1.79 | Erik Spoelstra | 0.47 |

Against the 1.79% baseline, a hazard ratio of 2.12 means a 3.8% chance of acting at any given RCR, and 0.34 means a 0.6% chance.

Therefore in theory, if Stephen Silas and George Karl were in the identical spot, both needing 4 points per minute to come back, coaching a league average roster in the same season, Silas is roughly six times more likely to have surrendered.

So yes, coaches do inherently differ in their surrender tendency independent of their team or era, at most by 6 times. Now with the initial question answered, I wanted to explore more into analysing coaches surrendering to finding some other interesting artefacts. 


### Is it the coach or the roster?
The model already removes era and roster when comparing one coach to another, but for a coach like Doc Rivers who moved across several franchises, it'll be interesting to see whether his surrender tendency changes with his team coached.

By taking 76 coaches who lasted four or more seasons and had real variation in roster quality. Subtract each coach's own average, so all that remains is how he moved from year to year:

```
within-coach slope: -0.143 percentage points of concede rate per SRS point
                    SE 0.057, t = -2.49, n = 675 coach-seasons
```

The sign is interesting part, as the same coach with a better roster surrenders less than if he had a bad roster, by about 1.4 percentage points per ten SRS points. The reasoning would be that a good team that is behind has more reason to think it can come back, so the coach leaves his starters out there.

Now looking at the sixty coaches coached two or more franchises with at least 60 trailing games at each. We pair each coach's rate at his main franchise against the weighted average of his others, then correlate across coaches:
```
r = +0.306, 95% CI [+0.084, +0.502], 3,000 bootstrap resamples over coaches
```
The interval excludes zero, so something inherent does travel with the coach. For comparison, the correlation of roster strength across the same coaches' clubs is +0.233, meaning a coach's tendency follows him slightly better than his luck with rosters does.

But the +0.306 effect is moderate, and the individual cases show why. Some coaches have their surrender tendency stay incredibly consistent across very different rosters, and others are not consistent at all.

To see this, if we take the 22 coaches who had both a real change in roster quality between clubs, meaning at least 5 SRS points, and enough games for the rates to mean something, meaning at least 250 trailing games. Then sort them by how much their concede rate moved.

The most stable coaches
Coach	Weak roster	Strong roster	SRS gap	Rate change
Isiah Thomas	NYK -4.8 -> 5%	IND +0.5 -> 5%	5.3	0.0 pt
Doug Collins	WAS -1.5 -> 6%	DET +3.7 -> 7%	5.3	0.9 pt
Quin Snyder	ATL -1.9 -> 8%	UTA +3.8 -> 11%	5.7	2.5 pt
Mike Budenholzer	ATL -0.4 -> 19%	MIL +5.6 -> 16%	6.0	2.6 pt
Dwane Casey	DET -5.2 -> 7%	TOR +1.8 -> 4%	7.0	2.9 pt
Brian Hill	VAN -7.6 -> 8%	ORL -0.4 -> 5%	7.2	2.9 pt
Mike Dunleavy	LAC -3.6 -> 7%	POR +4.1 -> 3%	7.7	4.4 pt
Byron Scott	LAL -7.6 -> 12%	NJN +0.3 -> 11%	7.9	4.7 pt

The most stable coaches
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

 Coaches whose tendency changed dramatically depending on team
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


For Flip Saunders, it's clear that this is a coach whose tendency is his own. He ran 11% on a -6.0 Washington roster and 12% on a +5.3 Detroit one, so an eleven point swing in team quality moved him by a single point.

Larry Drew is the opposite, at 3% with Cleveland and 20% with Atlanta. Larry Brown ran 10% in New York and 3% in Detroit. For these two the number is clearly not a fixed trait.

For Doc in particular, although he was the name I was originally focused on, he is actually absent from both tables (just like he his absence from in-game adjustments :) ). All four of his teams coached were at or above league average, giving him an SRS gap of only 3.6, which is below the threshold for either table. He does show stability in his tendencies as from coaching a +0.4 SRS Orlando Team to a +4.0 SRS Clippers team is hazard ratio only increased by 2%.



### How surrendering has increased over time 

