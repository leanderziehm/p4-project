run_a:
	cd src/a && make build && make run 

main container:
	cd container/p4_mininet && make

runbasic2:
	cd src/basic2 && make build && make run
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