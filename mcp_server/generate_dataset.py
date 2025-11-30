"""
Script per generare un dataset di test più ricco per il recommender system
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Seed per riproducibilità
np.random.seed(42)

# Parametri del dataset
n_users = 20
n_items = 30
n_ratings = 200

# Genera ratings casuali
users = np.random.randint(1, n_users + 1, n_ratings)
items = np.random.randint(101, 101 + n_items, n_ratings)
ratings = np.random.choice([1.0, 2.0, 3.0, 4.0, 5.0], n_ratings, 
                           p=[0.05, 0.1, 0.2, 0.35, 0.3])  # Bias verso rating alti

# Crea DataFrame
df = pd.DataFrame({
    'user_id': users,
    'item_id': items,
    'rating': ratings
})

# Rimuovi duplicati (stesso user-item)
df = df.drop_duplicates(subset=['user_id', 'item_id'])

# Ordina
df = df.sort_values(['user_id', 'item_id']).reset_index(drop=True)

# Salva
output_path = Path(__file__).parent.parent / "data" / "ratings.csv"
df.to_csv(output_path, index=False)

print(f"[OK] Dataset generato: {len(df)} ratings")
print(f"   - Utenti: {df['user_id'].nunique()}")
print(f"   - Items: {df['item_id'].nunique()}")
print(f"   - Rating medio: {df['rating'].mean():.2f}")
print(f"   - Salvato in: {output_path}")
print("\n[STATS] Distribuzione ratings:")
print(df['rating'].value_counts().sort_index())
