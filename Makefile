IMAGE_NAME := p4-mininet
CONTAINER_NAME := p4-dev

build:
	sudo podman build -t $(IMAGE_NAME) .

run:
	sudo podman run \
		--rm \
		--privileged \
		--network host \
		-it \
		-v $(PWD):/workspace \
		--name $(CONTAINER_NAME) \
		localhost/$(IMAGE_NAME):latest