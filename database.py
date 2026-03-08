import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DB_PATH = "users.db"


def _get_connection():
    """
    Возвращает новое соединение с базой.
    Иногда SQLite ведёт себя странно при одном
    глобальном соединении, поэтому открываем
    его по мере необходимости.
    """
    try:
        return sqlite3.connect(DB_PATH)
    except Exception as err:
        logger.error("DB connection error: %s", err)
        raise


def init_db():
    """
    Инициализация таблицы пользователей.
    Вызывается один раз при запуске бота.
    """
    conn = _get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            language TEXT,
            subscribed INTEGER DEFAULT 0,
            subscribed_at TEXT
        )
        """)
        conn.commit()
    finally:
        conn.close()


def get_user(user_id: int):
    """
    Возвращает пользователя из базы.
    """
    conn = _get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT user_id, language, subscribed FROM users WHERE user_id = ?",
            (user_id,)
        )

        row = cur.fetchone()

        return row

    except Exception as err:
        logger.warning("get_user failed for %s: %s", user_id, err)
        return None

    finally:
        conn.close()


def create_or_update_user(user_id: int, language: str):
    """
    Создаёт пользователя или обновляет язык.
    """

    if not language:
        logger.debug("create_or_update_user called with empty language")
        return

    conn = _get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO users (user_id, language, subscribed)
        VALUES (?, ?, 0)
        ON CONFLICT(user_id)
        DO UPDATE SET language = excluded.language
        """, (user_id, language))

        conn.commit()

    except Exception as err:
        logger.error("user save failed (%s): %s", user_id, err)

    finally:
        conn.close()


def activate_subscription(user_id: int):
    """
    Активирует подписку пользователя.
    """

    conn = _get_connection()
    cur = conn.cursor()

    try:
        timestamp = datetime.utcnow().isoformat()

        cur.execute("""
        UPDATE users
        SET subscribed = 1,
            subscribed_at = ?
        WHERE user_id = ?
        """, (timestamp, user_id))

        conn.commit()

    except Exception as err:
        logger.error("subscription activation failed for %s: %s", user_id, err)

    finally:
        conn.close()


def is_subscribed(user_id: int) -> bool:
    """
    Проверяет активность подписки.
    """

    conn = _get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT subscribed FROM users WHERE user_id = ?",
            (user_id,)
        )

        result = cur.fetchone()

        if result is None:
            return False

        return bool(result[0])

    except Exception as err:
        logger.warning("subscription check failed: %s", err)
        return False

    finally:
        conn.close()