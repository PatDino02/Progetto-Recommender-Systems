"""
Test completo del protocollo MCP per verificare la comunicazione con Continue
"""
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_connection():
    """Testa la connessione MCP completa come farebbe Continue"""
    
    server_params = StdioServerParameters(
        command="python",
        args=["recommender_server.py"],
        env=None
    )
    
    print("[1] Connessione al server MCP...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print("[OK] Connesso al server MCP")
            
            # Inizializza la sessione
            await session.initialize()
            print("[OK] Sessione inizializzata")
            
            # Lista i tools disponibili
            tools = await session.list_tools()
            print(f"\n[TOOLS] Tools disponibili: {len(tools.tools)}")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test: chiamata a get_recommendations
            print("\n[TEST] Chiamata get_recommendations(user_id=1, top_n=5)...")
            result = await session.call_tool(
                "get_recommendations",
                arguments={"user_id": 1, "top_n": 5}
            )
            
            print("\n[RESULT] Risultato:")
            for content in result.content:
                if hasattr(content, 'text'):
                    print(content.text)
            
            # Test: chiamata a get_similar_users
            print("\n[TEST] Chiamata get_similar_users(user_id=1, top_n=3)...")
            result = await session.call_tool(
                "get_similar_users",
                arguments={"user_id": 1, "top_n": 3}
            )
            
            print("\n[RESULT] Risultato:")
            for content in result.content:
                if hasattr(content, 'text'):
                    print(content.text)
            
            print("\n[SUCCESS] Tutti i test MCP completati!")

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
