import pytest
import asyncio
from prisma import Prisma

EXPECTED_GIFT_DATA = [
    {"slug": "palmeiras",    "gift_id": 7934,  "gift_name": "Heart Me"},
    {"slug": "flamengo",     "gift_id": 5655,  "gift_name": "Rose"},
    {"slug": "sao-paulo",    "gift_id": 8286,  "gift_name": "GG"},
    {"slug": "fluminense",   "gift_id": 15232, "gift_name": "You're awesome"},
    {"slug": "bahia",        "gift_id": 5487,  "gift_name": "Finger Heart"},
    {"slug": "athletico-pr", "gift_id": 19441, "gift_name": "Freestyle"},
    {"slug": "coritiba",     "gift_id": 5480,  "gift_name": "Heart"},
    {"slug": "atletico-mg",  "gift_id": 10602, "gift_name": "White Rose"},
    {"slug": "bragantino",   "gift_id": 5658,  "gift_name": "Perfume"},
    {"slug": "vitoria",      "gift_id": 9947,  "gift_name": "Friendship"},
    {"slug": "botafogo",     "gift_id": 5827,  "gift_name": "Ice Cream Cone"},
    {"slug": "gremio",       "gift_id": 19446, "gift_name": "Wink wink"},
    {"slug": "vasco",        "gift_id": 19439, "gift_name": "Oldies"},
    {"slug": "internacional","gift_id": 5269,  "gift_name": "TikTok"},
    {"slug": "santos",       "gift_id": 19448, "gift_name": "Slow motion"},
    {"slug": "corinthians",  "gift_id": 15231, "gift_name": "Love you so much"},
    {"slug": "cruzeiro",     "gift_id": 19445, "gift_name": "Name shoutout"},
    {"slug": "remo",         "gift_id": 19447, "gift_name": "Overreact"},
    {"slug": "chapecoense",  "gift_id": 19443, "gift_name": "Bravo!"},
    {"slug": "mirassol",     "gift_id": 15063, "gift_name": "Journey Pass"},
]

@pytest.fixture(scope="module")
async def db():
    client = Prisma()
    await client.connect()
    yield client
    await client.disconnect()

@pytest.mark.asyncio
async def test_entities_count(db):
    """Deve haver exatamente 20 entidades seedadas."""
    count = await db.entity.count()
    assert count == 20, f"Esperado 20 entidades, encontrado {count}"

@pytest.mark.asyncio
async def test_scores_count(db):
    """Deve haver um Score para cada entidade."""
    count = await db.score.count()
    assert count == 20, f"Esperado 20 scores, encontrado {count}"

@pytest.mark.asyncio
async def test_scores_start_at_zero(db):
    """Todos os scores devem iniciar em zero."""
    non_zero = await db.score.find_many(where={"total_score": {"gt": 0}})
    assert len(non_zero) == 0, f"{len(non_zero)} times já têm score > 0"

@pytest.mark.asyncio
async def test_gift_map_count(db):
    """Deve haver exatamente 20 entradas no GiftMap."""
    count = await db.giftmap.count()
    assert count == 20, f"Esperado 20 mapeamentos, encontrado {count}"

@pytest.mark.asyncio
@pytest.mark.parametrize("expected", EXPECTED_GIFT_DATA)
async def test_all_teams_gifts(db, expected):
    """Valida se cada time está com o presente e ID corretos conforme o JSON oficial."""
    entity = await db.entity.find_unique(
        where={"slug": expected["slug"]},
        include={"gift_map": {"include": {"gift": True}}}
    )
    
    assert entity is not None, f"Time {expected['slug']} não encontrado no banco"
    assert len(entity.gift_map) > 0, f"{entity.name} não tem presente mapeado"
    
    gift = entity.gift_map[0].gift
    assert gift.tiktok_gift_id == expected["gift_id"], \
        f"{entity.name}: ID esperado {expected['gift_id']}, encontrado {gift.tiktok_gift_id}"
    assert gift.name == expected["gift_name"], \
        f"{entity.name}: Nome esperado '{expected['gift_name']}', encontrado '{gift.name}'"

@pytest.mark.asyncio
async def test_slugs_are_unique(db):
    """Slugs devem ser únicos entre todas as entidades."""
    entities = await db.entity.find_many()
    slugs = [e.slug for e in entities]
    assert len(slugs) == len(set(slugs)), "Existem slugs duplicados!"

@pytest.mark.asyncio
async def test_flask_health_endpoint():
    """O endpoint /health deve retornar status ok."""
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from app import create_app
    app = create_app()
    client = app.test_client()

    response = client.get("/health")
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "ok"