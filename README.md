# `horse-logic`

This repository contain the code for the behavioural experiments conducted with horses at the Charles Sturt University.

## Experimental control code (RPi)

The code is used to capture data from a range of sensors controlled by a Raspberry Pi. The data is then analysed to determine the latency of the horses' responses to various stimuli.

## Analytics

The repo also includes code to parse the results of the experiments (contained in log files) and to create a (`DuckDB`) database which is then shared on the [MotherDuck](https://motherduck.com) platform.

This is performed using the Jupyter notebooks in the `notebooks` directory. Specifically:

- `notebooks/archive-analysis`
- `notebooks/archive-experiment`
- `notebooks/OCR-tests`

The key Python code is in these notebooks and/or the supporting functions defined in:

- `src/horse_logic/logfiles.py`

### Details

The key notebooks for performing the analysis are:


### Directory structure
