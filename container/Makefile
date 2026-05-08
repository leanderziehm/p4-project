IMAGE_NAME := p4-mininet
CONTAINER_NAME := p4-dev

build:
	sudo podman build -t $(IMAGE_NAME) .

run:
	sudo podman run \
		--rm \
		--replace \
		--privileged \
		--network host \
		-it \
		-v $(shell realpath ../):/p4-project:Z \
		--name $(CONTAINER_NAME) \
		localhost/$(IMAGE_NAME):latest