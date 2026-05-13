from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ModelConfig, ModelProvider


async def seed_model_configs(db: AsyncSession) -> None:
    """Seed default model provider and configs if not exist."""
    result = await db.execute(select(ModelProvider).where(ModelProvider.name == "zhipu"))
    if result.scalar_one_or_none():
        return

    provider = ModelProvider(
        name="zhipu",
        api_base_url="https://open.bigmodel.cn/api/paas/v4",
        api_key_encrypted="",
        status="active",
        priority=0,
    )
    db.add(provider)
    await db.flush()

    configs = [
        ModelConfig(
            provider_id=provider.id,
            model_name="glm-5.1",
            model_type="chat",
            capability="consult",
            input_price_per_m=7.0,
            output_price_per_m=26.0,
            max_tokens=8192,
            is_default=False,
            status="active",
        ),
        ModelConfig(
            provider_id=provider.id,
            model_name="glm-5-turbo",
            model_type="chat",
            capability="consult",
            input_price_per_m=5.0,
            output_price_per_m=24.0,
            max_tokens=4096,
            is_default=True,
            status="active",
        ),
        ModelConfig(
            provider_id=provider.id,
            model_name="glm-4-flash",
            model_type="chat",
            capability="router",
            input_price_per_m=0.0,
            output_price_per_m=0.0,
            max_tokens=4096,
            is_default=False,
            status="active",
        ),
        ModelConfig(
            provider_id=provider.id,
            model_name="embedding-3",
            model_type="embedding",
            capability=None,
            input_price_per_m=0.5,
            output_price_per_m=0.0,
            max_tokens=8192,
            is_default=True,
            status="active",
        ),
    ]
    for config in configs:
        db.add(config)
    await db.flush()
