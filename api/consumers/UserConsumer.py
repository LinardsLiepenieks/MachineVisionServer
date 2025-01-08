import json
from asgiref.sync import sync_to_async
from .ApiConsumer import ApiConsumer
from ..messages.transcribe.transcribers.silero import SileroTranscriber
from ..messages.transcribe.processors.base import AudioProcessor
from ..messages.transcribe.processors.metrics import AudioChunk
from ..messages.analyze.Text_analyzer import TextAnalyzer
from ..websocket_handling.ConsumerHandler import WebsocketConsumerHandler
from ..websocket_handling.RoomManager import RoomManager
from ..states.machine_states import MachineState
from ..websocket_handling.codes import WebSocketCloseCodes
from ..websocket_handling.error_handler import ClientError


class UserConsumer(ApiConsumer):
    async def connect(self):
        await super().connect()
        self.room_manager = RoomManager(self.redis_client)
        self.transcriber = SileroTranscriber()
        self.audio_processor = AudioProcessor(transcriber=self.transcriber)
        self.text_analyzer = TextAnalyzer()

    async def disconnect(self, close_code: WebSocketCloseCodes):
        await self.room_manager.clear_member_from_all_rooms(self.channel_name)
        await super().disconnect(close_code)

    async def receive(self, text_data: str):
        await super().receive(text_data)
        self.message_handlers = {
            "nlp_analyze": self._handle_analyze,
            "connect_to_machine": self._handle_connect_to_machine,
            "disconnect_from_machine": self._handle_disconnect_from_machine,
            "reload_machines": self._handle_reload_machines,
            "transcribe_audio": self._handle_transcribe_audio,
        }

        handler = self.message_handlers.get(self.message_type)
        if handler:
            await handler()

    async def _handle_analyze(self):
        try:
            input_text = self.text_data_json.get("text")
            if not input_text:
                raise ValueError("Missing text input")
            nlp_result = await self.text_analyzer.analyze_text(input_text)
            await self._notify_connected_machines("nlp_response", nlp_result)
        except Exception as e:
            error_response = ClientError.handle_error(e, self.logger)
            await WebsocketConsumerHandler.send_json_message(self, **error_response)

    async def _handle_connect_to_machine(self):
        try:
            machine_key = self.text_data_json.get("key")
            if not machine_key:
                raise ValueError("Missing machine key")

            if await self.room_manager.can_join_room(machine_key, self.channel_name):
                await self.room_manager.join_room(machine_key, self.channel_name)
                status = MachineState.get_connection_status(
                    machine_key, "connect", "success"
                )
                await WebsocketConsumerHandler.send_json_message(self, **vars(status))
            else:
                raise ResourceWarning("Machine is busy")
        except Exception as e:
            error_response = ClientError.handle_error(e, self.logger)
            await WebsocketConsumerHandler.send_json_message(self, **error_response)

    async def _handle_disconnect_from_machine(self):
        machine_key = self.text_data_json.get("key")
        try:
            await self.room_manager.leave_room(machine_key, self.channel_name)
            status = MachineState.get_connection_status(
                machine_key, "disconnect", "success"
            )
            await WebsocketConsumerHandler.send_json_message(self, **vars(status))
        except Exception as e:
            status = MachineState.get_connection_status(
                machine_key, "disconnect", "error", str(e)
            )
            await WebsocketConsumerHandler.send_json_message(self, **vars(status))

    async def _handle_reload_machines(self):
        machine_list = await self._get_machine_states()
        await WebsocketConsumerHandler.send_json_message(
            self, type="update_machines", machines=machine_list
        )
        await self._notify_other_users()

    async def _handle_transcribe_audio(self):
        try:
            if not self.text_data_json:
                raise ValueError("Invalid audio data format")
            chunk = AudioChunk.from_dict(self.text_data_json)
            metrics, transcription = self.audio_processor.process_chunk(chunk)
            print(metrics)

            if transcription:
                await WebsocketConsumerHandler.send_json_message(
                    self,
                    type="transcribe_response",
                    chunk_index=chunk.chunk_index,
                    metrics=metrics.to_dict(),
                    message=transcription,
                )
        except Exception as e:
            error_response = ClientError.handle_error(e, self.logger)
            await self.send(json.dumps(error_response))

    # redis (channel_layer) handlers
    async def machine_disconnected(self, event):
        try:
            machine_key = event.get("key")
            status = MachineState.get_connection_status(
                machine_key, "disconnect", "success"
            )
            await WebsocketConsumerHandler.send_json_message(self, **vars(status))
            machine_list = await self._get_machine_states()
            await WebsocketConsumerHandler.send_json_message(
                self, type="update_machines", machines=machine_list
            )
        except Exception as e:
            self.logger.error(f"Error handling machine disconnect: {str(e)}")

    # utility functions
    async def _get_machine_states(self):
        machines = await self._get_machines()
        machine_states = []

        for machine in machines:
            machine_info = await MachineState.get_machine_status(
                machine, self.room_manager, self.channel_name
            )
            machine_states.append(vars(machine_info))

        return machine_states

    @sync_to_async
    def _get_machines(self) -> list:
        return list(self.auth_object.profile.machines.all())

    async def _notify_other_users(self):
        user_group = "user_group"
        all_users = await self.redis_client.smembers(user_group)
        other_users = [user for user in all_users if user != self.channel_name]

        for user in other_users:
            await self.channel_layer.send(user, {"type": "handle_reload_machines"})

    async def _notify_connected_machines(self, type_: str, payload=None, status=None):
        # Get all rooms the user is in from room_manager
        for room_name in self.room_manager.active_rooms:
            try:
                room_members = await self.redis_client.smembers(room_name)
                room_members = [m for m in room_members if m != self.channel_name]
                for member in room_members:
                    await self.channel_layer.send(
                        member, {"type": type_, "message": payload, "status": status}
                    )
            except Exception as e:
                self.logger.error(f"Error notifying room {room_name}: {str(e)}")

    def get_redis_key(self) -> str:
        return self.auth_object.profile.redis_key
