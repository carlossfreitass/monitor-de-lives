import asyncio
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, DisconnectEvent, GiftEvent, CommentEvent

TIKTOK_USERNAME = "@hikarimayoficial"

client = TikTokLiveClient(unique_id=TIKTOK_USERNAME)

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"✅ Conectado à live de: {event.unique_id}")
    print(f"   Room ID: {client.room_id}")

@client.on(DisconnectEvent)
async def on_disconnect(event: DisconnectEvent):
    print("❌ Desconectado da live.")

@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    gift = event.gift

    quantidade = (
        getattr(gift, 'repeat_count', None) or
        getattr(gift, 'combo_count', None) or
        getattr(gift, 'gift_count', None) or
        1
    )

    print("🎁 PRESENTE RECEBIDO!")
    print(f"   Usuário   : {event.user.nickname}")
    print(f"   Gift ID   : {gift.id}")
    print(f"   Gift Name : {gift.name}")
    print(f"   Quantidade: {quantidade}")
    print(f"   [DEBUG] Atributos: {[a for a in dir(gift) if not a.startswith('_')]}")
    print("-" * 40)

@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    print(f"💬 {event.user.nickname}: {event.comment}")

if __name__ == "__main__":
    print(f"🔄 Tentando conectar à live de {TIKTOK_USERNAME}...")
    client.run()