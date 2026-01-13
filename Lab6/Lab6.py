import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import os

# Lista plików
BOOK_FILES = [f"book{i}.csv" for i in range(1, 6)]
OUTPUT_HTML = "got_full_saga.html"


def load_and_merge_books(files):
    """
    Wczytuje 5 plików CSV i łączy je w jeden graf.
    Jeśli krawędź istnieje w kilku książkach, sumujemy jej wagę.
    """
    print("--- 1. ETL: Wczytywanie i łączenie danych ---")
    G = nx.Graph()

    for fname in files:
        if not os.path.exists(fname):
            print(f"Ostrzeżenie: Brak pliku {fname}, pomijam.")
            continue

        print(f"Przetwarzanie {fname}...")
        df = pd.read_csv(fname)

        # Kolumny: Source, Target, Type, weight, book
        for _, row in df.iterrows():
            src = str(row['Source']).strip()
            tgt = str(row['Target']).strip()
            # Zabezpieczenie na wypadek braku wagi
            try:
                w = float(row['weight'])
            except (ValueError, KeyError):
                w = 1.0

            if G.has_edge(src, tgt):
                G[src][tgt]['weight'] += w
            else:
                G.add_edge(src, tgt, weight=w)

    print(f"\nStworzono 'Super-Graf' całej sagi:")
    print(f"Liczba węzłów (postaci): {G.number_of_nodes()}")
    print(f"Liczba krawędzi (relacji): {G.number_of_edges()}")
    return G


def analyze_properties(G):
    """Oblicza ogólne metryki sieci do raportu."""
    print("\n--- 2. ANALIZA MAKRO (Właściwości sieci) ---")

    density = nx.density(G)
    print(f"Gęstość sieci: {density:.5f} (Stosunkowo rzadka, co typowe dla sieci społecznych)")

    if nx.is_connected(G):
        print("Sieć jest spójna (każdy może dojść do każdego).")
        diam = nx.diameter(G)
        avg_path = nx.average_shortest_path_length(G)
        print(f"Średnica sieci (najdłuższa najkrótsza ścieżka): {diam}")
        print(f"Średnia długość ścieżki (efekt małego świata): {avg_path:.2f}")
    else:
        print("Sieć NIE jest spójna (są izolowane wyspy).")
        largest_cc = max(nx.connected_components(G), key=len)
        S = G.subgraph(largest_cc)
        print(f"Analiza największej spójnej składowej ({len(S)} węzłów):")
        print(f" - Średnica: {nx.diameter(S)}")
        print(f" - Średnia długość ścieżki: {nx.average_shortest_path_length(S):.2f}")

    clustering = nx.average_clustering(G)
    print(f"Współczynnik klastrowania (Average Clustering): {clustering:.4f}")
    print(" (Wysoki współczynnik oznacza, że znajomi moich znajomych często są moimi znajomymi - tworzą się grupy)")


def analyze_centrality(G):
    """Znajduje najważniejsze postacie (Huby i Mosty)."""
    print("\n--- 3. ANALIZA MIKRO (Huby i Mosty) ---")

    # Degree Centrality (ważony)
    degree_dict = dict(G.degree(weight='weight'))
    sorted_degree = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)

    print("\nTOP 5 - Najważniejsi bohaterowie (Weighted Degree - siła relacji):")
    for i, (node, val) in enumerate(sorted_degree[:5], 1):
        print(f"{i}. {node} (Waga relacji: {int(val)})")

    # Betweenness Centrality
    print("\nTOP 5 - Najważniejsi pośrednicy (Betweenness - kontrola przepływu):")
    betweenness = nx.betweenness_centrality(G, weight='weight')
    sorted_bet = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)

    for i, (node, val) in enumerate(sorted_bet[:5], 1):
        print(f"{i}. {node} ({val:.4f})")


def analyze_cliques(G):
    """Znajduje największą grupę, gdzie każdy zna każdego."""
    print("\n--- 4. KLIKI (Grupy) ---")

    cliques = list(nx.find_cliques(G))
    largest_clique = max(cliques, key=len)

    print(f"Liczba wszystkich klik w sieci: {len(cliques)}")
    print(f"Rozmiar największej kliki: {len(largest_clique)}")
    print(f"Członkowie największej kliki: {', '.join(largest_clique)}")
    print(" (To grupa postaci, które w całej sadze wystąpiły ze sobą nawzajem chociaż raz)")


def visualize_network(G, output_file):
    """Tworzy interaktywny plik HTML."""
    print(f"\n--- 5. WIZUALIZACJA ---")
    print(f"Generowanie pliku {output_file}...")

    # POPRAWKA: Usunięto 'select_menu=True', które powodowało błąd
    net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white")

    # Opcjonalnie: Dodanie panelu sterowania fizyką (zastępuje select_menu)
    # net.show_buttons(filter_=['physics'])

    THRESHOLD = 5
    print(f"Filtrowanie wizualizacji: Pokazuję tylko krawędzie o wadze >= {THRESHOLD}")

    vis_G = nx.Graph()

    for u, v, data in G.edges(data=True):
        if data['weight'] >= THRESHOLD:
            vis_G.add_edge(u, v, weight=data['weight'])

    degree_dict = dict(G.degree(weight='weight'))
    for node in vis_G.nodes():
        size = degree_dict.get(node, 1) / 10
        net.add_node(node, label=node, size=size, title=f"Waga: {int(degree_dict.get(node, 0))}")

    for u, v, data in vis_G.edges(data=True):
        net.add_edge(u, v, value=data['weight'], title=f"Wspólne wystąpienia: {int(data['weight'])}")

    net.barnes_hut(gravity=-2000, central_gravity=0.3, spring_length=200)

    # Zapisz plik
    net.save_graph(output_file)
    print(f"Gotowe! Otwórz plik '{output_file}' w przeglądarce.")


def main():
    G = load_and_merge_books(BOOK_FILES)

    if G.number_of_nodes() == 0:
        print("Błąd: Pusty graf. Sprawdź pliki CSV.")
        return

    analyze_properties(G)
    analyze_centrality(G)
    analyze_cliques(G)
    visualize_network(G, OUTPUT_HTML)


if __name__ == "__main__":
    main()