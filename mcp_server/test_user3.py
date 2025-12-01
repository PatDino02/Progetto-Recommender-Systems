"""
Test rapido raccomandazioni per User 3
"""
import asyncio
from recommender_server import load_or_initialize_data, get_recommendations

async def test_user_3():
    # Carica dati
    load_or_initialize_data()
    
    # Ottieni raccomandazioni per User 3
    result = await get_recommendations(user_id=3, top_n=5)
    
    # Parse e stampa risultato
    import ast
    data = ast.literal_eval(result)
    
    print(f"Top 5 raccomandazioni per User {data['user_id']}:\n")
    for rec in data['recommendations']:
        print(f"  {rec['title']} (ID: {rec['item_id']})")
        print(f"    → Rating predetto: {rec['predicted_rating']:.2f}\n")

if __name__ == "__main__":
    asyncio.run(test_user_3())
