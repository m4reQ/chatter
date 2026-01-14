import pydantic

from app.models.user import APIUserForeign
from app.models.chat_room import APIChatRoomInfo

class APIBaseSearchResult(pydantic.BaseModel):
    query: str
    offset: int
    limit: int

class APIUsersSearchResult(APIBaseSearchResult):
    users: list[APIUserForeign]

class APIRoomsSearchResult(APIBaseSearchResult):
    rooms: list[APIChatRoomInfo]