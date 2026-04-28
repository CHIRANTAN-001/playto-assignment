import logging
import redis
from celery import shared_task
from django.db import connection
from common.env import env

logger = logging.getLogger(__name__)


@shared_task(name="common.tasks.ping_infrastructure")
def ping_infrastructure():
    """
    Periodic health probe for Postgres and Redis.
    Logs status at INFO level when healthy, ERROR level when a service is down.
    """
    results = {}

    # ── Postgres ──
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
        results["database"] = "up"
        logger.info("[ping_infrastructure] Postgres is reachable")
    except Exception as e:
        results["database"] = str(e)
        logger.error("[ping_infrastructure] Postgres is DOWN: %s", e)

    # ── Redis ──
    try:
        r = redis.from_url(str(env("REDIS_URL")))
        r.ping()
        results["redis"] = "up"
        logger.info("[ping_infrastructure] Redis is reachable")
    except Exception as e:
        results["redis"] = str(e)
        logger.error("[ping_infrastructure] Redis is DOWN: %s", e)

    return results
