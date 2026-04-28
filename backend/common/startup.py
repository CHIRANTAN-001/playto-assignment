from django.db import connection
import socket
import sys
from urllib.parse import urlparse
from common.env import env
import logging
import redis

logger = logging.getLogger(__name__)

def check_dependencies():
    # DB check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
        logger.info("✅ Database is running and reachable")
    except Exception as e:
        logger.error("\nERROR: Database is NOT running or not reachable")
        return
    
    # Redis check
    try:
        r = redis.from_url(str(env("REDIS_URL")))
        r.ping()
        logger.info("✅ Redis is running and reachable")
    except Exception as e:
        logger.error("\nERROR: Redis is NOT running or not reachable")
        sys.exit(1)