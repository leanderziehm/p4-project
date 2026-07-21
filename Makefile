2 z_final:
	cd src/z_final && make build && make run

split_more2:
	cd src/split_more2 && make build && make run

3 run_elastic:
	cd src/split_more2 && make log_to_elastic_uv

1 main container:
	cd container/p4_mininet && make

# keep this in extra background terminal open
0 sshtmux elastic:
# 	tmux has-session -t ssh-tunnel 2>/dev/null && tmux attach -t ssh-tunnel || tmux new -s ssh-tunnel "ssh -i elastic_server/secret/elasticsearch_ssh_port_tunneling_user.pem -L 0.0.0.0:9200:localhost:9200 -L 0.0.0.0:5601:localhost:5601 ssh_port_tunneling_user@130.162.236.17"
	tmux has-session -t ssh-tunnel 2>/dev/null && tmux attach -t ssh-tunnel || tmux new -s ssh-tunnel "ssh -i elastic_server/secret/elasticsearch_ssh_port_tunneling_user.pem -L 9200:localhost:9200 -L 5601:localhost:5601 ssh_port_tunneling_user@130.162.236.17"

# ssh -i elastic_server/secret/elasticsearch_ssh_port_tunneling_user.pem -L 9200:localhost:9200 -L 5601:localhost:5601 ssh_port_tunneling_user@130.162.236.17
# ssh -i elastic_server/secret/elasticsearch_ssh_port_tunneling_user.pem ssh_port_tunneling_user@130.162.236.17

8 9 basic:
	cd src/basic && make build && make run

mri_clone_working_dev:
	cd src/mri_clone_working_dev && make build && make run

mri_clone:
	cd src/mri_clone && make build && make run
ssh:
	tmux has-session -t ssh-tunnel 2>/dev/null && tmux attach -t ssh-tunnel || tmux new -s ssh-tunnel "ssh -i elastic_server/secret/elasticsearch_ssh_port_tunneling_user.pem -L 9200:localhost:9200 -L 5601:localhost:5601 ssh_port_tunneling_user@130.162.236.17"

# split_more:
# 	cd src/split_more && make build && make run

# # mri_clone:
# # 	cd src/mri_clone && make build && make run
# # 	cd src/mri_clone && tmux has-session -t mri_clone 2>/dev/null && tmux attach -t mri_clone || tmux new -s mri_clone "make build && make run"
# # 	 tmux new -s mri_clone "make build && make run"
# # 	cd src/mri_clone && make build && make run

# final:
# 	cd src/z_final && make build && make run

# split:
# 	cd src/split && make build && make run

# elastic-compose compose:
# 	cd container/elasticsearch && podman compose up
	
# mri_simple:
# 	cd src/mri_simple && make build && make run
# run_aa_clone:
# 	cd src/aa_clone && make build && make run
# run_aa:
# 	cd src/aa && make build && make run

# run_multicast_simple:
# 	cd src/multicast_simple && make build && make run

# run_multicast:
# 	cd src/multicast && make build && make run

# run_basic_clone:
# 	cd src/basic_clone && make build && make run

# run_basic_custom_header:
# 	cd src/basic_custom_header && make build && make run

# run_basic:
# 	cd src/basic && make build && make run

# run_b2:
# 	cd src/b && make build && make run

# run_project:
# 	cd src/project && make build && make go

# mri2:
# 	cd src/mri2 && make build && make run

# run_load_balance:
# 	cd src/load_balance && make build && make run 

# run_linkmonitor:
# 	cd src/link_monitor && make build && make run 

# run_calc:
# 	cd src/calc && make build && make run 

# run_basic4:
# 	cd src/basic4 && make build && make run 


# run_basic3:
# 	cd src/basic3 && make build && make run 

# run_b:
# 	cd src/b && make build && make run 

# run_a:
# 	cd src/a && make build && make run 

# runbasic2:
# 	cd src/basic2 && make build && make run
# rundev:
# 	cd src/dev && make build && make run

# runmri:
# 	cd src/mri && make build && make go

# launch:
# 	cd container && make 

# test:
# 	cd src/project && python3 test1.py

# test3:
# 	cd src/project && pytest -s test_mri.py