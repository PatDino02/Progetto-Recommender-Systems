"""
Demo Interattiva che simula l'uso di Continue con MCP
Mostra come Continue dovrebbe comportarsi con i tool MCP
"""
import asyncio
from recommender_server import (
    load_or_initialize_data,
    get_recommendations,
    add_rating,
    get_similar_users,
    get_user_stats
)

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

async def simulate_continue():
    """Simula l'interazione di Continue con MCP Server"""
    
    print_header("DEMO: Continue + MCP Recommender System")
    print("Questa demo simula come Continue dovrebbe usare i tool MCP\n")
    
    # Carica dati
    load_or_initialize_data()
    print("[INIT] Server MCP inizializzato con 181 ratings\n")
    
    # Simula comando utente 1
    print('User: "Dammi le raccomandazioni per l\'utente 1"')
    print("\n[Continue identifica il tool]")
    print("""
{
  "name": "get_recommendations",
  "arguments": {
    "user_id": 1,
    "top_n": 5
  }
}
""")
    
    print("[Continue esegue il tool e mostra il risultato]\n")
    result = await get_recommendations(user_id=1, top_n=5)
    print("Risultato:")
    import json
    data = eval(result)
    print(f"\nRaccomandazioni per User {data['user_id']}:")
    for rec in data['recommendations']:
        print(f"  • Item {rec['item_id']}: rating predetto = {rec['predicted_rating']:.2f} ⭐")
    
    # Simula comando utente 2
    print("\n" + "-" * 70)
    print('\nUser: "Trova gli utenti simili all\'utente 1"')
    print("\n[Continue identifica il tool]")
    print("""
{
  "name": "get_similar_users",
  "arguments": {
    "user_id": 1,
    "top_n": 5
  }
}
""")
    
    print("[Continue esegue il tool e mostra il risultato]\n")
    result = await get_similar_users(user_id=1, top_n=5)
    print("Risultato:")
    data = eval(result)
    print(f"\nUtenti simili a User {data['user_id']}:")
    for user in data['similar_users']:
        print(f"  • User {user['user_id']}: similarity = {user['similarity_score']:.4f}")
    
    # Simula comando utente 3
    print("\n" + "-" * 70)
    print('\nUser: "Mostrami le statistiche dell\'utente 1"')
    print("\n[Continue identifica il tool]")
    print("""
{
  "name": "get_user_stats",
  "arguments": {
    "user_id": 1
  }
}
""")
    
    print("[Continue esegue il tool e mostra il risultato]\n")
    result = await get_user_stats(user_id=1)
    print("Risultato:")
    data = eval(result)
    print(f"\nStatistiche User {data['user_id']}:")
    print(f"  • Total ratings: {data['total_ratings']}")
    print(f"  • Average rating: {data['average_rating']:.2f}")
    print(f"  • Min rating: {data['min_rating']}")
    print(f"  • Max rating: {data['max_rating']}")
    print(f"  • Items rated: {len(data['rated_items'])}")
    
    # Simula comando utente 4
    print("\n" + "-" * 70)
    print('\nUser: "Aggiungi rating: utente 5, item 120, rating 4.5"')
    print("\n[Continue identifica il tool]")
    print("""
{
  "name": "add_rating",
  "arguments": {
    "user_id": 5,
    "item_id": 120,
    "rating": 4.5
  }
}
""")
    
    print("[Continue esegue il tool e mostra il risultato]\n")
    result = await add_rating(user_id=5, item_id=120, rating=4.5)
    print("Risultato:")
    print(f"  {result}")
    
    print_header("DEMO COMPLETATA")
    print("Questo è il comportamento atteso di Continue con MCP.")
    print("Il server MCP funziona perfettamente (verificato con test_mcp_protocol.py).")
    print("\nPer testare direttamente il server:")
    print("  • python test_server.py          - Test completo")
    print("  • python test_interactive.py     - Menu interattivo")
    print("  • python test_mcp_protocol.py    - Verifica protocollo MCP")

if __name__ == "__main__":
    asyncio.run(simulate_continue())
