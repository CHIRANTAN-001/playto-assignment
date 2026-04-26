from django.db import connection
import redis
import sys
from common.env import env

def check_dependencies():
    # DB check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
        print("✅ Database is running and reachable")
    except Exception as e:
        print("\nERROR: Database is NOT running or not reachable")
        print("Check Postgres container / connection settings\n")
        sys.exit(1)
    
    # Redis check
    try:
        r = redis.from_url(str(env("REDIS_URL")))
        r.ping()
        print("✅ Redis is running and reachable")
    except Exception as e:
        print("\nERROR: Redis is NOT running or not reachable")
        print("Check Redis container / connection settings\n")
        sys.exit(1)