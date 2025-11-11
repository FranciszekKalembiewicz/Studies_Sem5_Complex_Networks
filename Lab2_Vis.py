import os
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from pyvis.network import Network

# ---------- CONFIG ----------
EDGE_LIST_CSV = "actors_edgelist.csv"
GRAPH_GML = "actors_graph.gml"
OUTPUT_GML_SMALL = "actors_graph_small.gml"
OUTPUT_ADJ_CSV = "actors_adjacency.csv"
OUTPUT_INC_CSV = "actors_incidence.csv"
PYVIS_HTML = "actors_pyvis.html"

N_NODES = 200        # docelowa liczba wierzchołków (100-500)
MAX_EDGES = 200      # maksymalna liczba krawędzi (<200 wymagane przez zadanie)
LABEL_DEGREE_THRESHOLD = 2  # pokazuj etykiety tylko dla węzłów o deg >= progu
# ----------------------------

def load_graph():
    if os.path.exists(GRAPH_GML):
        G = nx.read_gml(GRAPH_GML)
        return G.to_undirected() if G.is_directed() else G
    if os.path.exists(EDGE_LIST_CSV):
        df = pd.read_csv(EDGE_LIST_CSV)
        cols = [c.lower() for c in df.columns]
        a1 = df.columns[cols.index("actor1")] if "actor1" in cols else df.columns[0]
        a2 = df.columns[cols.index("actor2")] if "actor2" in cols else df.columns[1]
        wcol = None
        if "weight" in cols:
            wcol = df.columns[cols.index("weight")]
        elif len(df.columns) > 2:
            wcol = df.columns[2]
        G = nx.Graph()
        if wcol is None:
            for _, r in df.iterrows():
                G.add_edge(str(r[a1]), str(r[a2]), weight=1.0)
        else:
            for _, r in df.iterrows():
                try:
                    w = float(r[wcol])
                except Exception:
                    w = 1.0
                G.add_edge(str(r[a1]), str(r[a2]), weight=w)
        return G
    raise FileNotFoundError("Brak actors_graph.gml i actors_edgelist.csv w katalogu.")

def reduce_by_degree_and_prune_edges(G, n_nodes=N_NODES, max_edges=MAX_EDGES):
    # wybierz top-n węzłów po stopniu
    if G.number_of_nodes() > n_nodes:
        nodes_sorted = sorted(G.degree(), key=lambda x: x[1], reverse=True)
        top_nodes = [node for node, _ in nodes_sorted[:n_nodes]]
        Gs = G.subgraph(top_nodes).copy()
    else:
        Gs = G.copy()

    # jeżeli zbyt dużo krawędzi -> zachowaj najsilniejsze (wg weight lub alternatywnie wg sumy stopni)
    if Gs.number_of_edges() > max_edges:
        edges_with_score = []
        for u, v, d in Gs.edges(data=True):
            w = d.get("weight", None)
            if w is None:
                # fallback: prefer edges łączące węzły o większym stopniu
                score = Gs.degree(u) + Gs.degree(v)
            else:
                score = float(w)
            edges_with_score.append(((u, v), score))
        edges_with_score.sort(key=lambda x: x[1], reverse=True)
        keep_edges = [e for e, _ in edges_with_score[:max_edges]]

        Gpr = nx.Graph()
        # dodaj tylko węzły, które występują w zachowanych krawędziach
        nodes_to_keep = set()
        for u, v in keep_edges:
            nodes_to_keep.add(u); nodes_to_keep.add(v)
        Gpr.add_nodes_from([(n, Gs.nodes[n]) for n in nodes_to_keep])
        for u, v in keep_edges:
            if Gs.has_edge(u, v):
                Gpr.add_edge(u, v, **Gs.edges[u, v])
        # usuń izolaty (na wszelki wypadek)
        isolates = list(nx.isolates(Gpr))
        if isolates:
            Gpr.remove_nodes_from(isolates)
        nx.write_gml(Gpr, OUTPUT_GML_SMALL)
        print(f"Przycięto krawędzie do {Gpr.number_of_edges()} i zapisano: {OUTPUT_GML_SMALL}")
        return Gpr
    else:
        nx.write_gml(Gs, OUTPUT_GML_SMALL)
        print(f"Zapisano: {OUTPUT_GML_SMALL} ({Gs.number_of_nodes()} węzłów, {Gs.number_of_edges()} krawędzi)")
        return Gs

def save_matrices(G):
    # macierz sąsiedztwa (0/1)
    adj = nx.to_pandas_adjacency(G, dtype=int, weight=None)
    adj.to_csv(OUTPUT_ADJ_CSV)
    # macierz incydencji
    inc = nx.incidence_matrix(G, oriented=False).todense()
    inc_df = pd.DataFrame(inc, index=list(G.nodes()), columns=[f"{u}-{v}" for u, v in G.edges()])
    inc_df.to_csv(OUTPUT_INC_CSV)
    print(f"Zapisano macierz sąsiedztwa: {OUTPUT_ADJ_CSV} i incydencji: {OUTPUT_INC_CSV}")

def viz_nx(G, figsize=(22,18), use_kamada=False):
    plt.figure(figsize=figsize)
    if use_kamada:
        pos = nx.kamada_kawai_layout(G, scale=30)
    else:
        # ekstremalne rozciągnięcie: duże k, dużo iteracji
        pos = nx.spring_layout(G, seed=42, k=30.0, iterations=3000)

    deg = dict(G.degree())
    node_sizes = [120 + deg[nn] * 120 for nn in G.nodes()]

    weights = nx.get_edge_attributes(G, "weight")
    if weights:
        max_w = max(weights.values())
        widths = [0.2 + 3.5 * (weights.get((u, v), weights.get((v, u), 1.0)) / max_w) for u, v in G.edges()]
    else:
        widths = 0.6

    nx.draw_networkx_edges(G, pos, alpha=0.18, width=widths)
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color="skyblue", edgecolors="k", linewidths=0.25)

    # etykiety tylko dla ważnych węzłów (próg)
    labels = {n: str(n) for n in G.nodes() if deg[n] >= LABEL_DEGREE_THRESHOLD}
    offset_pos = {n: (x + 0.08, y + 0.08) for n, (x, y) in pos.items() if n in labels}
    nx.draw_networkx_labels(G, offset_pos, labels, font_size=9,
                            bbox=dict(facecolor="white", edgecolor="none", alpha=0.9, boxstyle="round,pad=0.12"))
    plt.axis("off")
    plt.tight_layout()
    plt.show()

def viz_pyvis(G, height="900px", width="100%", physics=True):
    net = Network(height=height, width=width, directed=False)
    for n in G.nodes():
        label = str(n) if G.degree(n) >= LABEL_DEGREE_THRESHOLD else ""
        net.add_node(n, label=label, title=f"deg:{G.degree(n)}", value=G.degree(n))
    for u, v, d in G.edges(data=True):
        net.add_edge(u, v, value=d.get("weight", 1.0), title=f"w:{d.get('weight',1.0)}")

    if physics:
        # mocne odpychanie i dłuższe sprężyny by rozsunąć węzły
        net.barnes_hut(gravity=-30000, central_gravity=0.01, spring_length=300, spring_strength=0.01, damping=0.09)
        net.set_options("""
        var options = {
          "physics": {
            "enabled": true,
            "barnesHut": {
              "gravitationalConstant": -25000,
              "centralGravity": 0.01,
              "springLength": 300,
              "springConstant": 0.005,
              "damping": 0.09,
              "avoidOverlap": 1
            }
          }
        }
        """)
    else:
        net.toggle_physics(False)

    net.show(PYVIS_HTML)
    print(f"Zapisano interaktywną wizualizację: {PYVIS_HTML}")

def main():
    G = load_graph()
    print(f"Oryginał: {G.number_of_nodes()} węzłów, {G.number_of_edges()} krawędzi")
    G_small = reduce_by_degree_and_prune_edges(G, n_nodes=N_NODES, max_edges=MAX_EDGES)
    save_matrices(G_small)
    viz_nx(G_small)
    viz_pyvis(G_small)

if __name__ == "__main__":
    main()
