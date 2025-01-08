from dataclasses import dataclass
from enum import Enum
from typing import Optional


@dataclass
class MachineInfo:
    id: int
    name: str
    key: str
    state: str


@dataclass
class ConnectionStatus:
    type: str = "machine_connection_status"
    status: str = "success"
    key: str = ""
    action: str = ""
    message: str = ""


class MachineState(Enum):
    DISCONNECT = "Disconnect"
    BUSY = "Busy"
    CONNECT = "Connect"
    OFFLINE = "Offline"

    @classmethod
    def get_connection_status(
        cls,
        machine_key: str,
        action: str,
        status: str,
        error_message: Optional[str] = None,
    ) -> ConnectionStatus:
        """Generate standardized connection status message"""
        message = (
            f"Successfully {action}ed to machine {machine_key}"
            if status == "success"
            else error_message or f"Failed to {action} to machine"
        )

        return ConnectionStatus(
            key=machine_key, action=action, status=status, message=message
        )

    @classmethod
    def determine_state(
        cls, channel_name: str, room_members: list[str], member_count: int
    ) -> str:
        if channel_name in room_members:
            return cls.DISCONNECT.value
        if member_count > 1:
            return cls.BUSY.value
        if member_count > 0:
            return cls.CONNECT.value
        return cls.OFFLINE.value

    @classmethod
    async def get_machine_status(
        cls, machine, room_manager, channel_name: str
    ) -> MachineInfo:
        """Get complete machine status including state determination"""
        room_members = await room_manager.get_room_members(machine.redis_key)
        member_count = await room_manager.get_room_count(machine.redis_key)

        return MachineInfo(
            id=machine.id,
            name=machine.name,
            key=machine.redis_key,
            state=cls.determine_state(channel_name, room_members, member_count),
        )
