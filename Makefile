runmri:
	cd src/mri && make && make go

runproject:
	cd src/project && make

launch:
	cd container && make 