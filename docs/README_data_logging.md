## HKJC Brighter Side of Life project

### Data logging

Two components:
- Per session per horse (whole session of $N_{\text{TRIAL}}$ trials/sequences).
- Per trial/sequence within a session.

*In the code, a trial is called a sequence, but could change it to a trial to make it less confusing.*

Events to log: Bulleted items below indicate logging events.

Start time of code execution (commencement of a session)

> **Sequence (Trial) $n$**

- Time of start tone activation (commencement of a trial)
- Time of touch sensor activation
- Time of feed dispense

> **Next sequence/trial $n+1$**

- Time of next sequence/trial start
- Time of touch sensor activation
- Time of feed dispense

> **Repeat $n = 1, 2, \ldots, N_{\text{TRIAL}}$ trials/sequences in total**

- Time of next sequence/trial start
- Time of touch sensor activation
- Time of feed dispense

> **Completion of $N_{\text{TRIAL}}$ trials/sequences**

- Time of end tone activation (end of a session)

### Calculations

- **Duration of session**: total time from start of code execution to end tone.
- **Response latency**: from start tone activation to touch sensor
activation - how long it takes horse to respond to cue and make the touch
response.
- **Duration of a trial/sequence**: time period between one start tone and
the next start tone. Even though the feed dispense and eat time is a
fixed amount of time would like to log this in case we change the eat
time to a variable time (unlikely but a possibility).
