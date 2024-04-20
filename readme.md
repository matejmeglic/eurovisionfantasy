# Eurovision fantasy grading system

## Why build one?

Brief history is that Črt and Barbara hosted a competition that run on pen and paper question sets for every event and that grew in terms of competitiors that wanted to participate in the thrill of Eurovision night. Everyone printed their sheets, sent the results in via email. That resulted in Črt spending 1h+ grading and organizing results in 2023, so we decided that, if we want to scale the competition, we need a grading layer.

## Can this be reused?

In current state, sure. Best idea is to fork it and host it on heroku paid plan + PostGreSQL, the app itself is not whitelabeled yet (and there is currently no plans to do that).

## How does is work?

### Views

- index - bolierplate text
- admin - admin access
- error - simple error, no error handling
- thankyou - saving vote confirmation page
- gradingComplete - saving grading confirmation page
- email - mailing lists, returns all users from the DB (requires admin login as a safeguard, redirects to /vote)
- vote - voting page
- grade - grading page
- dryRunGrades - dryRun is a pre-save mechanism that grades all points, but allows grader to manipulate grades (and checks for errors) on an answer level. This is implemented to give the grader some control over the grades, punish the multiple select bug, implement a tiebreaker rule etc.
- results - show results

## Mechanics

### CSV format

IMPORTANT, can crash the app.
The app uses CSV format in many options (poll_question_set, quesiton_options etc.). The format should never contain spaces as they can break the app.

Correct example: Slovenija,Hrvaška,Anglija
Not correct example: Slovenija, Hrvaška, Anglija

### Basic setup and timeline

Admin has to set up the poll:

- create all questions (best way to start)
- create new season (multiple polls can be in a single season, then at grading polls are combined per season)
- create new poll (is_active = True)
  Poll is visible on the page.

Voters contribute their answers via /vote (have to input an email, name and optional group [that can be anything, but voters can agree to use the same separator to run "internal" results and find themselves easier in the results page]).

Admin closes the poll (is_active = False) and opens grading (is_grading = True).

Admin grades the results on /grade.

After grading is completed, admin sets (is_grading = False) and publishes the results (is_results = True). Results are shown.

### Question options

Any question has 3 required fields; Question itself, Question Type and Points that will be awarded.
There are other optional fields like Description, that renders under the question in the poll.
Admin would best craft questions that will render predictable results that will be scored correctly.

Question types:

- boolean
- textbox
- multipleselect
- radiobutton
- numvalue

#### Boolean

- renders True/False
- has a grading mechanism that allows admin to input another grading value for False (if empty = 0 points), as in fantasy league sometimes saying NO is a gamble for higher points, Example True 3 points - False 7 points.

#### Textbox

- an openended question that doesn't have a grading layer, unless it's an exact match (Example: England and england will not produce the same results due to app being in Slovene and there can be different ways of writing an answer). For that reason, in the /grade section, there are always provided all answers and the "correct" answer, so the grader can ammend the grading results correctly and fairly.

#### Multipleselect

- use values field to input values that should be rendered as options in csv format (no spaces!!!)
- max answers can be provided, but it does not do anything but warns the votes how many answers should they select (bug described in Improvements section)
- there is a mechanism that allows allocation of the partial scoring (Example: find 3/15 countries that will come to the finale? 3 countries = 10 points, 2 countries = 7 points, a single country = 3 points); in order to set this correctly, you have to (a) state full points in the points section, then (b) state partial points as csv value in another field ascending (Example: Points:10, Partial_points: 3,7)

#### Radiobutton

- use values field to input values that should be rendered as options in csv format (no spaces!!!)

#### Numvalue

- is a mechanism for determining INT values (Example: How many points will Slovenia get?) Only supports 0 or positive numbers.
- there is a grading mechanism that allows to put in range, that is then considered in grading (Example: grade=153, range=20 - results 153. 169, 141 get full points while 132, 209 do not [out of range])

#### Tiebreaker mechanism

- there is commonly a tiebreaker question that should be used in case the admin does not allow multiple winners
- you can select any type of a question, and set that question to be 0 points
- in the grading, once you get the results, you can repeat the grading process (just go back a bunch of times until /dryRunGrades) and just grade the tiebreaker question for the persons involved

### Seasons and results

- season is a concept for joining multiple polls together (Example: best-of-5 games in basketball will consist of a single season and five polls) and apply grading as a whole, it does not hold any information atm
- grading is currently always on the season level, results are shown (a) per season for all players and (b) per poll per player for that season, but there is no breakdown for per poll for all players. Question-level results are never shown to the public.
- there can be multiple seasons active at the same time, all the results are rendered based on polls with is_results = True

### Polls

- once all the questions are set, create a poll and assign it to the season (even a single poll has to have a season)
- select questions by their IDs, ordering on the /vote page will be as it's written on the question_set list. Use csv (no spaces, will break the app!!)
- there are three options: is_active, is_grading, is_results and in theory, only is_results is written in a way that can facilitate multiple seasons/polls combo (it will write the results based on name of the season, so you could run Eurovision 2024 vote, but already show results for Eurovision 2023 and, once voting is complete, render both seasons in the results page - 2024 will be on top, but be mindful of the season naming)
- that said, is_active and is_grading should have a single value active at one time. Having multiple entities set to True will result in both question_set be shown and/or graded, and that can be confusing to the voters.

## Obvious improvements

- currently the app allows grader to grade individual results, but intentionally doesn't let the grader to see the end (joined) results (grader has to accept the grading and then go to results). This can lead to multiple winners with the same results. There is a tiebreaker mechanism implemented, but for that, grader has to grade first time, then store, then check the results, then grade again, implement a tiebreaker, store results, check again - this would be much nicer if there was an interim screen with /results page, but... didn't go there ATM.
- error handling: currently the same person can save the form multiple times and will not be checked, they will just amass points at the end (attribution based on email)
- There is a bug with multiple select field (that wasn't properly implemented due to SQLlite db used for development and that does not understand arrays), so the user can in theory select more (or all) answers granting them all points. There is a mechanism built in for the grader to disqualify that question by grading it 0 points manually. Fair play should suffice.
- Arrays are implemented as csv fields+textFields atm
- There is a lot going on at the moment where a proper serializer should be. That part could use a rewamp
- Obvious next step is whitelabeling + user permissions (currently it works without any permissions, emails are stored directly in the db, any setup requires /admin access + staff rights)
- current codebase is set for heroku, so I just bugfixed on production (build without pipenv preview before), better handling of dev/prod env is crucial
- be more responsive (FE)

## What was good/would I do differently (Author's notes)?

- I would consider another level up with whitelabeling from the get-go
- I had major problems with dev-opsy things (git, deploy to heroku, procfile) that I am not versed in and have to relearn every time
- I really need to understand FE better or use another tool (Flutter)
- I am happy with how BE/FE communication is implemented, how context is flowing
- I think not requiring a login while protecting emails at all cost (keeping them behing admin permissions) is a great idea, because there can be two Barbaras, but it's highly unlikely there will be two persons using the same email
- After not being active in coding spiels for 2y+ I think this was a great excersize
- I can see that in the last views, my coding level went down (nasty for-loops) as I just "wanted it done"
- Quite sufficient self-QA process
- I am still unsure, whether I could describe the end solution to the AI or a no-code platform in a way, that it would "just work" as envisioned without me investing equal amount of time understanding the code it would produce. To be tested.

## Time spent

- 3h setup vsega
- 4h vote del + basic validation - 7
- 4h vote del dodajanje multiselecta, shranjevanje, routing, error handling - 11
- 5,5h celotni grading tool do ready to save, veliko dela na različnih možnostih ocen - 16.5
- 4,5h fe:bootstrap+theme+css+basic layout of all pages, copy - 21
- 2+1h transforming results, writing season_Grouping and then rewrtiting season grouping - 24
- 3h completing results view - 27
- 1h output of all emails + FE fixes + bring group to results - 28
- 4h devops for deploy to heroku - 32
- 2h fix ordering bugs and extra explanations on vote-grade + readme - 34
