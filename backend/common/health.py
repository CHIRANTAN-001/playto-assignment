from utils.response import api_response
from django.db import connection
import redis 
from common.env import env
from rest_framework import status as st
from rest_framework.request import Request
from rest_framework.views import APIView


class HealthCheckView(APIView):
    def get(self, request: Request):
        status="ok"
        checks={}
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
            checks["database"] = "up"
        except Exception as e:
            checks["database"] = str(e)
            status = "error"
            
        
        try:
            r = redis.from_url(str(env("REDIS_URL")))
            r.ping()
            checks["redis"] = "up"
        except Exception as e:
            checks["redis"] = str(e)
            status = "error"
        
        return api_response(data={"status": status, "checks": checks}, status_code=st.HTTP_200_OK if status == "ok" else st.HTTP_503_SERVICE_UNAVAILABLE)