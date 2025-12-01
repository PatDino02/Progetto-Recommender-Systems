#  Movie Recommender System with MCP

Sistema di raccomandazione film basato su **Collaborative Filtering** con supporto **Model Context Protocol (MCP)** per l'integrazione con Continue/Claude.

---

##  Descrizione

Questo progetto implementa un sistema di raccomandazione cinematografica che utilizza:
- **User-based Collaborative Filtering** con Pearson correlation
- **Model Context Protocol (MCP)** per esporre 4 tool utilizzabili da AI assistants
- **Dataset strutturato** con 502 ratings, 20 utenti, 89 film organizzati in 3 cluster tematici

L'algoritmo calcola la similarità tra utenti basandosi sui loro pattern di valutazione e predice i rating per film non ancora visti, generando raccomandazioni personalizzate.

---

##  Quick Start

### 1. Avvia il Server MCP

```powershell
cd "C:\Users\Patrick\Desktop\Progetto Recommender Systems\mcp_server"
python recommender_server.py
```

Il server si avvia in modalità stdio e resta in attesa di connessioni da Continue.

### 2. Usa Continue

Apri Continue in VS Code e prova:

```
Dammi le raccomandazioni per l'utente 3
```

```
Quali utenti sono simili all'utente 1?
```

Continue userà automaticamente i tool MCP per rispondere.

---

##  Funzionalità (MCP Tools)

Il server MCP espone 4 tool:

### 1. `get_recommendations`
Genera raccomandazioni personalizzate per un utente

**Parametri:**
- `user_id` (int): ID dell'utente
- `top_n` (int): Numero di raccomandazioni (default: 5)

**Output:** Lista di film con rating predetto e titolo

### 2. `get_similar_users`
Trova gli utenti con gusti simili

**Parametri:**
- `user_id` (int): ID dell'utente
- `top_n` (int): Numero di utenti simili (default: 5)

**Output:** Lista di utenti con score di similarità (0-100%) e numero di film in comune

### 3. `get_user_stats`
Ottiene statistiche di valutazione di un utente

**Parametri:**
- `user_id` (int): ID dell'utente

**Output:** Rating totali, media, min, max, lista film valutati

### 4. `add_rating`
Aggiunge o aggiorna un rating

**Parametri:**
- `user_id` (int): ID dell'utente
- `item_id` (int): ID del film
- `rating` (float): Valutazione (1-5)

**Output:** Messaggio di conferma

---

##  Algoritmo

### Collaborative Filtering con Pearson Correlation

1. **Calcolo Similarità**: Pearson correlation normalizzata [0,1]
   ```
   sim(u,v) = (pearson(u,v) + 1) / 2
   ```

2. **Predizione Rating**: Media pesata basata su utenti simili
   ```
   rating_predetto = Σ(similarity × rating) / Σ(similarity)
   ```

3. **Clustering Dataset**: 
   - **Action Fans** (User 1-7): preferiscono film d'azione/avventura
   - **Drama Lovers** (User 8-14): apprezzano film drammatici/psicologici  
   - **Indie Enthusiasts** (User 15-20): amano cinema indipendente/d'autore

Ogni coppia di utenti ha **almeno 3 film in comune** per garantire similarità affidabili.

---

##  Struttura Progetto

```
Progetto Recommender Systems/
├── mcp_server/
│   ├── recommender_server.py      # Server MCP principale
│   ├── generate_better_dataset.py # Generatore dataset con clustering
│   ├── test_interactive.py        # Test interattivo con menu
│  
├── data/
│   ├── ratings.csv                # Dataset ratings (502 righe)
│   └── movies.csv                 # Mapping ID → titolo film (103 film)
├── notebooks/
│   └── mcp_demo.ipynb             # Analisi completa con grafici e metriche
├── .continue/
│   └── mcpServers/
│       └── new-mcp-server.yaml    # Configurazione Continue
├── COMANDI.md                     # Guida comandi da eseguire
└── README.md                      # Questo file
```

---

## Dataset

- **502 ratings** (scala 1-5)
- **20 utenti** organizzati in 3 cluster tematici
- **89 film** da catalogo IMDb
- **103 film totali** in movies.csv (include titoli mappati)
- **Overlap minimo**: 3 film in comune tra ogni coppia di utenti

### Esempio Film nel Dataset
- The Shawshank Redemption (ID: 151)
- Inception (ID: 110)
- The Dark Knight (ID: 109)
- Pulp Fiction (ID: 114)
- Forrest Gump (ID: 105)

---

## Test e Validazione

### Test Interattivo
```powershell
python test_interactive.py
```
Menu interattivo per testare manualmente tutti i tool.

### Jupyter Notebook
Apri `notebooks/mcp_demo.ipynb` per:
- Analisi esplorativa dataset
- Grafici distribuzione ratings
- Test completo di tutti i tool
- Valutazione MAE/RMSE su train/test split
- Visualizzazione matrice user-item

---

## Configurazione Continue

File: `.continue/mcpServers/new-mcp-server.yaml`

```yaml
command: python
args:
  - recommender_server.py
type: stdio
cwd: C:\Users\Patrick\Desktop\Progetto Recommender Systems\mcp_server
```

---

## Dipendenze

- **Python 3.11+**
- **pandas** - manipolazione dati
- **numpy** - calcoli numerici
- **fastmcp** - framework MCP
- **scikit-learn** - metriche valutazione (opzionale, solo per notebook)
- **matplotlib** - grafici (opzionale, solo per notebook)

---

## Rigenerazione Dataset

Per generare un nuovo dataset:

```powershell
cd mcp_server
python generate_better_dataset.py
```

 **Attenzione**: Sovrascrive `ratings.csv` e `movies.csv` esistenti.

---

## Performance

Con il dataset attuale (502 ratings, overlap minimo 3 film):

- **MAE (Mean Absolute Error)**: ~0.6-0.8
- **RMSE (Root Mean Squared Error)**: ~0.8-1.0
- **Tempo risposta medio**: <100ms per raccomandazione
- **Coverage**: 100% utenti, ~85% film ricevono almeno una predizione

---

## Prossimi Sviluppi

- [ ] Implementare **Item-based Collaborative Filtering**
- [ ] Aggiungere **Content-based Filtering** (generi, attori, registi)
- [ ] Supporto per **Cold Start Problem** (nuovi utenti/film)
- [ ] **Matrix Factorization** (SVD) per scalabilità
- [ ] API REST in aggiunta a MCP
- [ ] Integrazione con database esterno (PostgreSQL)
- [ ] Sistema di feedback per migliorare predizioni

---

##  Autore

**Patrick Di Noto Marrella**  
Progetto: Recommender Systems  
Repository: [Progetto-Recommender-Systems](https://github.com/PatDino02/Progetto-Recommender-Systems)

---

## Licenza

Progetto didattico - uso libero per scopi educativi
