# Arquitetura do Sistema — TikTok Ranking Overlay

## Visão Geral

Sistema de ranking em tempo real que captura presentes de lives do TikTok,
processa a lógica de pontuação no backend e atualiza o overlay do streamer
sem necessidade de recarregar a página.

---

## Fluxo de Dados Completo

| Ordem | Componente | Descrição do Fluxo / Transformação |
| :--- | :--- | :--- |
| **1** | **TikTok Live Stream** | Origem do evento via WebSocket interno da plataforma TikTok. |
| **2** | **TikTokLive Client (Python)** | Captura do `GiftEvent` bruto: `{ gift_id, gift_name, user, repeat_count }`. |
| **3** | **Flask Backend (`gift_processor.py`)** | Valida o ID no `gift_map.json`, incrementa o score via Prisma/SQL e salva logs brutos. |
| **4** | **Flask-SocketIO** | Emite o sinal `ranking_update` via WebSocket para sincronização em tempo real. |
| **5** | **React Frontend / Overlay** | Recebe o ranking ordenado e executa a animação de reordenação suave das linhas. |
| **6** | **OBS Browser Source** | Exibição final do overlay transparente sobre a transmissão oficial. |

---

## Componentes e Responsabilidades

### Backend (`/backend`)
| Arquivo | Responsabilidade |
|---|---|
| `app.py` | Inicialização do Flask e SocketIO |
| `tiktok_client.py` | Conexão e escuta de eventos TikTokLive |
| `gift_processor.py` | Lógica de mapeamento gift → entidade → score |
| `routes/ranking.py` | Endpoints REST da API |
| `models/` | Modelos Prisma gerados |
| `config.py` | Carregamento de variáveis de ambiente |

### Frontend (`/frontend`)
| Arquivo | Responsabilidade |
|---|---|
| `src/App.jsx` | Componente raiz React |
| `src/components/RankingTable.jsx` | Tabela de ranking animada |
| `src/components/TeamRow.jsx` | Linha individual de cada time |
| `src/hooks/useSocket.js` | Hook de conexão com SocketIO |

### Overlay (`/overlay`)
| Arquivo | Responsabilidade |
|---|---|
| `index.html` | Página estática para OBS Browser Source |
| `style.css` | Estilização otimizada para OBS (fundo transparente) |
| `socket.js` | Conexão SocketIO vanilla JS |

### Banco de Dados (`Prisma + SQLite`)
- Detalhado em [Modelagem do Banco de Dados](#modelagem-do-banco-de-dados).

---

## Decisões Técnicas

| Decisão | Justificativa |
|---|---|
| SQLite no desenvolvimento | Zero configuração, portável, suficiente para o volume de uma live |
| Flask-SocketIO com threading | Compatível com TikTokLive assíncrono |
| gift_map.json como config | Fácil de editar sem alterar código |
| React no frontend principal | Componentização e animações de reordenação |
| HTML puro no overlay | OBS Browser Source não precisa de build |

---

## Portas e Serviços

| Serviço | Porta | Descrição |
|---|---|---|
| Flask API + SocketIO | 5000 | Backend principal |
| React Dev Server | 5173 | Frontend em desenvolvimento |
| OBS Browser Source | — | Aponta para `overlay/index.html` ou `localhost:5000/overlay` |

---

## Tratamento de Erros Planejado

- **Live offline:** TikTokLive lança `exception` → sistema tenta reconexão com backoff exponencial
- **Gift não mapeado:** gift_processor ignora silenciosamente e loga no `events_log`
- **Banco indisponível:** Flask retorna erro 503 e SocketIO não emite update
- **Desconexão do cliente:** SocketIO reconecta automaticamente via `reconnection: true`

---

## Modelagem do Banco de Dados

### Tabela: `entities`
Representa cada time do Brasileirão.

| Campo | Tipo | Descrição |
|---|---|---|
| id | Int (PK) | Identificador único |
| name | String | Nome do time (ex: "Palmeiras") |
| slug | String (unique) | Identificador URL-safe (ex: "palmeiras") |
| color | String | Cor hexadecimal do time (ex: "#E8001A") |
| logo_url | String | URL do escudo do time |
| created_at | DateTime | Data de criação |

### Tabela: `gifts`
Catálogo de presentes do TikTok mapeados.

| Campo | Tipo | Descrição |
|---|---|---|
| id | Int (PK) | Identificador único |
| tiktok_gift_id | Int (unique) | ID real do presente no TikTok |
| name | String | Nome do presente (ex: "Rose") |
| icon_url | String | URL do ícone do presente |
| point_value | Int | Quantos pontos vale 1 unidade |
| entity_id | Int (FK) | Time que este presente representa |

### Tabela: `scores`
Pontuação atual de cada time (atualizada em tempo real).

| Campo | Tipo | Descrição |
|---|---|---|
| id | Int (PK) | Identificador único |
| entity_id | Int (FK, unique) | Referência ao time |
| total_score | Int | Pontuação total acumulada |
| updated_at | DateTime | Última atualização |

### Tabela: `events_log`
Log imutável de cada presente recebido (auditoria).

| Campo | Tipo | Descrição |
|---|---|---|
| id | Int (PK) | Identificador único |
| tiktok_gift_id | Int | ID do presente recebido |
| gift_name | String | Nome do presente |
| sender_username | String | Username de quem enviou |
| repeat_count | Int | Quantidade enviada de uma vez |
| entity_id | Int (FK, nullable) | Time pontuado (null se não mapeado) |
| points_awarded | Int | Pontos concedidos neste evento |
| raw_event | String | JSON bruto do evento para debug |
| created_at | DateTime | Timestamp do evento |