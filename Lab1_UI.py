import networkx as nx

EDGE_LIST_FILE = "actors_edgelist.csv"
GML_FILE = "actors_graph.gml"

def shortest_path(G):
    print("\n--- Najkrótsza ścieżka ---")
    start = input("Podaj początkowego aktora: \n").strip()
    end = input("Podaj końcowego aktora: \n").strip()
    if start not in G or end not in G:
        print("Nie znaleziono jednego z aktorów w grafie.")
        return
    try:
        path = nx.shortest_path(G, source=start, target=end)
        print(f"Najkrótsza ścieżka między {start} a {end}:")
        print(" -> ".join(path))
        print(f"Długość ścieżki: {len(path)-1}")
    except nx.NetworkXNoPath:
        print("Brak ścieżki między tymi wierzchołkami.")

def eulerian_check(G):
    print("\n--- Sprawdzenie Eulerowskości ---")
    if not nx.is_connected(G):
        largest_cc = max(nx.connected_components(G), key=len)
        G_sub = G.subgraph(largest_cc).copy()
        print(f"Graf nie jest spójny, sprawdzamy największy spójny podgraf ({len(G_sub.nodes())} węzłów).")
    else:
        G_sub = G
    if nx.is_eulerian(G_sub):
        print("Graf (podgraf) jest eulerowski!")
        path = list(nx.eulerian_circuit(G_sub))
        print("Ścieżka Eulerowska (kolejne krawędzie):")
        for u,v in path:
            print(f"{u} -> {v}")
    else:
        print("Graf (podgraf) nie jest eulerowski.")

def max_flow_demo(G):
    print("\n--- Maksymalny przepływ ---")
    DG = nx.DiGraph()
    for u,v,d in G.edges(data=True):
        w = d.get("weight", 1)
        DG.add_edge(u, v, capacity=w)
        DG.add_edge(v, u, capacity=w)

    source = input("Podaj źródłowego aktora: \n").strip()
    target = input("Podaj docelowego aktora: \n").strip()
    if source not in DG or target not in DG:
        print("Nie znaleziono jednego z aktorów w grafie.")
        return
    try:
        flow_value, flow_dict = nx.maximum_flow(DG, source, target)
        print(f"Maksymalny przepływ między {source} a {target}: {flow_value}")
    except nx.NetworkXError as e:
        print("Błąd w obliczaniu przepływu:", e)

def main():
    G = nx.read_gml(GML_FILE)
    while True:
        print("\n--- Menu ---")
        print("1: Najkrótsza ścieżka")
        print("2: Sprawdzenie grafu Eulerowskiego i ścieżka Eulerowska")
        print("3: Maksymalny przepływ")
        print("4: Wyjście")
        choice = input("Wybierz opcję (1-4): \n").strip()
        if choice == "1":
            shortest_path(G)
        elif choice == "2":
            eulerian_check(G)
        elif choice == "3":
            max_flow_demo(G)
        elif choice == "4":
            break
        else:
            print("Niepoprawna opcja.")

if __name__ == "__main__":
    main()
