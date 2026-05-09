from prisma import Prisma
from typing import Optional

db = Prisma()

async def get_db():
    if not db.is_connected():
        await db.connect()
    return db

async def create_event(
    tiktok_gift_id: int,
    gift_name: str,
    sender_username: str,
    repeat_count: int,
    entity_id: Optional[int],
    points_awarded: int,
    raw_event: str,
) -> object:
    """Cria um registro no EventLog."""
    client = await get_db()

    return await client.eventlog.create(
        data={
            "tiktok_gift_id":  tiktok_gift_id,
            "gift_name":       gift_name,
            "sender_username": sender_username,
            "repeat_count":    repeat_count,
            "entity_id":       entity_id,
            "points_awarded":  points_awarded,
            "raw_event":       raw_event,
        }
    )

async def get_recent_events(limit: int = 50) -> list:
    """
    Retorna os últimos N eventos ordenados do mais recente para o mais antigo.
    Inclui a entidade relacionada quando disponível.
    """
    client = await get_db()

    return await client.eventlog.find_many(
        take=limit,
        order={"created_at": "desc"},
        include={"entity": True},
    )

async def count_events() -> int:
    """Total de eventos registrados."""
    client = await get_db()
    return await client.eventlog.count()