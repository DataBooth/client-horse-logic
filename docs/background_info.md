## Initial chat

CH: Cath Henshall
MB: Michael Booth

### What is the problem you are trying to solve?

- Un-yet built device for capturing a specific horse behaviours
- Sensor data - measure latency between trials and other metrics
- Potentially use Raspberry Pi and/or PC/Matlab to interface with sensors
- Need to start data collection in August
- UK collaborators — understand hardware piece
- Might go with touch screen solution (probably not)
- IR sensors don't work well :(
- Remote control - button - signal (human in the loop) - not ideal
- Prefer fully automated data collection

### Where are you doing the experiments?

- Wagga Wagga (onsite)
- Sensors and collection device with be co-located and mains power available
- Sensor on a fence and device directly connected

### Other

- Talked about potential of Python in Google Colab environment (freely available)
- Could also demo/show you remotely what this looks like

### Actions

- CH: Investigate Matlab license fees (is it available under University license or additional charge)
- CH: Send video to of manual experiment
- MB: Look at how sensor data <--> Raspberry Pi / Python typically work together

### Follow-up questions / answers

1. How long will each experiment last (duration) e.g. minutes, hours, days?

Each session will be about 10 minutes per horse, 20 horses, x 1 session a day, x probably 7 days total.

2. Do you want to keep a record of each run (even if it "fails”)? What about if power fails (e.g. have a partial record)?

Hadn't thought about power failure - will think about that.  We will want to collect correct responses and the latency between the correct responses.  Am thinking we will need a "go" signal-probably a noise, then measure the time between that and a correct response.  Then a set period of time out, then go signal again and commencement of trial.  So recording the latency between go signal and beginning of time out period, or between go signals.

3. How frequently (typically) will each observation occur? How many sensors / components to each observation (same timestamp?).

4. What are the details of the hardware interface (when available)?

   See YouTube video - https://youtu.be/-wm05ODt2XA

5. How many data points per second (per sensor) do you expect to collect? i.e. estimate of data size per experiment.

Not sure.  I expect it will be that once the touch sensor is triggered, that will start a time out period where no further presses would be registered.  Then after the time period has elapsed, the next touch would be registered and so on

6. Where will the data be stored? (e.g. first local disk, then Cloud, etc.).

Local drive/usb then cloud

7. Will the Raspberry Pi be connected to the internet?

Not sure - will check

8.  What storage will be available on the device? (e.g. SD card, SSD USB drive etc.)

Not sure - will check

9.  How will the data be transferred from the device to the storage location? (e.g. USB, network, etc.).

Cloud upload

10. Will WiFi be available at the site?

Not sure - will check next week when I am in Wagga

11. Do you have a GitHub account? (or similar). No, but Rob does.

12. Do you have a Google account? (for Google Colab and Drive). Yes

13. What type of sensor(s) will be used? Do they produce a digital or analog signals?  Not sure yet, will find out.

14. What do you want to do with the data after it is collected? (e.g. analysis, visualisation, etc.).

Both, graph it, analyse it probably in SPSS.  Will hope to use mixed model logistic regression in SPSS or perhaps in R with horse as random factor, session fixed factor/effect and latency or correct response as the dependant variable.

15. Is any data processing required before storage? (e.g. filtering, etc.)

Not sure

16. Any real-time processing required? (e.g. feedback to sensors, etc.)

Maybe

17. How many horses are involved in the experiment? Is it a separate experiment for each horse?

There  will be 20 subjects.  All subjects will do the same training.  We are not sure yet whether we go with a fixed number of trials or trials to criteria.

## Additional questions

1. Will the experiments also be recorded (video)?
2. Will the experiments be conducted in a controlled environment (e.g. indoors)?
3. Recording of prevailing (weather) conditions? e.g. Barometric pressure, temperature, humidity, wind speed, wind direction, etc.
4. Use of local devices (or BoM API)? e.g. https://github.com/tonyallan/weather-au
5. Wagga-Wagga weather: http://www.bom.gov.au/places/nsw/wagga-wagga/ (there are also historical records available)
