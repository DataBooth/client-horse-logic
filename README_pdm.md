# PDM Commands

[https://pdm.fming.dev/latest/](https://pdm.fming.dev/latest/)

## Initialise PDM in the repo

`pdm init`

## Add dependencies

`pdm add PACKAGE_NAME`

## Install / update

`pdm update`

## Export the production requirements

`pdm export --o requirements.txt --without-hashes --prod`

## Publishing

pdm config repository.testpypi.url https://test.pypi.org/simple
pdm config repository.testpypi.username <username>
pdm config repository.testpypi.password <api-token>
pdm publish -r testpypi
