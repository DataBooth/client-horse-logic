## Installing Python

I highly recommend the [`pyenv`](https://github.com/pyenv/pyenv) tool to manage your Python install/version.

e.g. On macOS it can be [`brew`](https://brew.sh)-installed i.e.

```
brew install pyenv
```

## Python Package Manager (PDM)

The package manager I usually use is [`pdm`](https://pdm-project.org/en/latest/). There are others and/or
you can install the packages using the standard Python `pip` installer. See below for PDM commands.

Otherwise use the standard Python tools.

## `pip` and `venv` tools

If you decide not to use a package mananger (which hides away most of the following), I highly recommend working within a (Python) virtual environment for reproducibility. `venv` is the built-in Python tool for setting this up.

```
python -m venv .venv
```
where here `.venv` is the name of your virtual environment (it is a choice but I try and keep it standard). It
is activated with:
```
source .venv/bin/activate
```
on Unix/Linux/macOS/RPi (search the internet or ask Copilot for Windows installs.)

Once a `venv` has been setup, to install all of the packages you do:

```
pip install -r requirements.txt
```

## PDM Commands

If not using the standard Python tools, here are some PDM commands.

[https://pdm.fming.dev/latest/](https://pdm.fming.dev/latest/)

### Initialise PDM in the repo

`pdm init`

### Add dependencies

`pdm add PACKAGE_NAME`

### Install / update packages

`pdm update`

### Export the production requirements.txt

`pdm export --o requirements.txt --without-hashes --prod`
