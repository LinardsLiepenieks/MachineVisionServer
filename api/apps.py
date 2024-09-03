from django.apps import AppConfig
import spacy
import asyncio
import redis.asyncio as redis

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    nlp = None

    def ready(self):
        # Load the spaCy model when the app is ready
        self.nlp = spacy.load('en_core_web_sm')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.clear_redis())


    async def clear_redis(self):
        redis_client = redis.from_url('redis://127.0.0.1:6379')
        await redis_client.flushdb()  # Clears all data in the database

