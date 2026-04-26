from django.db import models

class UUIDv7(models.Func):
    function='uuidv7'

class UUIDExtractTimestamp(models.Func):
    function='uuid_extract_timestamp'