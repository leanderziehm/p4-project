IMAGE_NAME := p4-mininet
CONTAINER_NAME := p4-dev

all: build run 

build:
	sudo podman build -t $(IMAGE_NAME) .

run:
	sudo podman run \
		--rm \
		--replace \
		--privileged \
		--network host \
		-it \
		-v $(shell git rev-parse --show-toplevel):/p4-project:Z \
		--name $(CONTAINER_NAME) \
		localhost/$(IMAGE_NAME):latest

mininet:
	sudo podman exec -it <container_name> mnexec h1 bash
	sudo podman exec -it <container_name> mnexec h2 bash


x:
	-e DISPLAY=$DISPLAY \
	-v /tmp/.X11-unix:/tmp/.X11-unix \