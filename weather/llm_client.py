"""
Client LLM che usa il server MCP per rispondere a domande sul meteo.
Questo dimostra come un LLM (Llama) possa utilizzare funzioni MCP
in modo automatico basandosi sul prompt dell'utente.
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import ollama

async def chat_with_weather_tools(user_prompt: str):
    """
    Gestisce una conversazione con l'LLM che ha accesso ai tools MCP.
    
    Args:
        user_prompt: La domanda dell'utente
    """
    # Connessione al server MCP
    server_params = StdioServerParameters(
        command="python",
        args=["weather_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Ottengo i tools disponibili dal server MCP
            tools_list = await session.list_tools()

# siccome MCP usa il formato Tool, devo convertirlo in formato Ollama che utiliza il formato OpenAI

            tools = []
            for tool in tools_list.tools:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name, #prendo il nome della funzione
                        "description": tool.description, #prendo la descrizione della funzione
                        "parameters": tool.inputSchema
                    }
                })
            
            print(f"\n User: {user_prompt}\n")
            
#Chiamo l'LLM con i tools disponibili e aggiungo un system message per guidare l'LLM
            response = ollama.chat(
                model='llama3.2',
                messages=[
                    {
                        'role': 'system', 
                        'content': 'Sei un assistente meteo. Hai accesso a funzioni per ottenere temperatura e umidità. se ti chiedono in generale come è il tempo usa entrambe le funzioni.'
                    },
                    {
                        'role': 'user', 
                        'content': user_prompt
                    }
                ],
                tools=tools
            )
            
            # Se llama  vuole usare una funzione entra nell'if
            if response['message'].get('tool_calls'):
     
                for tool_call in response['message']['tool_calls']:
                    function_name = tool_call['function']['name'] #estraggo il nome della funzione da chiamare
                    print(f"   - {function_name}()")
                    
                    # Chiamo la funzione tramite MCP
                    result = await session.call_tool(function_name, {}) #invia una richiesta al server MCP per eseguire la funzione 
                    print(f"\n Risultato: {result.content[0].text}\n")
            else:
                print(f" Risposta: {response['message']['content']}\n")

async def main():
    """
    Esegue alcuni esempi di prompt per dimostrare come l'LLM
    scelga automaticamente quale funzione chiamare.
    """
    prompts = [
        "Che temperatura c'è?",
        "Qual è l'umidità attuale?",
        "Com'è il tempo oggi?"
    ]
    
    for prompt in prompts:
        await chat_with_weather_tools(prompt)
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())

