#!/usr/bin/env python3
import argparse
import time
from utils.run_exercise import ExerciseRunner

class TrafficManager(ExerciseRunner):
    def run_traffic_scenario(self):
        self.create_network()
        self.net.start()
        time.sleep(1)

        self.program_hosts()
        self.program_switches()
        time.sleep(1)

        # Get references to specific hosts
        h1 = self.net.get('h1')
        h2 = self.net.get('h2')
        h3 = self.net.get('h3')

        # Start a receiver on h2 in the background
        h2.cmd('python3 receive.py &')
        time.sleep(0.5)  # give it a moment to bind

        # Have h1 send to h2
        h1.cmd('python3 send.py --dst 10.0.1.2 --count 100')

        # Have h3 do something else entirely
        h3.cmd('ping -c 5 10.0.1.1')

        # Optionally drop into the CLI afterward to inspect things
        self.do_net_cli()
        self.net.stop()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--topo', default='./topology.json')
    parser.add_argument('-j', '--switch_json', required=False)
    parser.add_argument('-b', '--behavioral-exe', default='simple_switch')
    parser.add_argument('-l', '--log-dir', default='./logs')
    parser.add_argument('-p', '--pcap-dir', default='./pcaps')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    manager = TrafficManager(args.topo, args.log_dir, args.pcap_dir,
                               args.switch_json, args.behavioral_exe)
    manager.run_traffic_scenario()