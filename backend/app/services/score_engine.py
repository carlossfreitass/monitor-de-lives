from typing import Optional
from app.services.logger import get_logger
from app.repositories import gift_repository as gift_repo
from app.repositories import entity_repository as entity_repo

logger = get_logger("score_engine")

class ScoreEngine:
    """
    Motor de pontuação com cache em memória do gift_map.
    """

    def __init__(self):
        self._cache: dict[int, dict] = {}
        self._loaded = False

    # Cache
    async def load_cache(self) -> None:
        """
        Carrega o gift_map do banco para a memória.
        Deve ser chamado uma vez no startup do serviço TikTok.
        """
        gift_maps = await gift_repo.get_gift_map()

        self._cache = {
            entry.gift.tiktok_gift_id: {
                "entity_id":   entry.entity.id,
                "entity_name": entry.entity.name,
                "point_value": entry.gift.point_value,
            }
            for entry in gift_maps
        }

        self._loaded = True
        logger.info(f"✅ Cache carregado: {len(self._cache)} presentes mapeados.")

    async def reload_cache(self) -> None:
        """Recarrega o cache sem reiniciar o serviço."""
        logger.info("🔄 Recarregando cache do gift_map...")
        await self.load_cache()

    def get_cache_snapshot(self) -> dict:
        """Retorna uma cópia do cache atual (para debug/status)."""
        return dict(self._cache)

    # Processamento
    async def process_gift(
        self,
        tiktok_gift_id: int,
        gift_name: str,
        sender_username: str,
        repeat_count: int,
        raw_event: str = "{}",
    ) -> Optional[dict]:

        if not self._loaded:
            logger.warning("⚠️  Cache não carregado. Chamando load_cache()...")
            await self.load_cache()

        mapping = self._cache.get(tiktok_gift_id)

        if mapping is None:
            # Presente não mapeado: loga e descarta silenciosamente
            logger.debug(
                f"🎁 Presente não mapeado — gift_id={tiktok_gift_id} "
                f"name='{gift_name}' sender={sender_username}"
            )
            await self._persist_event(
                tiktok_gift_id=tiktok_gift_id,
                gift_name=gift_name,
                sender_username=sender_username,
                repeat_count=repeat_count,
                entity_id=None,
                points_awarded=0,
                raw_event=raw_event,
            )
            return None

        entity_id   = mapping["entity_id"]
        entity_name = mapping["entity_name"]
        point_value = mapping["point_value"]
        points      = point_value * repeat_count

        # Incremento atômico
        updated_score = await entity_repo.update_score(entity_id, points)

        # Persiste o log
        await self._persist_event(
            tiktok_gift_id=tiktok_gift_id,
            gift_name=gift_name,
            sender_username=sender_username,
            repeat_count=repeat_count,
            entity_id=entity_id,
            points_awarded=points,
            raw_event=raw_event,
        )

        logger.info(
            f"🎁 {sender_username} → '{gift_name}' ×{repeat_count} "
            f"| +{points} pts → {entity_name} "
            f"| Total: {updated_score.total_score}"
        )

        return {
            "entity_id":   entity_id,
            "entity_name": entity_name,
            "new_score":   updated_score.total_score,
            "gift_name":   gift_name,
            "points":      points,
            "sender":      sender_username,
        }

    # EventLog
    async def _persist_event(
        self,
        tiktok_gift_id: int,
        gift_name: str,
        sender_username: str,
        repeat_count: int,
        entity_id: Optional[int],
        points_awarded: int,
        raw_event: str,
    ) -> None:
        """Persiste o evento no EventLog."""
        try:
            from app.repositories import event_repository as event_repo
            await event_repo.create_event(
                tiktok_gift_id=tiktok_gift_id,
                gift_name=gift_name,
                sender_username=sender_username,
                repeat_count=repeat_count,
                entity_id=entity_id,
                points_awarded=points_awarded,
                raw_event=raw_event,
            )
        except Exception as e:
            # Log de erro
            logger.error(f"❌ Erro ao persistir EventLog: {e}")

# Singleton
score_engine = ScoreEngine()