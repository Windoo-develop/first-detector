import logging
from aiogram import Router

from .start import router as start_router
from .subscription import router as subscription_router
from .pcap import router as pcap_router
from .fallback import router as fallback_router


logger = logging.getLogger(__name__)

router = Router()


def register_handlers(main_router: Router) -> None:
    """
    Регистрирует все роутеры обработчиков.
    Функция используется при инициализации бота,
    чтобы централизованно подключать handlers.
    """

    routers_to_include = [
        start_router,
        subscription_router,
        pcap_router,
        fallback_router,
    ]

    for r in routers_to_include:
        try:
            main_router.include_router(r)
            logger.debug("Router %s registered", r)
        except Exception as error:
            logger.warning(
                "Failed to register router %s: %s",
                r,
                error
            )


# регистрация роутеров
register_handlers(router)