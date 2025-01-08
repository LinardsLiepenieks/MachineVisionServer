import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import logging
from channels.exceptions import DenyConnection, StopConsumer
import redis.asyncio as redis
from ..websocket_handling.ConsumerHandler import WebsocketConsumerHandler

"""TODO: EXTRACT A REDIS MANAGER CLASS WHICH POOLS CONNECTIONS AND RUNS SETUP"""


class ApiConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.initialize_redis()

        self.auth_type = self.scope.get("auth_type")
        self.auth_object = self.scope.get("auth_object")
        self.type_group = f"{self.auth_type}_group"

        self.setup_logger()

        if not await self._validate_auth():
            return

        await self.redis_client.sadd(self.type_group, self.channel_name)

        await WebsocketConsumerHandler.approve_connection(self)

    async def disconnect(self, close_code):
        if hasattr(self, "redis_client") and hasattr(self, "type_group"):
            try:
                await self.redis_client.srem(self.type_group, self.channel_name)
            except Exception as e:
                self.logger.error(f"Error removing from {self.type_group}: {str(e)}")

        if hasattr(self, "redis_client"):
            await self.redis_client.close()

        WebsocketConsumerHandler.close(self, close_code, reason="disconnected")

    async def receive(self, text_data):
        self.text_data_json = json.loads(text_data)
        self.message_type = self.text_data_json.get("type")

    async def initialize_redis(self):
        self.redis_client = redis.from_url("redis://localhost", decode_responses=True)
        self.channel_layer = get_channel_layer()

        if not self.channel_layer:
            raise DenyConnection("Redis channel layer is not configured")

    def setup_logger(self) -> None:
        """Configure instance-specific logger with additional context."""
        self.logger = logging.getLogger(f"{__name__}.{self.auth_type}")

    async def _validate_auth(self):
        if self.auth_type == "anonymous":
            raise DenyConnection("Anonymous connection attempt")
        if hasattr(self, "consumer_type") and self.consumer_type != self.auth_type:
            await WebsocketConsumerHandler.reject_route_mismatch(self)
            raise StopConsumer()
        return True

    def get_redis_key(self):
        raise NotImplementedError("Derived class must implement `get_redis_key` method")
