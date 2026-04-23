from prisma import Prisma
from typing import Optional

db = Prisma()

async def get_db():
    """Garante que o cliente Prisma está conectado."""
    if not db.is_connected():
        await db.connect()
    return db

async def get_all(page: int = 1, page_size: int = 20) -> list:
    """
    Retorna todos os times ordenados por score decrescente.
    Inclui score e gift_map com dados do presente.
    Suporta paginação simples.
    """
    client = await get_db()
    skip = (page - 1) * page_size

    entities = await client.entity.find_many(
        skip=skip,
        take=page_size,
        include={
            "score": True,
            "gift_map": {
                "include": {"gift": True}
            }
        }
    )

    # Ordena por score decrescente (None vira 0)
    entities.sort(
        key=lambda e: e.score.total_score if e.score else 0,
        reverse=True
    )

    return entities

async def get_by_id(entity_id: int) -> Optional[object]:
    """Retorna uma entidade pelo ID com score e gift_map."""
    client = await get_db()

    return await client.entity.find_unique(
        where={"id": entity_id},
        include={
            "score": True,
            "gift_map": {
                "include": {"gift": True}
            }
        }
    )

async def get_by_slug(slug: str) -> Optional[object]:
    """Retorna uma entidade pelo slug."""
    client = await get_db()

    return await client.entity.find_unique(
        where={"slug": slug},
        include={
            "score": True,
            "gift_map": {
                "include": {"gift": True}
            }
        }
    )

async def update_score(entity_id: int, increment: int) -> object:
    """
    Incrementa o score de uma entidade atomicamente.
    Retorna o Score atualizado.
    """
    client = await get_db()

    return await client.score.update(
        where={"entity_id": entity_id},
        data={"total_score": {"increment": increment}}
    )

async def reset_all_scores() -> int:
    client = await get_db()
    result = await client.score.update_many(
        where={},
        data={"total_score": 0}
    )
    return result

async def count_entities() -> int:
    """Retorna o total de entidades no banco."""
    client = await get_db()
    return await client.entity.count()