# API Reference — TikTok Ranking Overlay

**Base URL:** `http://localhost:5000`  
**Content-Type:** `application/json`

---

## Autenticação

Endpoints protegidos exigem o header:
X-Secret-Key: `valor de SECRET_KEY no .env`

---

## Endpoints

### `GET /health`
Verifica se o servidor está rodando.

**Response 200:**
```json
{
  "status": "ok",
  "env": "development"
}
```

---

### `GET /api/ranking/`
Retorna o ranking completo ordenado por score decrescente.

**Query Params:**

| Param | Tipo | Default | Descrição |
|---|---|---|---|
| page | int | 1 | Página atual |
| page_size | int | 20 | Itens por página (máx. 20) |

**Response 200:**
```json
{
  "data": [
    {
      "position": 1,
      "id": 1,
      "name": "Palmeiras",
      "slug": "palmeiras",
      "color": "#006437",
      "logo_url": "/logos/palmeiras.png",
      "score": 0,
      "gift": {
        "tiktok_gift_id": 7934,
        "name": "Heart Me",
        "icon_url": "https://i.ibb.co/20Lw7LLR/f82b75d67c3e4553d278404babdf91e2.webp",
        "point_value": 1
      }
    }
  ],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 20,
    "total_pages": 1
  }
}
```

---

### `GET /api/ranking/<entity_id>`
Retorna dados de um time específico.

**Response 200:**
```json
{
  "data": {
    "position": 0,
    "id": 1,
    "name": "Palmeiras",
    "slug": "palmeiras",
    "color": "#006437",
    "logo_url": "/logos/flamengo.png",
    "score": 42,
    "gift": {
      "tiktok_gift_id": 7934,
      "name": "Heart Me",
      "icon_url": "https://i.ibb.co/20Lw7LLR/f82b75d67c3e4553d278404babdf91e2.webp",
      "point_value": 1
    }
  }
}
```

**Response 404:**
```json
{ "error": "Entidade 99 não encontrada" }
```

---

### `GET /api/gifts/`
Retorna todos os presentes cadastrados.

**Response 200:**
```json
{
  "data": [
    {
      "id": 1,
      "tiktok_gift_id": 5655,
      "name": "Rose",
      "icon_url": "https://i.ibb.co/rGrfc0j5/cf6a40558018965a8171cf5a575dd9de.png",
      "point_value": 1
    }
  ],
  "total": 20
}
```

---

### `GET /api/gifts/map`
Retorna o mapeamento gift → entidade para o frontend.

**Response 200:**
```json
{
  "data": [
    {
      "tiktok_gift_id": 5655,
      "gift_name": "Rose",
      "gift_icon_url": "https://i.ibb.co/rGrfc0j5/cf6a40558018965a8171cf5a575dd9de.png",
      "point_value": 1,
      "entity_id": 1,
      "entity_name": "Palmeiras",
      "entity_slug": "palmeiras",
      "entity_color": "#006437"
    }
  ],
  "indexed": {
    "5655": { "...": "mesmo objeto acima" }
  },
  "total": 20
}
```

---

### `GET /api/control/status`
Retorna o estado atual do serviço.

**Response 200:**
```json
{
  "connected": true,
  "username": "@streamer",
  "retry_count": 0,
  "last_error": null,
  "gifts_received": 42,
  "thread_alive": true
}
```

---

### `GET /api/events/recent`
Retorna os últimos eventos recebidos. Útil para debug e auditoria ao vivo.

**Query Params:**

| Param | Tipo | Default | Descrição |
|---|---|---|---|
| limit | int | 50 | Máx. 200 eventos |

**Response 200:**
```json
{
  "data": [
    {
      "id": 42,
      "tiktok_gift_id": 5655,
      "gift_name": "Rose",
      "sender": "fan123",
      "repeat_count": 3,
      "points_awarded": 3,
      "entity_id": 2,
      "entity_name": "Flamengo",
      "created_at": "2026-05-09T20:15:30.000Z"
    }
  ],
  "meta": {
    "returned": 1,
    "total": 1,
    "limit": 50
  }
}
```

---

### `GET /api/events/cache`
Retorna snapshot do cache em memória do ScoreEngine.

---

### `POST /api/ranking/reset`
Zera todos os scores do ranking.

**Headers obrigatórios:**
X-Secret-Key: sua-secret-key

**Body:**
```json
{ "confirm": true }
```

**Response 200:**
```json
{
  "message": "Ranking zerado com sucesso.",
  "updated": 20
}
```

**Response 401:**
```json
{ "error": "Não autorizado. Header X-Secret-Key inválido ou ausente." }
```

**Response 400:**
```json
{ "error": "Confirmação necessária. Envie { \"confirm\": true } no body." }
```

---

### `POST /api/control/start`
Inicia a conexão com uma live do TikTok.

**Headers:** `X-Secret-Key`  
**Body:** `{ "username": "streamer" }`

**Response 200:**
```json
{ "success": true, "message": "Serviço iniciado para @streamer.", "username": "@streamer" }
```

---

### `POST /api/control/stop`
Encerra a conexão com a live.

**Headers:** `X-Secret-Key`

**Response 200:**
```json
{ "success": true, "message": "Serviço encerrado com sucesso." }
```

---

### `POST /api/events/cache/reload`
Força recarregamento do gift_map sem reiniciar o servidor.

---

## Códigos de Status

| Código | Significado |
|---|---|
| 200 | Sucesso |
| 400 | Bad Request — parâmetro inválido ou faltando |
| 401 | Não autorizado — secret key incorreta |
| 404 | Recurso não encontrado |
| 500 | Erro interno do servidor |

---

## Notas de Implementação

- Todos os endpoints são **stateless** — o estado fica no banco SQLite
- O campo `indexed` em `/api/gifts/map` permite lookup O(1) no frontend por `tiktok_gift_id`
- O reset usa `hmac.compare_digest` para proteção contra timing attacks
- Paginação usa ceil division: `-(-total // page_size)`