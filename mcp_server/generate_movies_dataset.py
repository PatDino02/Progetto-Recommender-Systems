"""
Script per generare un dataset di SOLI FILM per il recommender system
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
    # Altri 50 film
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

# Parametri del dataset
n_users = 20
n_ratings = 300  # Più ratings per avere dati più ricchi

# Genera ratings con pattern più realistici
data = []
for user_id in range(1, n_users + 1):
    # Ogni utente vota tra 10 e 20 film casuali
    n_user_ratings = np.random.randint(10, 21)
    
    # Seleziona film casuali
    user_movies = np.random.choice(len(MOVIES), n_user_ratings, replace=False)
    
    for movie_idx in user_movies:
        # Genera rating con bias verso valori alti (più realistico)
        rating = np.random.choice([1.0, 2.0, 3.0, 4.0, 5.0], 
                                  p=[0.05, 0.1, 0.2, 0.35, 0.3])
        
        data.append({
            'user_id': user_id,
            'item_id': 101 + movie_idx,  # Movie ID da 101 a 150
            'rating': rating
        })

# Crea DataFrame
df = pd.DataFrame(data)

# Rimuovi eventuali duplicati
df = df.drop_duplicates(subset=['user_id', 'item_id'])

# Ordina
df = df.sort_values(['user_id', 'item_id']).reset_index(drop=True)

# Salva il dataset
output_path = Path(__file__).parent.parent / "data" / "ratings.csv"
df.to_csv(output_path, index=False)

# Salva anche la mappatura movie_id -> nome film
movies_df = pd.DataFrame({
    'item_id': range(101, 101 + len(MOVIES)),
    'title': MOVIES
})
movies_path = Path(__file__).parent.parent / "data" / "movies.csv"
movies_df.to_csv(movies_path, index=False)

print(f"✓ Dataset FILM generato: {len(df)} ratings")
print(f"   - Utenti: {df['user_id'].nunique()}")
print(f"   - Film: {df['item_id'].nunique()}")
print(f"   - Rating medio: {df['rating'].mean():.2f}")
print(f"   - Salvato in: {output_path}")
print(f"   - Mappatura film salvata in: {movies_path}")
print("\n[STATS] Distribuzione ratings:")
print(df['rating'].value_counts().sort_index())
print(f"\n[SPARSITY] {(1 - len(df) / (df['user_id'].nunique() * df['item_id'].nunique())) * 100:.1f}%")
