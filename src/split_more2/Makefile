BMV2_SWITCH_EXE = simple_switch_grpc

include ../../utils/Makefile


all: build run

run:
	sudo python3 ../../utils/run_exercise.py -t topology.json -j build/mri.json -b simple_switch_grpc


log_to_elastic_uv:
	uv run background_log_to_elastic.py

log_to_elastic:
	python3 background_log_to_elastic.py