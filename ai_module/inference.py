from ai_module.models.generate_profile import generate_profile as generate_profile_impl
from ai_module.models.generate_head import generate_structured_head as generate_head_impl
import logging
from typing import Dict

logger = logging.getLogger(__name__)

async def generate_profile(text: str) -> Dict:
    """
    Wrapper pour generate_profile
    """
    return await generate_profile_impl(text)

async def generate_head(text: str) -> Dict:
    """
    Wrapper pour generate_head
    """
    return await generate_head_impl(text)
