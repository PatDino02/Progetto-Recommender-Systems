"""
Script di test per il server MCP Recommender Systems
Testa le funzioni del server in modo programmatico
"""

import asyncio
import sys
from pathlib import Path

# Aggiungi il path del server al PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

# Import delle funzioni del server
from recommender_server import (
    load_or_initialize_data,
    get_recommendations,
    add_rating,
    get_similar_users,
    get_user_stats
)


async def test_server():
    """Test completo del server MCP"""
    
    print("=" * 60)
    print("TEST MCP RECOMMENDER SERVER")
    print("=" * 60)
    
    # 1. Carica/inizializza dati
    print("\n[1] Caricamento dati...")
    load_or_initialize_data()
    print("[OK] Dati caricati correttamente\n")
    
    # 2. Test get_user_stats
    print("[2] Test get_user_stats (User 1)")
    print("-" * 60)
    stats = await get_user_stats(user_id=1)
    print(stats)
    print()
    
    # 3. Test get_similar_users
    print("[3] Test get_similar_users (User 1, top 3)")
    print("-" * 60)
    similar = await get_similar_users(user_id=1, top_n=3)
    print(similar)
    print()
    
    # 4. Test get_recommendations
    print("[4] Test get_recommendations (User 1, top 3)")
    print("-" * 60)
    recommendations = await get_recommendations(user_id=1, top_n=3)
    print(recommendations)
    print()
    
    # 5. Test add_rating
    print("[5] Test add_rating (User 1 -> Item 106 -> Rating 4.5)")
    print("-" * 60)
    result = await add_rating(user_id=1, item_id=106, rating=4.5)
    print(result)
    print()
    
    # 6. Test raccomandazioni dopo nuovo rating
    print("[6] Test get_recommendations dopo nuovo rating")
    print("-" * 60)
    recommendations2 = await get_recommendations(user_id=1, top_n=3)
    print(recommendations2)
    print()
    
    # 7. Test con utente diverso
    print("[7] Test get_recommendations (User 3, top 3)")
    print("-" * 60)
    recommendations3 = await get_recommendations(user_id=3, top_n=3)
    print(recommendations3)
    print()
    
    print("=" * 60)
    print("[SUCCESS] TUTTI I TEST COMPLETATI")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_server())
    
    
#cd C:\Users\Patrick\Desktop\progetto\mcp_server.venv\Scripts\python.exe test_server.py
