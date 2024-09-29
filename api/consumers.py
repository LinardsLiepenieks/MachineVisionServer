import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging
from channels.exceptions import DenyConnection, StopConsumer
from .messages.transcribe import speech_to_text
from .messages.analyze import find_object
import io
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
import redis.asyncio as redis

logger = logging.getLogger(__name__)

redis_client = redis.from_url("redis://localhost", decode_responses=True)

class ApiConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.channel_layer = get_channel_layer()
        if not self.channel_layer:
            self._log_and_deny("Channel layer is not configured")
        self.auth_type = self.scope.get('auth_type')
        self.auth_object = self.scope.get('auth_object')
        
        if not await self._validate_auth():
            return
        
        logger.error("FURTHER")
        self.type_group = f'{self.auth_type}_group'
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'auth_response',
            'message': f"{self.auth_type} {self.auth_object} successfully connected",
            'status': 'success'
        }))

    def _log_and_deny(self, message):
        logger.error(message)
        raise DenyConnection(message)

    async def _validate_auth(self):

        if self.auth_type == 'anonymous':
            self._log_and_deny("Anonymous connection attempt")
            return False
        if hasattr(self, 'consumer_type') and self.consumer_type != self.auth_type:
            await self.accept()
            await self.close(code=4003)
            raise StopConsumer()
        return True

    async def disconnect(self, close_code):
        logger.warning(f"Disconnecting with code {close_code}")
        if hasattr(self, 'type_group'):
            try:
                redis_key = self.get_redis_key()
                await redis_client.srem(self.type_group, self.channel_name)
            except Exception as e:
                logger.error(f"Error removing {redis_key} from {self.type_group}: {str(e)}")

    async def receive(self, text_data):
        self.text_data_json = json.loads(text_data)
        self.message_type = self.text_data_json.get('type')

    def get_redis_key(self):
        raise NotImplementedError("Derived class must implement `get_redis_key` method")


class UserConsumer(ApiConsumer):
    async def connect(self):
        logger.error("USERCONS")
        self.consumer_type = "user"
        self.search_group = "machine_group"
        self.machine_rooms = []
        await super().connect()
        logger.info(f"user {self.get_redis_key()} connected")
        await redis_client.sadd("user_group", self.channel_name)

    async def disconnect(self, close_code):
        for room in self.machine_rooms:
            await redis_client.srem(room, self.channel_name)
        self.machine_rooms = []
        logger.info(f"user {self.get_redis_key()} disconnected")
        await super().disconnect(close_code)

    async def receive(self, text_data, bytes_data=None):
        await super().receive(text_data)
        handler = {
            'analyze': self._handle_analyze,
            'transcribe': self._handle_transcribe,
            'reload_machines': self._handle_reload_machines,
            'connect_to_machine': self._handle_connect_to_machine,
            'disconnect_from_machine': self._handle_disconnect_from_machine
        }.get(self.message_type)

        if handler:
            await handler()

    async def _handle_analyze(self):
        text = self.text_data_json.get('text')
        analyzed_objects = await find_object(text)
        await self.send_messages(self.machine_rooms, "execute", analyzed_objects)

    async def _handle_transcribe(self):
        filename = self.text_data_json.get('filename')
        file_data = self.text_data_json.get('data')
        file_bytes = bytes(file_data.values())
        file = io.BytesIO(file_bytes)
        file.name = filename
        transcribed_text = speech_to_text(file, file_name=file.name)
        await self.send(text_data=json.dumps({
            'type': 'transcribe_response',
            'message': transcribed_text
        }))

    async def _handle_reload_machines(self, message=""):
        machine_list = await self.reload_machines()
        await self.send(text_data=json.dumps({
            'type': 'update_machines',
            'machines': machine_list
        }))

    async def _handle_connect_to_machine(self):
        logger.error("RECIEVED CONNECT TO MACHINE")
        machine_key = self.text_data_json.get('key')
        room_name = f"machine_{machine_key}_room"
        try:
            room_members = await redis_client.scard(room_name)
            if room_members > 1 and self.channel_name not in room_members:
                await self._send_machine_status('busy', f'The machine is currently busy', machine_key)
            else:
                self.machine_rooms.append(room_name)
                await redis_client.sadd(room_name, self.channel_name)
                await self._send_machine_status('success', f'Successfully connected to machine {machine_key}', machine_key)
                await self.notify_reload_machines()
        except Exception as e:
            await self._send_machine_status('error', f'Failed to connect to machine: {str(e)}', machine_key)

    async def _handle_disconnect_from_machine(self):
        machine_key = self.text_data_json.get('key')
        room_name = f"machine_{machine_key}_room"
        try:
            if room_name in self.machine_rooms:
                self.machine_rooms.remove(room_name)
                await redis_client.srem(room_name, self.channel_name)
            await self._send_machine_status('disconnected', f'Successfully disconnected from machine {machine_key}', machine_key)
            await self.notify_reload_machines()
        except Exception as e:
            await self._send_machine_status('error', f'Failed to disconnect from machine: {str(e)}', machine_key)

    async def _send_machine_status(self, status, message, key):
        logger.error(f"{status} {key}")
        await self.send(text_data=json.dumps({
            'type': 'machine_connection_status',
            'status': status,
            'message': message,
            'key': key
        }))
    
    async def handle_reload_machines(self, message=""):
        machine_list = await self.reload_machines()
        await self.send(text_data=json.dumps({
            'type': 'update_machines',
            'machines': machine_list
        }))

    async def execute(self, message=""):
        self.analyzed_objects = message
    
    async def send_messages(self, rooms, type, message):
        for room in rooms:
            room_members = await redis_client.smembers(room)
            for member in room_members:
                await self.channel_layer.send(member, {
                    'type': type,
                    'message': message,
                })

    def get_redis_key(self):
        return self.auth_object.profile.redis_key

    async def reload_machines(self, test=""):
        machines = await self.get_machines()
        # Get all machines from db
        machine_list = [{'id': machine.id, 'name': machine.name, 'key': machine.redis_key, 'state': 'Offline'} for machine in machines]

        # Prepare a Redis pipeline to fetch room member counts
        pipeline = redis_client.pipeline()
        room_names = [f"machine_{machine['key']}_room" for machine in machine_list]
        
        # Use pipeline to execute multiple commands in one go
        for room_name in room_names:
            pipeline.scard(room_name)
        
        room_member_counts = await pipeline.execute()
        
        # Map room names to their member counts
        room_member_count_map = dict(zip(room_names, room_member_counts))

        for machine in machine_list:
            room_name = f"machine_{machine['key']}_room"
            room_members = room_member_count_map.get(room_name, 0)

            if room_name in self.machine_rooms:
                machine['state'] = 'Disconnect'
            elif room_members > 1:
                machine['state'] = 'Busy'
            elif room_members > 0:
                machine['state'] = 'Connect'

        return machine_list

    async def machine_connected(self, event):
        machine_key = event['key']
        logger.error(f"Machine with key {machine_key} connected")
        await self._update_machines()

    async def machine_disconnected(self, event):
        machine_key = event['key']
        room_name = f"machine_{machine_key}_room"
        if room_name in self.machine_rooms:
            self.machine_rooms.remove(room_name)
        await self._update_machines()

    async def _update_machines(self):
        self.machine_list = await self.reload_machines()
        #logger.error("MACHINE LIST", self.machine_list)
        await self.send(text_data=json.dumps({
            'type': 'update_machines',
            'machines': self.machine_list
        }))

    async def send_messages(self, rooms, type, message):
        for room in rooms:
            room_members = await redis_client.smembers(room)
            for member in room_members:
                await self.channel_layer.send(member, {
                    'type': type,
                    'message': message,
                })

    async def notify_reload_machines(self):
        # Get all users in the user_group
        user_group = 'user_group'
        current_user_channel = self.channel_name

        # Get all users (channels) in the group
        all_users = await redis_client.smembers(user_group)

        # Filter out the current user's channel
        users_to_notify = [user for user in all_users if user != current_user_channel]

        # Send a reload message to all other users
        for user in users_to_notify:
            await self.channel_layer.send(user, {
                'type': 'handle_reload_machines',
            })

    def get_redis_key(self):
        return self.auth_object.profile.redis_key

    @sync_to_async
    def get_machine_keys(self):
        machines = self.auth_object.profile.machines.all()
        return [machine.redis_key for machine in machines]

    @sync_to_async
    def get_machines(self):
        return list(self.auth_object.profile.machines.all())

    async def check_connected_machines(self, search_group, keys):
        connections = await redis_client.smembers(search_group)
        return list(set(connections) & set(keys))


class MachineConsumer(ApiConsumer):
    async def connect(self):
        self.consumer_type = "machine"
        self.search_group = "user_group"
        self.machine_room = ""

        await super().connect()

        self.machine_room = f"machine_{self.get_redis_key()}_room"
        await self._join_machine_room()
        await self._notify_group(self.search_group, 'machine_connected')

    async def _join_machine_room(self):
        await redis_client.sadd(self.machine_room, self.channel_name)

    async def _notify_group(self, group, event_type):
        room_members = await redis_client.smembers(group)
        for member in room_members:
            await self.channel_layer.send(member, {
                'type': event_type,
                 'key': self.get_redis_key(),
                })


    async def disconnect(self, close_code):
        await redis_client.srem(self.machine_room, self.channel_name)
        await self._notify_group(self.search_group, 'machine_disconnected')
        await redis_client.delete(self.machine_room)
        await super().disconnect(close_code)

    async def execute(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'execute_response',
            'result': 'Executed successfully',
            'message': message,
        }))

    def get_redis_key(self):
        return self.auth_object.redis_key