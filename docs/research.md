# Research — TikTok Ranking Overlay

## 1. TikTokLive — Biblioteca

- **Versão instalada:** 6.6.5
- **Repositório:** https://github.com/isaackogan/TikTokLive
- **Conexão:** TikTokLiveClient(unique_id="@username")
- **Eventos principais:**
  - `ConnectEvent` — Disparado ao conectar na live
  - `DisconnectEvent` — Disparado ao desconectar
  - `GiftEvent` — Disparado ao receber presente
  - `CommentEvent` — Disparado ao receber comentário

## 2. Flask 3.x — Breaking Changes Relevantes

- Suporte nativo a rotas async (não precisa mais de `flask[async]` separado)
- `flask.escape()` removido → usar `markupsafe.escape()`

## 3. Flask-SocketIO

- **Versão:** 5.6.1
- **Inicialização:** `SocketIO(app, cors_allowed_origins="*")`
- **Emit servidor → cliente:** `socketio.emit('update_ranking', data)`
- **Compatível com:** gevent, eventlet, threading

## 4. Dúvidas e Riscos Identificados

- [⚠️] Gift IDs mudam entre regiões do TikTok?
> Teste com presentes comuns primeiro; use logs para IDs novos.
- [✅] TikTokLive funciona sem conta logada?
- [⚠️] Latência do SocketIO em eventos de alta frequência?
> Se a live for grande, use "buffer" no Python antes de dar o `.emit`.

## 5. Próximos Passos (Fase 2)

- Arquitetura do banco de dados (Prisma + SQL)
- Estrutura do Flask com Blueprints
- Primeiro endpoint REST `/api/ranking`