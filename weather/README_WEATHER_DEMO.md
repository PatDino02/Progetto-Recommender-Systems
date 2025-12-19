# Demo LLM + MCP: Temperatura e Umidità

Modello semplice per visualizzare il comportamento tra MCP e Llama 
## File

- **weather_server.py**: Server MCP che espone due funzioni:
  - `get_temperatura()`: restituisce la temperatura attuale
  - `get_umidita()`: restituisce l'umidità attuale

- **llm_client.py**: Client che integra Llama con il server MCP

## Come funziona

1. Il server MCP espone le funzioni disponibili
2. Il client connette l'LLM al server MCP
3. L'utente fa una domanda
4. L'LLM decide automaticamente se e quale funzione chiamare
5. Il risultato viene mostrato all'utente

## Installazione

```bash
ollama pull llama3.2
```

## Esecuzione

```bash
python llm_client.py
```

## Esempi

- **"Che temperatura c'è?"** → L'LLM chiama `get_temperatura()`
- **"Qual è l'umidità?"** → L'LLM chiama `get_umidita()`  
- **"Com'è il tempo?"** → L'LLM chiama entrambe le funzioni


