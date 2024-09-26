## `Experiment_2023-10-09T17:45:46.540359_apollo_5_Training randomised Type 1.log`

0. ExeperimentCB Table

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| ExperimentID       | 1                                                  |
| Cohort             | (not provided)                                    |
| SubjectName        | apollo                                            |
| SubjectNumber      | 0                                                  |
| SessionNumber      | 5                                                  |
| SessionType        | Training                                          |
| ExperimentType     | Training randomised Type 1                        |
| Comment            | Positive = LEFT                                   |
| DateTime           | 2023-10-09 17:45:46.540359                       |
| LogFileName        | Experiment_2023-10-09T17:45:46.540359_apollo_5_Training randomised Type 1.log |

### Explanation of Each Field

- **ExperimentID**: Unique identifier for the experiment.
- **Cohort**: Not provided in the log file, so left blank (will set this to the location e.g. CSU).
- **SubjectName**: The name of the subject involved in the experiment.
- **SubjectNumber**: Set to 0 for this example; typically, this would be looked up from a subject database.
- **SessionNumber**: Indicates which session this trial belongs to.
- **SessionType**: Describes the type of session (in this case, "Training").
- **ExperimentType**: Describes the specific type of experiment conducted.
- **Comment**: Contains additional context about the trial or experiment.
- **DateTime**: The timestamp indicating when the experiment started.
- **LogFileName**: The name of the log file associated with this experiment.

1. TrialCB Table:

| TrialID | ExperimentID | TrialNumber | ResponseType | TrialSubType | Direction | CriterionType | CriterionCount | TrialStartTime        | TrialEndTime          | SessionType |
|---------|--------------|-------------|--------------|--------------|-----------|---------------|----------------|------------------------|------------------------|-------------|
| 1       | 1            | 1           | GO           | P            | LEFT      | positive      | 1              | 2023-10-09 17:50:14.143264 | 2023-10-09 17:50:26.919705 | Training    |
| 2       | 1            | 2           | NOGO         | N            | LEFT      | negative      | 1              | 2023-10-09 17:50:38.927073 | 2023-10-09 17:53:29.968300 | Training    |
| 3       | 1            | 3           | GO           | P            | LEFT      | positive      | 2              | 2023-10-09 17:53:41.971244 | 2023-10-09 17:54:21.266292 | Training    |
| 4       | 1            | 4           | GO           | N            | LEFT      | NULL          | NULL           | 2023-10-09 17:54:33.274255 | 2023-10-09 17:56:00.046265 | Training    |
| 5       | 1            | 5           | NOGO         | N            | LEFT      | negative      | 2              | 2023-10-09 17:56:12.054307 | 2023-10-09 17:57:19.116385 | Training    |
| 6       | 1            | 6           | GO           | P            | LEFT      | positive      | 3              | 2023-10-09 17:57:31.119283 | 2023-10-09 17:57:55.169267 | Training    |
| 7       | 1            | 7           | GO           | N            | LEFT      | NULL          | NULL           | 2023-10-09 17:58:07.178272 | 2023-10-09 17:59:53.701160 | Training    |
| 8       | 1            | 8           | GO           | P            | LEFT      | positive      | 4              | 2023-10-09 18:00:05.709267 | 2023-10-09 18:00:50.038745 | Training    |
| 9       | 1            | 9           | GO           | P            | LEFT      | positive      | 5              | 2023-10-09 18:01:02.043238 | 2023-10-09 18:02:35.342735 | Training    |
| 10      | 1            | 10          | NOGO         | N            | LEFT      | negative      | 3              | 2023-10-09 18:02:47.345237 | 2023-10-09 18:04:28.534258 | Training    |
| 11      | 1            | 11          | GO           | P            | LEFT      | positive      | 6              | 2023-10-09 18:04:40.539254 | 2023-10-09 18:05:11.801773 | Training    |
| 12      | 1            | 12          | NOGO         | N            | LEFT      | negative      | 4              | 2023-10-09 18:05:23.808218 | 2023-10-09 18:08:02.642448 | Training    |
| 13      | 1            | 13          | GO           | N            | LEFT      | NULL          | NULL           | 2023-10-09 18:08:14.645842 | 2023-10-09 18:08:45.246303 | Training    |
| 14      | 1            | 14          | GO           | P            | LEFT      | positive      | 7              | 2023-10-09 18:08:57.248272 | 2023-10-09 18:09:29.922994 | Training    |
| 15      | 1            | 15          | NOGO         | N            | LEFT      | negative      | 5              | 2023-10-09 18:09:41.927216 | 2023-10-09 18:12:17.276907 | Training    |
| 16      | 1            | 16          | GO           | P            | LEFT      | positive      | 8              | 2023-10-09 18:12:29.285217 | 2023-10-09 18:13:03.342167 | Training    |
| 17      | 1            | 17          | GO           | P            | LEFT      | positive      | 9              | 2023-10-09 18:13:15.347257 | 2023-10-09 18:14:53.377774 | Training    |
| 18      | 1            | 18          | NOGO         | N            | LEFT      | negative      | 6              | 2023-10-09 18:15:05.382236 | 2023-10-09 18:17:17.925594 | Training    |
| 19      | 1            | 19          | GO           | P            | LEFT      | positive      | 10             | 2023-10-09 18:17:29.928718 | 2023-10-09 18:18:01.437739 | Training    |
| 20      | 1            | 20          | NOGO         | N            | LEFT      | negative      | 7              | 2023-10-09 18:18:13.441239 | 2023-10-09 18:20:42.720777 | Training    |

2. ResponseCB Table:

| ResponseID | TrialID | ResponseTime | EventDateTime        |
|------------|---------|--------------|----------------------|
| 1          | 1       | 9.151622     | 2023-10-09 17:50:26.919705 |
| 2          | 3       | 11.543718    | 2023-10-09 17:54:21.266292 |
| 3          | 4       | 11.528231    | 2023-10-09 17:56:00.046265 |
| 4          | 6       | 9.848299     | 2023-10-09 17:57:55.169267 |
| 5          | 7       | 21.996519    | 2023-10-09 17:59:53.701160 |
| 6          | 8       | 11.117833    | 2023-10-09 18:00:50.038745 |
| 7          | 9       | 10.262957    | 2023-10-09 18:02:35.342735 |
| 8          | 11      | 12.766254    | 2023-10-09 18:05:11.801773 |
| 9          | 13      | 19.630359    | 2023-10-09 18:08:45.246303 |
| 10         | 14      | 11.391896    | 2023-10-09 18:09:29.922994 |
| 11         | 16      | 11.423845    | 2023-10-09 18:13:03.342167 |
| 12         | 17      | 10.391335    | 2023-10-09 18:14:53.377774 |
| 13         | 19      | 10.046309    | 2023-10-09 18:18:01.437739 |

3. EventCB Table:

| EventID | TrialID | EventType                             | EventTime               | ElapsedTime |
|---------|---------|---------------------------------------|-------------------------|-------------|
| 1       | 1       | Current Trial                         | 2023-10-09 17:50:14.143264 | 0.000000    |
| 2       | 1       | Green button pressed - horse released | 2023-10-09 17:50:17.768052 | 3.624788    |
| 3       | 1       | GO                                    | 2023-10-09 17:50:26.919705 | 12.776441   |
| 4       | 2       | Current Trial                         | 2023-10-09 17:50:38.927073 | 0.000000    |
| 5       | 2       | Green button pressed - horse released | 2023-10-09 17:52:29.968279 | 111.041206  |
| 6       | 2       | NOGO                                  | 2023-10-09 17:53:29.968300 | 171.041227  |
| 7       | 3       | Current Trial                         | 2023-10-09 17:53:41.971244 | 0.000000    |
| 8       | 3       | Green button pressed - horse released | 2023-10-09 17:54:09.722465 | 27.751221   |
| 9       | 3       | GO                                    | 2023-10-09 17:54:21.266292 | 39.295048   |
| 10      | 4       | Current Trial                         | 2023-10-09 17:54:33.274255 | 0.000000    |
| 11      | 4       | Green button pressed - horse released | 2023-10-09 17:55:48.518037 | 75.243782   |
| 12      | 4       | GO                                    | 2023-10-09 17:56:00.046265 | 86.772010   |
| 13      | 5       | Current Trial                         | 2023-10-09 17:56:12.054307 | 0.000000    |
| 14      | 5       | Green button pressed - horse released | 2023-10-09 17:56:19.116396 | 7.062089    |
| 15      | 5       | NOGO                                  | 2023-10-09 17:57:19.116385 | 67.062078   |
| 16      | 6       | Current Trial                         | 2023-10-09 17:57:31.119283 | 0.000000    |
| 17      | 6       | Green button pressed - horse released | 2023-10-09 17:57:45.320918 | 14.201635   |
| 18      | 6       | GO                                    | 2023-10-09 17:57:55.169267 | 24.049984   |
| 19      | 7       | Current Trial                         | 2023-10-09 17:58:07.178272 | 0.000000    |
| 20      | 7       | Green button pressed - horse released | 2023-10-09 17:59:31.704638 | 84.526366   |
| 21      | 7       | GO                                    | 2023-10-09 17:59:53.701160 | 106.522888  |
| 22      | 8       | Current Trial                         | 2023-10-09 18:00:05.709267 | 0.000000    |
| 23      | 8       | Green button pressed - horse released | 2023-10-09 18:00:38.920273 | 33.211006   |
| 24      | 8       | GO                                    | 2023-10-09 18:00:50.038745 | 44.329478   |
| 25      | 9       | Current Trial                         | 2023-10-09 18:01:02.043238 | 0.000000    |
| 26      | 9       | Green button pressed - horse released | 2023-10-09 18:02:25.080445 | 83.037207   |
| 27      | 9       | GO                                    | 2023-10-09 18:02:35.342735 | 93.299497   |
| 28      | 10      | Current Trial                         | 2023-10-09 18:02:47.345237 | 0.000000    |
| 29      | 10      | Green button pressed - horse released | 2023-10-09 18:03:28.534260 | 41.189023   |
| 30      | 10      | NOGO                                  | 2023-10-09 18:04:28.534258 | 101.189021  |
| 31      | 11      | Current Trial                         | 2023-10-09 18:04:40.539254 | 0.000000    |
| 32      | 11      | Green button pressed - horse released | 2023-10-09 18:04:59.035480 | 18.496226   |
| 33      | 11      | GO                                    | 2023-10-09 18:05:11.801773 | 31.262519   |
| 34      | 12      | Current Trial                         | 2023-10-09 18:05:23.808218 | 0.000000    |
| 35      | 12      | Green button pressed - horse released | 2023-10-09 18:07:02.642547 | 98.834329   |
| 36      | 12      | NOGO                                  | 2023-10-09 18:08:02.642448 | 158.834230  |
| 37      | 13      | Current Trial                         | 2023-10-09 18:08:14.645842 | 0.000000    |
| 38      | 13      | Green button pressed - horse released | 2023-10-09 18:08:25.615940 | 10.970098   |
| 39      | 13      | GO                                    | 2023-10-09 18:08:45.246303 | 30.600461   |
| 40      | 14      | Current Trial                         | 2023-10-09 18:08:57.248272 | 0.000000    |
| 41      | 14      | Green button pressed - horse released | 2023-10-09 18:09:18.531072 | 21.282800   |
| 42      | 14      | GO                                    | 2023-10-09 18:09:29.922994 | 32.674722   |
| 43      | 15      | Current Trial                         | 2023-10-09 18:09:41.927216 | 0.000000    |
| 44      | 15      | Green button pressed - horse released | 2023-10-09 18:11:17.276917 | 95.349701   |
| 45      | 15      | NOGO                                  | 2023-10-09 18:12:17.276907 | 155.349691  |
| 46      | 16      | Current Trial                         | 2023-10-09 18:12:29.285217 | 0.000000    |
| 47      | 16      | Green button pressed - horse released | 2023-10-09 18:12:51.918371 | 22.633154   |
| 48      | 16      | GO                                    | 2023-10-09 18:13:03.342167 | 34.056950   |
| 49      | 17      | Current Trial                         | 2023-10-09 18:13:15.347257 | 0.000000    |
| 50      | 17      | Green button pressed - horse released | 2023-10-09 18:14:42.986387 | 87.639130   |
| 51      | 17      | GO                                    | 2023-10-09 18:14:53.377774 | 98.030517   |
| 52      | 18      | Current Trial                         | 2023-10-09 18:15:05.382236 | 0.000000    |
| 53      | 18      | Green button pressed - horse released | 2023-10-09 18:16:17.926250 | 72.544014   |
| 54      | 18      | NOGO                                  | 2023-10-09 18:17:17.925594 | 132.543358  |
| 55      | 19      | Current Trial                         | 2023-10-09 18:17:29.928718 | 0.000000    |
| 56      | 19      | Green button pressed - horse released | 2023-10-09 18:17:51.391368 | 21.462650   |
| 57      | 19      | GO                                    | 2023-10-09 18:18:01.437739 | 31.509021   |
| 58      | 20      | Current Trial                         | 2023-10-09 18:18:13.441239 | 0.000000    |
| 59      | 20      | Green button pressed - horse released | 2023-10-09 18:19:42.720723 | 89.279484   |
| 60      | 20      | NOGO                                  | 2023-10-09 18:20:42.720777 | 149.279538  |

This complete EventCB table shows all events for all 20 trials in the experiment, including the start of each trial, the button press event, and the final response (GO or NOGO) for each trial.

## Notes

1. TrialCB Table:

This table represents each trial in the experiment.

- TrialID: Unique identifier for each trial, matching TrialNumber in this case.
- ExperimentID: Set to 1 here as a placeholder for all trials, indicating they belong to the same experiment.
- TrialNumber: The sequential number of the trial within the experiment (1-20).
- ResponseType: Either "GO" or "NOGO", indicating the horse's response.
- TrialSubType: "P" for positive trials, "N" for negative trials.
- Direction: Always "LEFT" in this experiment, based on the initial comment.
- CriterionType: "positive" or "negative" for trials that count towards the criterion, NULL for incorrect responses.
- CriterionCount: The cumulative count of correct responses for the given criterion type, NULL for incorrect responses.
- TrialStartTime: Timestamp when the trial began.
- TrialEndTime: Timestamp when the trial ended (when the response was recorded).
- SessionType: Always "Training" in this experiment.

Observations:
- There are 20 trials in total.
- 11 trials are "GO" responses, 9 are "NOGO" responses.
- The experiment alternates between positive (P) and negative (N) trials.
- CriterionCount reaches 10 for positive trials and 7 for negative trials by the end.

2. ResponseCB Table:

This table contains data for "GO" responses only.

- ResponseID: Unique identifier for each response.
- TrialID: Corresponds to the TrialID in the TrialCB table.
- ResponseTime: The time taken for the horse to respond (in seconds).
- EventDateTime: Timestamp when the response was recorded.

Observations:
- There are 13 "GO" responses recorded.
- Response times vary from about 9 to 22 seconds.
- Not all trials have a corresponding entry in this table (only "GO" responses are recorded).

3. EventCB Table:

This table records all events that occur during each trial.

- EventID: Unique identifier for each event.
- TrialID: Corresponds to the TrialID in the TrialCB table.
- EventType: Describes the type of event ("Current Trial", "Green button pressed - horse released", "GO", or "NOGO").
- EventTime: Timestamp when the event occurred.
- ElapsedTime: Time in seconds since the start of the trial.

Observations:
- Each trial has three events: start of trial, button press, and final response (GO or NOGO).
- The "Green button pressed" event represents when the horse was released to make a choice.
- ElapsedTime allows for analysis of timing within each trial.

General Annotations:
1. The experiment consists of 20 trials, alternating between positive and negative stimuli.
2. The session type is "Training" throughout, with both positive and negative criteria being tracked.
3. The direction (LEFT) is consistent across all trials, indicating the position of the positive stimulus.
4. Response times and patterns could be analyzed to study learning progression or fatigue effects.
5. The cumulative criterion counts (reaching 10 for positive and 7 for negative) suggest the experiment ended when a certain performance level was reached.
6. The detailed event timing allows for analysis of decision-making processes within each trial.
