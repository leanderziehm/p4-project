run_b:
	cd src/b && make build && make run


run_project:
	cd src/project && make build && make go

mri2:
	cd src/mri2 && make build && make run



run_load_balance:
	cd src/load_balance && make build && make run 


run_linkmonitor:
	cd src/link_monitor && make build && make run 

run_calc:
	cd src/calc && make build && make run 

run_basic4:
	cd src/basic4 && make build && make run 


run_basic3:
	cd src/basic3 && make build && make run 


run_b:
	cd src/b && make build && make run 

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
	



runmri:
	cd src/mri && make build && make go

launch:
	cd container && make 


test:
	cd src/project && python3 test1.py

test3:
	cd src/project && pytest -s test_mri.py