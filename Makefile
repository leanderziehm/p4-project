rundev:
	cd src/dev && make build && make run

elastic:
	cd container/elasticsearch && podman compose up
	
runproject:
	cd src/project && make build && make go

runmri:
	cd src/mri && make build && make go

launch:
	cd container && make 


test:
	cd src/project && python3 test1.py

test3:
	cd src/project && pytest -s test_mri.py