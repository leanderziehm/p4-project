import json
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

    # Store node labels
    node_labels = {}

    # Hosts
    for host, info in topo["hosts"].items():
        ip = info["ip"]
        G.add_node(host, node_type="host", ip=ip)

        node_labels[host] = f"{host}\n{ip}"

    # Switches
    for sw in topo["switches"]:
        G.add_node(sw, node_type="switch")
        node_labels[sw] = sw

    # Links
    edge_labels = {}

    for link in topo["links"]:
        a, b = link[0], link[1]

        node1, port1 = parse_endpoint(a)
        node2, port2 = parse_endpoint(b)

        G.add_edge(node1, node2)

        # Save port labels for each endpoint
        edge_labels[(node1, node2)] = (port1, port2)

    return G, node_labels, edge_labels


def draw_topology(G, node_labels, edge_labels,
                  output="a.png"):

    plt.figure(figsize=(10, 7))

    pos = nx.spring_layout(G, seed=5)

    hosts = [n for n, d in G.nodes(data=True)
             if d["node_type"] == "host"]

    switches = [n for n, d in G.nodes(data=True)
                if d["node_type"] == "switch"]

    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=hosts,
        node_color="#8fd3ff",
        node_shape="o",
        node_size=1800
    )

    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=switches,
        node_color="#ffcc66",
        node_shape="s",
        node_size=2200
    )

    nx.draw_networkx_edges(G, pos, width=2)

    nx.draw_networkx_labels(
        G,
        pos,
        labels=node_labels,
        font_size=9,
        font_weight="bold"
    )

    # Draw port labels near each end of the link
    for (u, v), (port_u, port_v) in edge_labels.items():

        x1, y1 = pos[u]
        x2, y2 = pos[v]

        # 20% from u
        if port_u:
            plt.text(
                x1 * 0.8 + x2 * 0.2,
                y1 * 0.8 + y2 * 0.2,
                port_u,
                fontsize=8,
                color="red",
                bbox=dict(facecolor="white", alpha=0.7, edgecolor="none")
            )

        # 20% from v
        if port_v:
            plt.text(
                x1 * 0.2 + x2 * 0.8,
                y1 * 0.2 + y2 * 0.8,
                port_v,
                fontsize=8,
                color="red",
                bbox=dict(facecolor="white", alpha=0.7, edgecolor="none")
            )

    plt.title("Network Topology")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output, dpi=300)
    plt.show()


if __name__ == "__main__":

    topo = load_topology("src/basic/simple-topo/topology.json")

    G, node_labels, edge_labels = build_graph(topo)

    draw_topology(G, node_labels, edge_labels)