import json
import os
import sys
import networkx as nx
import matplotlib.pyplot as plt
def load_topology(json_file):
    with open(json_file, "r") as f:
        return json.load(f)
def parse_endpoint(endpoint):
    """
    Converts:
        h1      -> ("h1", None)
        s1-p2   -> ("s1", "p2")
    """
    if "-p" in endpoint:
        node, port = endpoint.split("-p")
        return node, f"p{port}"
    return endpoint, None
def build_graph(topo):
    G = nx.Graph()
    node_labels = {}
    # Hosts
    for host, info in topo["hosts"].items():
        ip = info.get("ip", "")
        mac = info.get("mac", "")
        G.add_node(
            host,
            node_type="host",
            ip=ip,
            mac=mac
        )
        node_labels[host] = (
            f"{host}\n"
            f"IP: {ip}\n"
            f"MAC: {mac}"
        )
    # Switches
    for sw in topo["switches"]:
        G.add_node(
            sw,
            node_type="switch"
        )
        node_labels[sw] = sw
    # Links
    edge_labels = {}
    for link in topo["links"]:
        a, b = link
        node1, port1 = parse_endpoint(a)
        node2, port2 = parse_endpoint(b)
        G.add_edge(node1, node2)
        edge_labels[(node1, node2)] = (
            port1,
            port2
        )
    return G, node_labels, edge_labels
def draw_topology(
        G,
        node_labels,
        edge_labels,
        output):
    plt.figure(figsize=(12, 8))
    # plt.figure(figsize=(8, 5))
    pos = nx.spring_layout(
        G,
        seed=5,
        #  k=0.1    
    )
    hosts = [
        n for n, d in G.nodes(data=True)
        if d["node_type"] == "host"
    ]
    switches = [
        n for n, d in G.nodes(data=True)
        if d["node_type"] == "switch"
    ]
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=hosts,
        node_color="#8fd3ff",
        node_shape="o",
        node_size=2600
    )
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=switches,
        node_color="#ffcc66",
        node_shape="s",
        node_size=2600
    )
    nx.draw_networkx_edges(
        G,
        pos,
        width=2
    )
    nx.draw_networkx_labels(
        G,
        pos,
        labels=node_labels,
        font_size=8,
        font_weight="bold"
    )
    # Port labels
    for (u, v), (port_u, port_v) in edge_labels.items():
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        if port_u:
            plt.text(
                x1 * 0.8 + x2 * 0.2,
                y1 * 0.8 + y2 * 0.2,
                port_u,
                fontsize=8,
                color="red",
                bbox=dict(
                    facecolor="white",
                    alpha=0.8,
                    edgecolor="none"
                )
            )
        if port_v:
            plt.text(
                x1 * 0.2 + x2 * 0.8,
                y1 * 0.2 + y2 * 0.8,
                port_v,
                fontsize=8,
                color="red",
                bbox=dict(
                    facecolor="white",
                    alpha=0.8,
                    edgecolor="none"
                )
            )
    plt.title("Network Topology")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(
        output,
        dpi=300,
        bbox_inches="tight"
    )
    plt.show()
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python draw_topology.py <topology.json>"
        )
        sys.exit(1)
    topology_file = sys.argv[1]
    if not os.path.isfile(topology_file):
        print(
            f"File not found: {topology_file}"
        )
        sys.exit(1)
    topo = load_topology(topology_file)
    G, node_labels, edge_labels = build_graph(topo)
    # Save PNG next to topology.json
    folder = os.path.dirname(
        os.path.abspath(topology_file)
    )
    output_file = os.path.join(
        folder,
        "topology.png"
    )
    draw_topology(
        G,
        node_labels,
        edge_labels,
        output_file
    )
    print(
        f"Topology image saved to: {output_file}"
    )