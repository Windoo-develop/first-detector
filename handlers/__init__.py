from aiogram import Router

from .start import router as start_router
from .subscription import router as subscription_router
from .pcap import router as pcap_router
from .fallback import router as fallback_router

router = Router()

router.include_router(start_router)
router.include_router(subscription_router)
router.include_router(pcap_router)
router.include_router(fallback_router)