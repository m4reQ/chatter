import sqlalchemy
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.models.user import APIUserForeign, SQLUser
from app.models.search_result import APIUsersSearchResult, APIRoomsSearchResult
from app.models.chat_room import APIChatRoomInfo, SQLChatRoom, RoomType
from app.models.chat_room_user import SQLChatRoomUser

class SearchService:
    def __init__(self, db_sessionmaker: async_sessionmaker[AsyncSession]):
        self._db_sessionmaker = db_sessionmaker
    
    async def search_users(self,
                           user_id: int | None,
                           phrase: str,
                           limit: int,
                           offset: int):
        async with self._db_sessionmaker() as session:
            query = (
                sqlalchemy.select(
                    SQLUser.id,
                    SQLUser.username,
                    SQLUser.accepts_friend_requests,
                    SQLUser.created_at,
                    SQLUser.last_active,
                    SQLUser.activity_status)
                .where(
                    SQLUser.username.ilike(f'%{phrase}%'),
                    SQLUser.id != user_id,
                    SQLUser.accepts_friend_requests == True)
                .order_by(SQLUser.username)
                .limit(limit)
                .offset(offset)
            )
            results = await session.execute(query)
            results = results.all()
            return APIUsersSearchResult(
                query=phrase,
                offset=offset,
                limit=limit,
                users=[APIUserForeign.model_validate(x) for x in results])
    
    async def search_rooms(self,
                           user_id: int | None,
                           phrase: str,
                           limit: int,
                           offset: int):
        async with self._db_sessionmaker() as session:
            query = (
                sqlalchemy.select(
                    SQLChatRoom.id,
                    SQLChatRoom.name,
                    SQLChatRoom.description)
                .where(
                    sqlalchemy.text('MATCH(name, description) AGAINST (:term IN NATURAL LANGUAGE MODE)'),
                    SQLChatRoom.type == RoomType.PUBLIC,
                    ~sqlalchemy.exists(1)
                        .where(
                            SQLChatRoomUser.room_id == SQLChatRoom.id,
                            SQLChatRoomUser.user_id == user_id))
                .order_by(SQLChatRoom.name)
                .limit(limit)
                .offset(offset)
                .params(term=phrase)
            )
            results = await session.execute(query)
            results = results.all()
            return APIRoomsSearchResult(
                query=phrase,
                offset=offset,
                limit=limit,
                rooms=[APIChatRoomInfo.model_validate(x) for x in results])