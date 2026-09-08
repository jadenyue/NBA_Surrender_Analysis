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

Additionally, adding an interaction between the indicator and the length of the settled window, we can see the effect weakening sharply when the window widens. When a game is settled with 2 to 4 minutes left, the opponent's bench emptying doubles the odds of following. While in games that are settled with more than twelve minutes, the effect is almost nonexistent. A narrow window forces a decision and the other coach going first makes it acceptable, whereas with twenty minutes left, there's no urgency and no need to commit. 

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

## Variables that do and don't matter in determining surrender odds

By identifying three variables that potentially influence a coach's decision to surrender and conducting statistical analysis on the effects, it can be seen that only one of the three parameters can be shown to have a real effect.

| Predictor                        |    OR |        95% CI |     z | Real effect? |
|----------------------------------|------:|--------------:|------:|--------------|
| Own team strength (per SRS point) | 1.101 | [1.094, 1.109] | +28.9 | yes         |
| Playing at home                   | 1.026 | [0.967, 1.088] |  +0.8 | no          |
| Opponent strength (per SRS point) | 0.998 | [0.991, 1.004] |  -0.7 | no          |

 Playing at home has no effect on coach's decision to surrender. Which is surprising as home-court advantage is one of the most studied aspects in all of sports. It raises scoring rates (Ribeiro et al., 2016), inflates subjective stat-keeping (Bommela et al.,2021), and bends officiating (Price, Remer & Stone, 2012). Home court advantage turns up almost everywhere, but does not change a coach's tendency to surrender. On average, there doesn't seem to be any embarrassment effect in front of your own crowd, nor extra push for the home fans who bought tickets. 

Opponent quality is irrelevant too, suggesting that coaches respond to their own position rather than to who is beating them. What does matter is the strength of your own team. Coaches of good teams give up on games more quickly than bad ones, which may seem counterintuitive at first, but a good team's bench is deeper, so emptying it costs less, and the star player of a good team would be more valuable to rest and protect.

## Different coaches differ in their tendency to surrender enormously 
This was the question that initially inspired this study: finding the differences in how reactive a coach is to surrender.

The obvious way to measure this is to count the share of decided games in which each coach coach end with his starters of. However, this fails to account for the vast differences in surrender window. 

| Game was settled for | Share of teams who pulled |
|----------------------|--------------------------:|
| under 1 minute       |                      0.4% |
| 1–4 minutes          |                      8.0% |
| 4–8 minutes          |                     39.8% |
| 8+ minutes           |                      57.9% |

A coach whose games happened to be settled early would have a high raw percentage without having a quicker tendency to act. 

This issue can be solved once again by using the discrete-time hazard model and splitting each game into 30 second intervals. 

Additionally, Only games with at least 4 minutes remaining when settled were included. This filter is necessary as bad teams get disproportionally blown out while also pulling their starters far less than winning teams (41% vs 55%). So a coach of a bad team accumulates a pile of games where the team is getting blown out early, and in those he rarely withdraws. That drags his estimate toward zero without any connection to his actual tendency. 

If no minimum window is implemented, the failure can be seen below:
| Coach        | Season  | Team record     | Team SRS | Games coached |   HR | %pull |  n |
|--------------|---------|-----------------|---------:|---------------|-----:|------:|---:|
| Bill Hanzlik | 1997-98 | Denver 11–71    |   −11.74 | 82 of 82      | 0.09 |    2% | 82 |
| Mike Dunlap  | 2012-13 | Charlotte 21–61 |    −9.29 | 82 of 82      | 0.11 |    2% | 82 |
| Ed Tapscott  | 2008-09 | Washington 19–63 |   −6.98 | 71 of 82      | 0.14 |    3% | 71 |
| Dick Motta   | 1996-97 | Denver 21–61    |    −6.40 | 69 of 82      | 0.18 |    3% | 69 |
| M.L. Carr    | 1996-97 | Boston 15–67    |    −6.62 | 82 of 82      | 0.30 |    5% | 

The coaches that seem to surrender the most are five one-season coaches of terrible teams, and the ranking becomes a list of bad teams rather than an actual measure of coaches' tendency.

With the minimum window of 4 minutes:
|                              |   Value |
|------------------------------|--------:|
| Settled team-games           |  23,328 |
| Coach-attributed             |  22,145 |
| Half-minute intervals        | 270,832 |
| Intervals ending in a pull   |  10,085 |
| Baseline chance per interval |   3.72% |

Fitting to the model
```
logit(chance of pulling in interval k) = α_k + β_coach + γ × [eventual winner]
```
Where: 
|           | Meaning                                                                                                    |
|-----------|------------------------------------------------------------------------------------------------------------|
| `α_k`     | a free parameter per interval index - lets the model learn how the urge builds over settled time, without assuming a shape |
| `β_coach` | each coach's own adjustment; `exp(β)` is his hazard ratio                                                   |
| `γ`       | winners pull faster than losers: +0.286, z = +13.1                    

Looking at the 109 coaches that have coached at least 60 settled games:

Quickest to surrender
| Coach            |   HR |       95% CI |    z | Median wait (min) | %pull |   n |
|------------------|-----:|-------------:|-----:|------------:|------:|----:|
| Darvin Ham       | 2.36 | [1.66, 3.35] | +4.8 |        4.17 |   77% |  60 |
| Ime Udoka        | 2.23 | [1.70, 2.93] | +5.8 |        4.35 |   82% | 125 |
| Chris Finch      | 2.14 | [1.65, 2.76] | +5.8 |        4.88 |   82% | 151 |
| Nick Nurse       | 1.88 | [1.47, 2.40] | +5.1 |        5.13 |   72% | 215 |
| Mike Budenholzer | 1.86 | [1.48, 2.34] | +5.3 |        4.90 |   70% | 300 |
| Phil Jackson     | 1.67 | [1.34, 2.10] | +4.5 |        5.28 |   65% | 346 |


Slowest:
| Coach         |   HR |       95% CI |    z | Median wait (min) | %pull |   n |
|---------------|-----:|-------------:|-----:|------------:|------:|----:|
| Rick Pitino   | 0.29 | [0.17, 0.49] | −4.6 |       never |   15% |  97 |
| Sidney Lowe   | 0.31 | [0.17, 0.58] | −3.7 |       never |   18% |  60 |
| George Karl   | 0.36 | [0.28, 0.48] | −7.2 |        21.2 |   22% | 411 |
| David Fizdale | 0.42 | [0.26, 0.69] | −3.4 |        19.1 |   25% |  73 |
| Doug Collins  | 0.51 | [0.37, 0.72] | −3.9 |        13.1 |   28% | 170 |
| Mike D'Antoni | 0.52 | [0.40, 0.68] | −4.9 |        13.1 |   31% | 348 |

Ham and Pitino differ by ≈8.5x in their hazard ratio. So in theory, if these two coaches were in the same situation: same score, same clock, same time since the game stopped being competitive, Ham is roughly 8.5 times more likely than Pitino to surrender in the next thirty seconds.

The full ranking of all 109 coaches and the Python file used to compute the coach statistics can be found in XXX

# Conclusion, Limitations, and Where This Goes

## Conclusion
Four findings:
1. Coaches quit on a curve and the threshold scales with the amount of time left. Coaches need, on average, a 26 point differential to surrender at twelve minutes, and 14 at two. The leading coach consistently waits two to three points longer than the trailing one due to asymmetric risk. 

2. Surrendering has become far more common, but not because coaches tendency changed. The share of games with at least one surrender rose from 22.8% to 36.6%. Yet the median margin at surrender has remained at around 21 points the entire time. Coaches did not lower their standards to surrender. The league produced more blowouts meeting them.

3. The decision spreads between coaches on the same game. Once an opponent has emptied his, a coach's odds of following are multiplied by 1.49, and the effect is more concentrated where the window is narrow, reaching 2.29 at one minute left. 

4. Coaches differ enormously in whether they concede based on their coaching style. Hazard ratios differ by 8.5x at the most extreme, but among games where a coach did surrender, the timing difference is extremely small.

## Limitations

1. The event of surrender is inferred rather than observed. Coaches never state their intent of surrender, so the observation of the last permanent exit of five starters is consistent with surrender, but also with injury, ejection, foul trouble, or minute management unrelated to the score itself. 

2. The four-minute filter on measuring differences in coach tendency is arbitrary. The surrender rate increases smoothly through 0.4%, 8.0%, 39.8% and 57.9% with no natural break. However, looking at the correlations against the four-minute version result in 1.000, 1.000, 0.978 and 0.929 at two, three, six and eight minutes respectively. Therefore, the threshold choice does not impact the results findings significantly, but it is still relevant to mention as a limitation. 

3. The contagion result is not proven to be a mechanism. We know only the odds of whether the opponent had withdrawn, but not if a coach was actually influenced by the opposing coach or both coaches read the same scoreboard and came to the same conclusion independently. 

4. The data is partially incomplete. As the substitutions are not all recorded. Using the best available CSV files of NBA play-by-play data, a few games had incomplete data about substitutions. Games with less than 15 substitutions (median is 20) were excluded from analysis. This lack of data affects older seasons more significantly, with only 74% of 1996-97 team games passing the test, while 98.7% in 2025-26. Which could create bias in the "surrender is happening more" claim. 

5. Team strength is contaminated by the outcome. Basketball's own SRS metric is built from point margin, and point margin is compressed by the behaviour under study. A leading coach emptying his bench costs about 1.2 points off the final margin. The contamination is small against a 4.6 point standard deviation, but the circularity exists.

## Why it Matters, and Where it Leads 

The most informative result is the one that did not move. Incidence rose from 22.8% to 36.6% of games while the median margin at surrender held at roughly 21 points throughout. Had coaches lowered their standards, the required margin would have fallen. It did not. The rise therefore reflects a change in the games rather than in the coaching, and it constitutes a behavioural measure of competitive imbalance: a count of games that professionals judged unwinnable while they were still in progress.

Approximately one game in three is now abandoned by at least one side. In the late 1990s the figure was closer to one in five. Extrapolating the recent slope places the rate above 40% within a decade.

### The timing points to style, not talent

The series is not a steady climb — it is flat through the first half of the sample and then turns. That shape rules out the structural changes usually invoked to explain rising scores. The 2004 hand-checking ban raised offensive efficiency immediately and left the surrender rate untouched for years afterwards. The 2011 lockout and the CBA that followed did nothing to it either.

What the turn coincides with is the three-point revolution. A league in which two-fifths of shots are threes, taken at a faster pace, produces a wider distribution of outcomes than one shooting a fifth of its attempts from range — not because the teams are less equal, but because each possession carries more variance. Leads that once took a quarter to build now arrive in minutes. The mechanism is arithmetic rather than competitive decay.

That distinction matters, because the two explanations imply opposite remedies.

### What this suggests about the next decade

**The second apron probably will not help.** The 2023 CBA's restrictions are designed to break up talent concentrations, and they are already forcing roster decisions that would have been unthinkable under the previous agreement. If the rise were driven by superteams, this would arrest it. But the association here runs with how the game is played, and dispersing talent does not make anyone shoot fewer threes. The likely outcome is that the apron flattens the tail of the distribution — fewer historic juggernauts — while leaving the typical blowout untouched.

**Expansion would push the other way.** Adding franchises dilutes the talent pool across more rotation spots, and expansion seasons have historically produced weaker teams at the bottom of the league. Whatever the apron removes from the top, expansion is likely to add at the bottom.

**The 65-game rule may be counterproductive here.** The 2023 participation policy requires a player to appear in 65 games to qualify for major awards, with a game counting only if he plays twenty minutes or more. A coach can therefore satisfy the rule and still withdraw his star at the twenty-minute mark — which in a decided game is exactly the behaviour this study measures. The policy addresses absence from whole games. It does nothing about departure from decided ones, and its threshold structure arguably encourages it.

### Two further consequences

**The trend is partly self-reinforcing.** One coach conceding makes the other substantially more likely to follow, and that reciprocity has itself been strengthening across the sample. Each additional blowout therefore generates more than one abandonment, so the projection above should be read as a lower bound rather than a central estimate.

**The minutes lost are the valuable ones.** Stronger teams concede sooner, so the games most likely to end early are those featuring the best teams and the highest-profile players — precisely the games with the largest audiences.

### A note on incentives

None of this indicates suboptimal coaching. Conceding a decided game carries no measurable cost and protects a valuable asset, so the observed behaviour is consistent with rational play. The eightfold spread between coaches persists precisely because the decision is unconstrained: absent cost or sanction, individual variation goes unsuppressed. It follows that the behaviour will not change without a change in incentives, and that no rule aimed at rosters or at absence from whole games will touch it.

### What would resolve the open questions

Three data additions would settle most of what remains ambiguous. **Injury-report records** would separate concession from forced substitution. **Withdrawal ordering with a cluster-robust variance** would identify sequence and correct the contagion intervals. And a **team-strength measure restricted to contested minutes** would eliminate the circularity in the control variable. All three lie beyond what public play-by-play alone can support.
