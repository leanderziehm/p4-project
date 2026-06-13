runmri:
	cd src/mri && make build && make go

runproject:
	cd src/project && make

launch:
	cd container && make 