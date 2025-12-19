"""
creo il MCP Server per gestire le funzioni temperatura/umidità

"""

from mcp.server.fastmcp import FastMCP
import random

mcp = FastMCP("weather-service")

@mcp.tool()
async def get_temperatura() -> str:
    """Restituisce la temperatura attuale """
    temp = random.uniform(15.0, 30.0) #ho utilizzato valori casuali per la demo per smplicità
    return f"La temperatura attuale è {temp:.1f}°C"

@mcp.tool()
async def get_umidita() -> str:
    """Restituisce l'umidità attuale in percentuale"""
    humidity = random.uniform(40.0, 80.0)
    return f"L'umidità attuale è {humidity:.1f}%"

if __name__ == "__main__":
    mcp.run(transport='stdio')
