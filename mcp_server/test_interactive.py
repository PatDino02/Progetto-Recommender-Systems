"""
Test Interattivo MCP Recommender System
Scegli quale funzione testare dal menu
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from recommender_server import (
    load_or_initialize_data,
    get_recommendations,
    add_rating,
    get_similar_users,
    get_user_stats
)

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_separator():
    print("-" * 60)

async def test_user_stats(user_id):
    print_header(f"[STATS] Statistiche Utente {user_id}")
    result = await get_user_stats(user_id=user_id)
    print(result)

async def test_similar_users(user_id, top_n=5):
    print_header(f"[SIMILARITY] Utenti Simili a User {user_id}")
    result = await get_similar_users(user_id=user_id, top_n=top_n)
    print(result)

async def test_recommendations(user_id, top_n=5):
    print_header(f"[RECOMMENDATIONS] Raccomandazioni per User {user_id}")
    result = await get_recommendations(user_id=user_id, top_n=top_n)
    print(result)

async def test_add_rating(user_id, item_id, rating):
    print_header("[ADD] Aggiungi Rating")
    result = await add_rating(user_id=user_id, item_id=item_id, rating=rating)
    print(result)

async def run_all_tests():
    print_header("[TEST] TEST COMPLETO - Tutti i Tools MCP")
    
    user_id = 1
    
    # Test 1
    await test_user_stats(user_id)
    
    # Test 2
    await test_similar_users(user_id, top_n=3)
    
    # Test 3
    await test_recommendations(user_id, top_n=5)
    
    # Test 4
    await test_add_rating(user_id=1, item_id=131, rating=4.5)
    
    # Test 5 - Raccomandazioni dopo nuovo rating
    print_header("[UPDATE] Raccomandazioni Aggiornate")
    await test_recommendations(user_id, top_n=3)
    
    print("\n" + "=" * 60)
    print("[SUCCESS] TUTTI I TEST COMPLETATI CON SUCCESSO!")
    print("=" * 60 + "\n")

async def main():
    # Carica dati
    print_header("[INIT] MCP Recommender System - Test Interattivo")
    print("\n[LOADING] Caricamento dati...")
    load_or_initialize_data()
    print("[OK] Dati caricati correttamente\n")
    
    while True:
        print("\n" + "=" * 60)
        print("MENU TEST")
        print("=" * 60)
        print("1. [STATS] Statistiche Utente")
        print("2. [SIMILARITY] Trova Utenti Simili")
        print("3. [RECOMMENDATIONS] Ottieni Raccomandazioni")
        print("4. [ADD] Aggiungi Rating")
        print("5. [TEST] Esegui TUTTI i test")
        print("0. [EXIT] Esci")
        print("=" * 60)
        
        choice = input("\nScegli un'opzione (0-5): ").strip()
        
        if choice == "1":
            user_id = input("User ID: ").strip()
            try:
                await test_user_stats(int(user_id))
            except Exception as e:
                print(f"[ERROR] Errore: {e}")
        
        elif choice == "2":
            user_id = input("User ID: ").strip()
            top_n = input("Quanti utenti simili? (default: 5): ").strip() or "5"
            try:
                await test_similar_users(int(user_id), int(top_n))
            except Exception as e:
                print(f"[ERROR] Errore: {e}")
        
        elif choice == "3":
            user_id = input("User ID: ").strip()
            top_n = input("Quante raccomandazioni? (default: 5): ").strip() or "5"
            try:
                await test_recommendations(int(user_id), int(top_n))
            except Exception as e:
                print(f"[ERROR] Errore: {e}")
        
        elif choice == "4":
            user_id = input("User ID: ").strip()
            item_id = input("Item ID: ").strip()
            rating = input("Rating (1-5): ").strip()
            try:
                await test_add_rating(int(user_id), int(item_id), float(rating))
            except Exception as e:
                print(f"[ERROR] Errore: {e}")
        
        elif choice == "5":
            await run_all_tests()
        
        elif choice == "0":
            print("\n[EXIT] Arrivederci!")
            break
        
        else:
            print("[ERROR] Opzione non valida!")

if __name__ == "__main__":
    asyncio.run(main())
    

#.venv\Scripts\python.exe test_interactive.py
