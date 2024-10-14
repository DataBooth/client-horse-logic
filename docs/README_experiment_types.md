## HKJC- Brighter side of life project***

Code design update 12 Sep 2023

### CH-New WAV files to create

**Replace existing:**

Acquisition session started -- replace existing

Habit session started

Extinction session started

Reinstatement session started

**Create new:**

Criterion reached-end of session

Incorrect response tone for session type RP-H (habit)

Incorrect response tone for session type RP-E

### New session types names (simplified to reduce confusion)

- RP-A = acquisition of response
- RP-H = habit formation
- RP-E = extinction of response
- RP-R = reinstatement of response

**Sessions occur in order.**

All sessions types commence with double green button press to identify
system is ready and session commenced.

All sessions have capacity for blue button override and red button
pause/restart.

**Criterion determination- for MB info and RB to code then MB to
integrate?**

### Session type = RP-A (acquisition)

#### Objective of this session

Horses acquire the basic response of
responding to the start tone by touching the touch panel, triggering
correct response tone and receiving feed reward.

#### Session structure:

**Variable** number of **trials** per session-max=20

**Variable** number of **sessions** until criterion is reached.

Time limit between start tone and touch/button event= Unlimited

Criterion= *x* touches or button presses in a row under 20 s from
playing of start tone (integer -will be between 5-15). Log/count
calculate duration of period between start tone play and touch/button
event to determine when criterion has been reached.

When criterion reached, play "criterion reached, session ended" WAV and
terminate session.

### Session type = RP-H (Habit)

**Objective of this session:** Horses develop habitual responding to the
start tone and respond to it quickly and consistently across 60 sessions
of 20 trials per session.

**Session structure:**

**Fixed** number of trials per session=20

**Fixed** number of sessions = 3

**Time limit**= 45s between start tone play and touch/button event

**Two types of response for RP-H sessions:**

Correct response (go)= touch/button event within 45s of start tone

Incorrect response (no-go)= no touch/button event after 45s of start
tone.

Trial=

Play start tone

If time between start tone play and touch sensor/button press = \< 45s=
log as correct response and execute existing code to play correct
response tone and dispense feed.

If time between start tone = 45s, with no touch/button event (no-go) =
incorrect response.

Log as incorrect response, play "incorrect response RP-H" WAV and sleep
for set period as if feed had been dispensed, without operating servo
(time out period).

Then advance to next trial, play start tone and execute as per existing
code.

Log number of correct and incorrect responses per fixed trial session.

***Session type =*** **RP-E (extinction)**

**Objective of this session:** Horses stop responding to the start tone
because they no longer receive food rewards for touching the touch
panel. Servo operation is disabled but sleep/feed dispense intervals
remain the same as if food was being dispensed.

**Session structure:**

**Variable** number of **trials** per session**, max=20**

**Variable** number of **sessions** until extinction criterion is
reached.

Time limit= 20s for go/no-go response to start tone

**Two types of response for RP-E sessions:**

Incorrect response (go)=touch/button event within 20s of start tone

Correct response (no-go) = no touch/button event within 20s of start
tone

Trial=

Play start tone.

Incorrect response (go)=If time between start tone and touch/button
event = \< 20s log as incorrect response, play "incorrect response RP-E"
WAV. Then sleep for set time, then advance to next trial.

Correct response (no-go)=If time between start tone and no-go event =
20s (touch/button not triggered within 20s of start tone), log as
correct response, sleep for set-period then advance to next trial. No
audio feedback for a correct response.

Criterion= *n* in a row of no-go events for 20s per start tone interval
ie- horse hears the start tone but does not touch the panel so
touch/button is not triggered.

Perfect extinction would be 20 start tone plays with no-go responses ie
horse is no longer reacting to or engaging with the device. Criterion
likely to be 8 in row of no-go responses within 20 s. This integer needs
to be adjustable.

Log and count. When criterion reached, play "criterion reached, session
ended" WAV and end session.

**Session type=RP-R- (reinstatement)**

**Objective of this session:** The touch response to the start tone is
reinstated and the horse responds to the device again.

**Session structure:**

**Variable** number of **trials** per session**, max=20**

**Variable** number of **sessions** until reinstatement criterion is
reached.

Time limit between start tone and touch/button event= Unlimited

Criterion= *x* touches or button presses in a row under 20 s from
playing of start tone (integer -will be between 5-15).

Log/count calculate duration of period between start tone play and
touch/button event to determine when criterion has been reached.

When criterion reached, play "criterion reached, session ended" WAV and
terminate session.

End of RP part of experiment.
