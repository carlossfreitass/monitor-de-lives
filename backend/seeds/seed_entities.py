import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prisma import Prisma

# 20 times do Brasileirao Serie A 2026
TEAMS = [
    {"name": "Palmeiras",           "slug": "palmeiras",    "color": "#006437", "tiktok_gift_id": 7934,  "gift_name": "Heart Me",          "point_value": 1, "icon_url": "https://i.ibb.co/20Lw7LLR/f82b75d67c3e4553d278404babdf91e2.webp"},
    {"name": "Flamengo",            "slug": "flamengo",     "color": "#E8001A", "tiktok_gift_id": 5655,  "gift_name": "Rose",              "point_value": 1, "icon_url": "https://i.ibb.co/rGrfc0j5/cf6a40558018965a8171cf5a575dd9de.png"},
    {"name": "São Paulo",           "slug": "sao-paulo",    "color": "#CC0000", "tiktok_gift_id": 8286,  "gift_name": "GG",                "point_value": 1, "icon_url": "https://i.ibb.co/dw5JyTWs/26dd80bd9499dbed22cd6f1ac6ef6fd1.webp"},
    {"name": "Fluminense",          "slug": "fluminense",   "color": "#83001E", "tiktok_gift_id": 15232, "gift_name": "You're awesome",    "point_value": 1, "icon_url": "https://i.ibb.co/pBSTgYGz/9fab14e0441db1950dd8dedbb9a8dd17.webp"},
    {"name": "Bahia",               "slug": "bahia",        "color": "#004B8D", "tiktok_gift_id": 5487,  "gift_name": "Finger Heart",      "point_value": 1, "icon_url": "https://i.ibb.co/JFbWJzWq/2b2d66c2f9767fc8332ee1b5ba0c1057.png"},
    {"name": "Athletico-PR",        "slug": "athletico-pr", "color": "#CC0000", "tiktok_gift_id": 19441, "gift_name": "Freestyle",         "point_value": 1, "icon_url": "https://i.ibb.co/GQ0XbNTT/3d39c9a4674e1083790fe11b9240c9b0.webp"},
    {"name": "Coritiba",            "slug": "coritiba",     "color": "#008041", "tiktok_gift_id": 5480,  "gift_name": "Heart",             "point_value": 1, "icon_url": "https://i.ibb.co/7tCxn0KL/7a382fcc2e03076c9e4b089176de1395.webp"},
    {"name": "Atlético-MG",         "slug": "atletico-mg",  "color": "#000000", "tiktok_gift_id": 10602, "gift_name": "White Rose",        "point_value": 1, "icon_url": "https://i.ibb.co/Lz5cFKvV/e27a48825b293ef903e57305b18a7473.webp"},
    {"name": "Red Bull Bragantino", "slug": "bragantino",   "color": "#CC0000", "tiktok_gift_id": 5658,  "gift_name": "Perfume",           "point_value": 1, "icon_url": "https://i.ibb.co/G4xSNvyS/cd5792b709a7f56cbb2b6669a0e13c29.png"},
    {"name": "Vitória",             "slug": "vitoria",      "color": "#E30613", "tiktok_gift_id": 9947,  "gift_name": "Friendship",        "point_value": 1, "icon_url": "https://i.ibb.co/LDnBqccF/384165e9235c13d54ed3bfb1e08852c4.webp"},
    {"name": "Botafogo",            "slug": "botafogo",     "color": "#000000", "tiktok_gift_id": 5827,  "gift_name": "Ice Cream Cone",    "point_value": 1, "icon_url": "https://i.ibb.co/NnVg6cDS/71ba7d4c6eeaef46e5cc11fbf36ba3fa.png"},
    {"name": "Grêmio",              "slug": "gremio",       "color": "#5591CF", "tiktok_gift_id": 19446, "gift_name": "Wink wink",         "point_value": 1, "icon_url": "https://i.ibb.co/Ps9K6sMb/bc1471eff547aa787e5704e9aae615f3.webp"},
    {"name": "Vasco",               "slug": "vasco",        "color": "#000000", "tiktok_gift_id": 19439, "gift_name": "Oldies",            "point_value": 1, "icon_url": "https://i.ibb.co/7NY6SMcr/49734a1d4741786da371341e685df110.webp"},
    {"name": "Internacional",       "slug": "internacional","color": "#CC0000", "tiktok_gift_id": 5269,  "gift_name": "TikTok",            "point_value": 1, "icon_url": "https://i.ibb.co/CKmn0ggX/94aa2d574cfe6e3893c087cfb5a5efcd.png"},
    {"name": "Santos",              "slug": "santos",       "color": "#000000", "tiktok_gift_id": 19448, "gift_name": "Slow motion",       "point_value": 1, "icon_url": "https://i.ibb.co/B5QcLYYb/763049214b53c3ba4b6f077bf63ed37e.webp"},
    {"name": "Corinthians",         "slug": "corinthians",  "color": "#000000", "tiktok_gift_id": 15231, "gift_name": "Love you so much",  "point_value": 1, "icon_url": "https://i.ibb.co/9k3Tshvn/9e4be53ae69fbb59203f18f95ede626d.webp"},
    {"name": "Cruzeiro",            "slug": "cruzeiro",     "color": "#003087", "tiktok_gift_id": 19445, "gift_name": "Name shoutout",     "point_value": 1, "icon_url": "https://i.ibb.co/5hyZSYLQ/fd78e0b747c785c524b66c1c166758ca.webp"},
    {"name": "Remo",                "slug": "remo",         "color": "#121929", "tiktok_gift_id": 19447, "gift_name": "Overreact",         "point_value": 1, "icon_url": "https://i.ibb.co/1G4GyWwd/f172d4598f4902bd338126795104549e.webp"},
    {"name": "Chapecoense",         "slug": "chapecoense",  "color": "#00913C", "tiktok_gift_id": 19443, "gift_name": "Bravo!",            "point_value": 1, "icon_url": "https://i.ibb.co/WvLJBQyC/5ee7a490d3b37db28865517cbe917ec0.webp"},
    {"name": "Mirassol",            "slug": "mirassol",     "color": "#FFD700", "tiktok_gift_id": 15063, "gift_name": "Journey Pass",      "point_value": 1, "icon_url": "https://i.ibb.co/mrWK8Bp7/bd76c52c4c4601ab84ea01fefa1a8b5e.webp"},
]

async def seed():
    db = Prisma()
    await db.connect()

    print("🌱 Iniciando seed do banco de dados...")

    seeded = 0
    skipped = 0

    for team in TEAMS:
        # Verifica se entidade já existe (idempotente)
        existing = await db.entity.find_unique(where={"slug": team["slug"]})
        if existing:
            print(f"   ⏭️  Pulando {team['name']} — já existe.")
            skipped += 1
            continue

        # Cria a entidade (time)
        entity = await db.entity.create(data={
            "name":     team["name"],
            "slug":     team["slug"],
            "color":    team["color"],
            "logo_url": f"/logos/{team['slug']}.png",
        })

        # Cria ou recupera o Gift
        gift = await db.gift.upsert(
            where={"tiktok_gift_id": team["tiktok_gift_id"]},
            data={
                "create": {
                    "tiktok_gift_id": team["tiktok_gift_id"],
                    "name":           team["gift_name"],
                    "point_value":    team["point_value"],
                    "icon_url":       team["icon_url"],
                },
                "update": {}
            }
        )

        # Cria o GiftMap (relacionamento time ↔ presente)
        await db.giftmap.create(data={
            "entity_id": entity.id,
            "gift_id":   gift.id,
        })

        # Cria o Score inicial zerado
        await db.score.create(data={
            "entity_id":   entity.id,
            "total_score": 0,
        })

        print(f"   ✅ {team['name']} seedado — Gift: {team['gift_name']} (ID: {team['tiktok_gift_id']})")
        seeded += 1

    await db.disconnect()

    print(f"\n🎉 Seed concluído! {seeded} times criados, {skipped} ignorados.")

if __name__ == "__main__":
    asyncio.run(seed())