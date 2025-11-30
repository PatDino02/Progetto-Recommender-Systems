# Comandi per Eseguire il Progetto

## 1. Test Completo del Server

```powershell
cd C:\Users\Patrick\Desktop\progetto\mcp_server
.venv\Scripts\python.exe test_server.py
```

**Output atteso:**
```
[OK] Dati caricati: 181 ratings
[OK] Test get_user_stats: passed
[OK] Test get_similar_users: passed
[OK] Test get_recommendations: passed
[OK] Test add_rating: passed
[SUCCESS] TUTTI I TEST COMPLETATI
```

---

## 2. Test Interattivo (Menu)

```powershell
cd C:\Users\Patrick\Desktop\progetto\mcp_server
.venv\Scripts\python.exe test_interactive.py
```

**Menu disponibile:**
- `1` - Statistiche Utente
- `2` - Trova Utenti Simili
- `3` - Ottieni Raccomandazioni
- `4` - Aggiungi Rating
- `5` - Esegui TUTTI i test
- `0` - Esci

**Esempio:** Scegli `5` per vedere tutti i tool in azione

---

## 3. Test Protocollo MCP

```powershell
cd C:\Users\Patrick\Desktop\progetto\mcp_server
.venv\Scripts\python.exe test_mcp_protocol.py
```

**Verifica che il server MCP funzioni correttamente**

---

## 4. Demo Simulazione Continue

```powershell
cd C:\Users\Patrick\Desktop\progetto\mcp_server
.venv\Scripts\python.exe demo_continue.py
```

**Mostra come Continue dovrebbe comportarsi con i tool MCP**

---

## 5. Jupyter Notebook (Analisi Completa)

```powershell
cd C:\Users\Patrick\Desktop\progetto
jupyter notebook notebooks/mcp_demo.ipynb
```

Oppure apri direttamente `notebooks/mcp_demo.ipynb` in VS Code e:
1. Seleziona kernel Python (`.venv`)
2. Run All

**Include:**
- Analisi dataset
- Grafici
- Test tutti i tool
- Metriche MAE/RMSE
- Spiegazione algoritmo

---

## 6. Generare Nuovo Dataset (Opzionale)

```powershell
cd C:\Users\Patrick\Desktop\progetto\mcp_server
.venv\Scripts\python.exe generate_dataset.py
```

