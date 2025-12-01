import pandas as pd
import numpy as np

# Carica i dati
df = pd.read_csv('../data/ratings.csv')

# Crea matrice user-item
pivot = df.pivot_table(index='user_id', columns='item_id', values='rating')

# Funzione per calcolare similarità con Pearson correlation
def calculate_similarity(user1_ratings, user2_ratings):
    common = user1_ratings.index.intersection(user2_ratings.index)
    common = [i for i in common if pd.notna(user1_ratings[i]) and pd.notna(user2_ratings[i])]
    
    if len(common) == 0:
        return 0.0, 0
    
    # Need at least 2 items for correlation
    if len(common) < 2:
        return 0.0, len(common)
    
    r1 = user1_ratings[common].values
    r2 = user2_ratings[common].values
    
    # Calculate means
    mean1 = np.mean(r1)
    mean2 = np.mean(r2)
    
    # Center the ratings
    r1_centered = r1 - mean1
    r2_centered = r2 - mean2
    
    # Calculate Pearson correlation
    numerator = np.sum(r1_centered * r2_centered)
    denominator = np.sqrt(np.sum(r1_centered ** 2) * np.sum(r2_centered ** 2))
    
    if denominator == 0:
        return 0.0, len(common)
    
    correlation = numerator / denominator
    
    # Normalize from [-1, 1] to [0, 1] for compatibility
    return (correlation + 1) / 2, len(common)


