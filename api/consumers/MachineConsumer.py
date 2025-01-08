from .ApiConsumer import ApiConsumer
from ..websocket_handling.ConsumerHandler import WebsocketConsumerHandler
from ..websocket_handling.RoomManager import RoomManager


class MachineConsumer(ApiConsumer):
    async def connect(self):
        await super().connect()
        self.room_manager = RoomManager(self.redis_client)

        await self.room_manager.join_room(self.get_redis_key(), self.channel_name)

    async def disconnect(self, close_code):
        await self.room_manager.clear_member_from_all_rooms(self.channel_name)
        await self._notify_group("user_group", "machine_disconnected")
        await super().disconnect(close_code)

    async def receive(self, text_data, bytes_data=None):

        await super().receive(text_data)

        handler = {
            # Add other handlers here as needed for consumer messages
        }.get(self.message_type)

        if handler:
            await handler()

    # redis handlers
    async def nlp_response(self, event):
        data = event.get("message")
        await WebsocketConsumerHandler.send_json_message(
            self,
            type="analyze",
            message=f"{self.auth_type} {self.auth_object} successfully responded",
            status="success",
            data=data,
        )

    async def _notify_group(self, group, event_type):
        room_members = await self.redis_client.smembers(group)
        for member in room_members:
            await self.channel_layer.send(
                member,
                {
                    "type": event_type,
                    "key": self.get_redis_key(),
                },
            )

    def get_redis_key(self):
        return self.auth_object.redis_key
