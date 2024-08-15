Update from CH - 14 August 2023

We did ... the pilot with horses but didn’t capture any useful latency data because focussed on working out the logistics of what we were doing - where to lead horse, where to focus cameras etc.

So attached is made up data but designed to reflect likely types of responding for the two halves of the experiment.

The cog bias tab is the choice between the positive (food) and negative (gravel) buckets.  This is training data only - not test data - eg where they have to choose between the pos/neg and ambiguous positions.  I will create that a bit later in the week ...

I have deliberately created three types of horse responses based on what we observed in the pilot:
- a horse in a neutral mood (horse 1),
- a real optimist (horse 2) learns quickly about the baited bucket but learns slowly to stop responding to the negative bucket (contains gravel) and
- a pessimist horse (horse 3) learns slowly about the baited bucket but quickly learns to stop responding to the gravel bucket.

The criterion is to respond to the positive bucket within 30s of being released and to not respond (stay stationary) for 30s when released when the bucket is in the negative position.

The RPE data is for the second half of the experiment where the horses hear the tone, touch the device with their noses and then get the food reward.  I haven’t included the extinction data (where no food reward is given) because again, need to get my head around what it would likely look like.  I have not yet written the code (i.e. copied it from chat GPT) to run the device during the extinction phase.

I did include some delays and basic data logging into the code (attached) but then shorted out the SD card while handling the powered Rpi and had to start again and no I had not put the new code into GitHub.  Luckily I did have copies of the original so was able to reinstall the OS and start again.

So might be good to maybe have a Zoom and I can talk you through where it is all up to.

Am definitely going through basic trial and error learning experience with this project. ... I am wanting to move away from the electronic buzzer to computer generated tones that are played through speakers because the buzzer is not loud enough when it is windy.  And I am adding a sort of wireless remote control to operate it if the touch sensor stops working (which it does a lot when the horses are involved).  I got a manually button version kind of working and then lost the code due to the shorting issue... I am not at all confident in coding the electronic tones ...

So in terms of the code, would need something to log the same variables - e.g. time of start, time of “touch”, (which would be manually triggered by the remote), length of trial etc.

See attached link to footage of device working perfectly for the first time before I broke it.

### Attached files (with renaming):
- SampleData.xlsx
- 1Button_manual_testcode.py.zip
- 8buzzer_testcode_with_delay_timelog.py.zip

### Links:
- Footage of trial experiment #1: https://ln5.sync.com/dl/c14b08cd0/asyyfuhy-jseaaz9x-4xbusjj9-mkvfitvz
- Footage #2 (Test Freckle 4 Sept edited.mov - 4 September 2023): https://ln5.sync.com/dl/41220c530/y4zgpdq5-3hr34wcd-w7pr2q86-k648sk2u
