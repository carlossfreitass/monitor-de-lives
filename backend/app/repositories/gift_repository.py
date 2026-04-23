from prisma import Prisma
from typing import Optional

db = Prisma()

async def get_db():
    if not db.is_connected():
        await db.connect()
    return db

async def get_by_tiktok_gift_id(tiktok_gift_id: int) -> Optional[object]:
    """
    Busca um Gift pelo gift_id real do TikTok.
    Inclui o GiftMap com a entidade relacionada.
    Retorna None se o presente não estiver mapeado.
    """
    client = await get_db()

    return await client.gift.find_unique(
        where={"tiktok_gift_id": tiktok_gift_id},
        include={
            "gift_map": {
                "include": {"entity": True}
            }
        }
    )

async def get_gift_map() -> list:
    """
    Retorna o mapa completo de presentes com entidades.
    Usado pelo frontend para exibir ícones ao lado de cada time.
    """
    client = await get_db()

    gift_maps = await client.giftmap.find_many(
        include={
            "gift":   True,
            "entity": True
        }
    )

    return gift_maps

async def get_all_gifts() -> list:
    """Retorna todos os presentes cadastrados."""
    client = await get_db()
    return await client.gift.find_many()