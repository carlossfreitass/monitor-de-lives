def serialize_entity(entity, position: int) -> dict:
    """Converte um objeto Entity do Prisma em dict para a API."""
    score = entity.score.total_score if entity.score else 0

    gift_info = None
    if entity.gift_map:
        gift = entity.gift_map[0].gift
        gift_info = {
            "tiktok_gift_id": gift.tiktok_gift_id,
            "name":           gift.name,
            "icon_url":       gift.icon_url,
            "point_value":    gift.point_value,
        }

    return {
        "position":  position,
        "id":        entity.id,
        "name":      entity.name,
        "slug":      entity.slug,
        "color":     entity.color,
        "logo_url":  entity.logo_url,
        "score":     score,
        "gift":      gift_info,
    }

def serialize_gift_map(gift_map_entry) -> dict:
    """Converte um GiftMap em dict para a API."""
    return {
        "tiktok_gift_id": gift_map_entry.gift.tiktok_gift_id,
        "gift_name":      gift_map_entry.gift.name,
        "gift_icon_url":  gift_map_entry.gift.icon_url,
        "point_value":    gift_map_entry.gift.point_value,
        "entity_id":      gift_map_entry.entity.id,
        "entity_name":    gift_map_entry.entity.name,
        "entity_slug":    gift_map_entry.entity.slug,
        "entity_color":   gift_map_entry.entity.color,
    }