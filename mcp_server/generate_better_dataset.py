"""
Script per generare un dataset con overlap garantito tra utenti
Ogni coppia di utenti ha almeno 3 film in comune O nessuno
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Seed per riproducibilità
np.random.seed(42)

# Lista di 100 film popolari
MOVIES = [
    "Il Padrino", "Pulp Fiction", "Il Cavaliere Oscuro", "Inception", 
    "Forrest Gump", "Matrix", "Interstellar", "Il Signore degli Anelli",
    "Star Wars", "Titanic", "Avatar", "Avengers", "Joker", "Parasite",
    "La La Land", "Oppenheimer", "Barbie", "Dune", "Spider-Man",
    "Il Grande Gatsby", "The Social Network", "Whiplash", "Coco",
    "Inside Out", "Toy Story", "Il Re Leone", "Frozen", "Gladiatore",
    "Il Silenzio degli Innocenti", "Fight Club", "Salvate il Soldato Ryan",
    "Schindler's List", "The Prestige", "Memento", "Django Unchained",
    "Kill Bill", "Bastardi Senza Gloria", "The Wolf of Wall Street",
    "The Revenant", "Birdman", "Grand Budapest Hotel", "Moonlight",
    "Get Out", "Arrival", "Blade Runner 2049", "Mad Max Fury Road",
    "1917", "Dunkirk", "Tenet", "Everything Everywhere All at Once",
    "Shawshank Redemption", "Il Buono il Brutto il Cattivo", "12 Angry Men",
    "La Vita è Bella", "Se7en", "The Usual Suspects", "Casablanca",
    "Il Miglio Verde", "City of God", "Rear Window", "Psycho", "Aliens",
    "Back to the Future", "Apocalypse Now", "Indiana Jones", "E.T.",
    "2001 Odissea nello Spazio", "Vertigo", "Witness for the Prosecution",
    "Rashomon", "Lawrence d'Arabia", "Metropolis", "Shining", "Alien",
    "Citizen Kane", "Taxi Driver", "Nuovo Cinema Paradiso", "Once Upon a Time in America",
    "Les Misérables", "Amadeus", "The Pianist", "Requiem for a Dream",
    "Eternal Sunshine", "American History X", "Terminator 2", "Die Hard",
    "The Departed", "No Country for Old Men", "There Will Be Blood",
    "Zodiac", "Gone Girl", "Prisoners", "Sicario", "Nightcrawler",
    "La Forma dell'Acqua", "Roma", "The Irishman", "Marriage Story",
    "Jojo Rabbit", "Knives Out", "Ford v Ferrari", "Soul", "The Batman"
]

n_users = 20
n_movies = len(MOVIES)

# Strategia: creare "cluster" di utenti che guardano film simili
# Cluster 1: Film d'azione/fantascienza (utenti 1-7)
# Cluster 2: Film drammatici/classici (utenti 8-14)
# Cluster 3: Film moderni/indie (utenti 15-20)

clusters = {
    'action': list(range(1, 8)),      # Users 1-7
    'drama': list(range(8, 15)),      # Users 8-14
    'indie': list(range(15, 21))      # Users 15-20
}

# Film per cluster (indici)
cluster_movies = {
    'action': list(range(0, 35)),     # Primi 35 film
    'drama': list(range(20, 60)),     # Film 20-60 (overlap con action)
    'indie': list(range(40, 95))      # Film 40-95 (overlap con drama)
}

data = []

for cluster_name, users in clusters.items():
    available_movies = cluster_movies[cluster_name]
    
    # Film "core" del cluster che TUTTI gli utenti vedono (per garantire overlap)
    core_movies = np.random.choice(available_movies, size=20, replace=False)
    
    for user_id in users:
        # Ogni utente vota i film core
        for movie_idx in core_movies:
            rating = np.random.choice([3.0, 4.0, 5.0], p=[0.2, 0.4, 0.4])
            data.append({
                'user_id': user_id,
                'item_id': 101 + movie_idx,
                'rating': rating
            })
        
        # Aggiungi film casuali dal cluster (3-8 film)
        n_extra = np.random.randint(3, 9)
        extra_movies = np.random.choice(
            [m for m in available_movies if m not in core_movies],
            size=min(n_extra, len(available_movies) - 20),
            replace=False
        )
        
        for movie_idx in extra_movies:
            rating = np.random.choice([1.0, 2.0, 3.0, 4.0, 5.0], 
                                     p=[0.05, 0.1, 0.25, 0.35, 0.25])
            data.append({
                'user_id': user_id,
                'item_id': 101 + movie_idx,
                'rating': rating
            })

# Crea DataFrame
df = pd.DataFrame(data)
df = df.drop_duplicates(subset=['user_id', 'item_id'])
df = df.sort_values(['user_id', 'item_id']).reset_index(drop=True)

# Verifica l'overlap
print("=" * 70)
print("VERIFICA OVERLAP TRA UTENTI")
print("=" * 70)

from itertools import combinations

user_pairs = list(combinations(range(1, n_users + 1), 2))
overlap_stats = []

for u1, u2 in user_pairs:
    u1_items = set(df[df['user_id'] == u1]['item_id'])
    u2_items = set(df[df['user_id'] == u2]['item_id'])
    common = len(u1_items & u2_items)
    
    if common > 0:
        overlap_stats.append(common)
        if common < 3:
            print(f"  User {u1} e User {u2}: solo {common} film in comune")

if overlap_stats:
    print(f"\n Overlap medio: {np.mean(overlap_stats):.1f} film")
    print(f" Overlap minimo: {min(overlap_stats)} film")
    print(f" Overlap massimo: {max(overlap_stats)} film")
else:
    print("\n Nessun overlap tra utenti di cluster diversi")

# Salva i file
output_path = Path(__file__).parent.parent / "data" / "ratings.csv"
df.to_csv(output_path, index=False)

movies_df = pd.DataFrame({
    'item_id': range(101, 101 + len(MOVIES)),
    'title': MOVIES
})
movies_path = Path(__file__).parent.parent / "data" / "movies.csv"
movies_df.to_csv(movies_path, index=False)

print(f"\n{'=' * 70}")
print(f" Dataset generato: {len(df)} ratings")
print(f"   - Utenti: {df['user_id'].nunique()}")
print(f"   - Film: {df['item_id'].nunique()}")
print(f"   - Rating medio: {df['rating'].mean():.2f}")
print(f"   - Salvato in: {output_path}")
print(f"   - Mappatura film salvata in: {movies_path}")
print(f"\n[STATS] Distribuzione ratings:")
print(df['rating'].value_counts().sort_index())
