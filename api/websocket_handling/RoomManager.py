class RoomManager:
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.active_rooms = set()

    def _get_room_name(self, machine_key: str) -> str:
        """Generate consistent room names"""
        return f"machine_{machine_key}_room"

    async def join_room(self, machine_key: str, channel_name: str) -> bool:
        """Add a member to a room"""
        room_name = self._get_room_name(machine_key)
        self.active_rooms.add(room_name)
        await self.redis_client.sadd(room_name, channel_name)
        return True

    async def leave_room(self, machine_key: str, channel_name: str) -> bool:
        """Remove a member from a room"""
        room_name = self._get_room_name(machine_key)
        self.active_rooms.remove(room_name)
        await self.redis_client.srem(room_name, channel_name)
        return True

    async def get_room_members(self, machine_key: str) -> set:
        """Get all members in a room"""
        room_name = self._get_room_name(machine_key)
        return await self.redis_client.smembers(room_name)

    async def can_join_room(self, machine_key: str, channel_name: str) -> bool:
        """Check if a channel can join a room"""
        room_members = await self.get_room_members(machine_key)
        return len(room_members) <= 1 or channel_name in room_members

    async def clear_member_from_all_rooms(self, channel_name: str) -> None:
        """Remove a member from all their active rooms"""
        for room_name in self.active_rooms.copy():
            await self.redis_client.srem(room_name, channel_name)
            self.active_rooms.remove(room_name)

    async def get_room_count(self, machine_key: str) -> int:
        """Get number of members in a room"""
        room_name = self._get_room_name(machine_key)
        return await self.redis_client.scard(room_name)
