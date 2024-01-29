# https://just.systems/

default:
  @just --list

# Docker containers on macOS
# brew install --cask docker

# Define default values for parameters

image_name := "app"
tag := "latest"
container_name := "app_container"
host_port := "8000"
container_port := "8000"
dockerfile := "Dockerfile"
build_context := "."

# Commands

# Example (with specified parameters):
#
# just build image_name=my_app tag=v1

build:
    docker build -t {{image_name}}:{{tag}} -f {{dockerfile}} {{build_context}}

run:
    docker run --name {{container_name}} -p {{host_port}}:{{container_port}} -d {{image_name}}:{{tag}}

stop:
    docker stop {{container_name}}

remove:
    docker rm {{container_name}}

logs:
    docker logs {{container_name}}

shell:
    docker exec -it {{container_name}} /bin/sh

push:
    docker push {{image_name}}:{{tag}}

pull:
    docker pull {{image_name}}:{{tag}}
