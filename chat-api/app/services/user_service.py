import datetime
import asyncio
import os
import pathlib
import fastapi
import typing as t
import sqlalchemy
import sqlalchemy.orm
from PIL import Image
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from app.models.errors import ErrorFriendRequestNotFound, ErrorProfilePictureInvalidType, ErrorProfilePictureSaveFailed, ErrorSelfFriendRequest, ErrorUserNotFoundID
from app.models.user import APIUserForeign, SQLUser, APIUserSearchResult, UserActivityStatus
from app.models.friend_request import APIFriendRequest, SQLFriendRequest
from app.models.friend import APIFriend, SQLFriend, APIFriendActivity
from app.models.chat_room import APIUserChatRoom, SQLChatRoom
from app.models.chat_room_user import SQLChatRoomUser

class UserService:
    def __init__(self,
                 db_session_factory: async_sessionmaker[AsyncSession],
                 data_directory: pathlib.Path,
                 profile_picture_size: int) -> None:
        self._db_session_factory = db_session_factory
        self._profile_pictures_directory = data_directory / 'profile_pictures'
        self._profile_picture_size = profile_picture_size

        if not self._profile_pictures_directory.exists():
            os.makedirs(self._profile_pictures_directory)

    async def get_user(self, user_id: int) -> SQLUser:
        return await self._get_user_by_id(user_id)
    
    async def get_user_email_info(self, user_id: int) -> tuple[str, bool]:
        async with self._db_session_factory() as session:
            query = sqlalchemy.select(SQLUser.email, SQLUser.is_email_verified) \
                .where(SQLUser.id == user_id)
            result = await session.execute(query)
            result = result.one_or_none()
            if result is None:
                self._raise_user_not_found(user_id)

            return result
        
    async def create_friend_request(self, id_from: int, id_to: int):
        if id_from == id_to:
            ErrorSelfFriendRequest(id_from=id_from, id_to=id_to) \
                .raise_(fastapi.status.HTTP_400_BAD_REQUEST)
            
        async with self._db_session_factory() as session:
            request = SQLFriendRequest(sender_id=id_from, receiver_id=id_to)
            session.add(request)

            # TODO Check integrity error (user does not exist, request already sent)
            await session.commit()

    async def process_friend_request(self, user_id: int, from_id: int, accept: bool):
        async with self._db_session_factory() as session:
            query = sqlalchemy.select(SQLFriendRequest) \
                .where(
                    sqlalchemy.and_(
                        SQLFriendRequest.receiver_id == user_id,
                        SQLFriendRequest.sender_id == from_id))
            friend_request = (await session.execute(query)).scalar_one_or_none()
            if friend_request is None:
                ErrorFriendRequestNotFound(user_id=user_id, from_id=from_id) \
                    .raise_(fastapi.status.HTTP_404_NOT_FOUND)
                            
            if accept:
                session.add(SQLFriend(user_id=user_id, friend_id=from_id))
                session.add(SQLFriend(user_id=from_id, friend_id=user_id))
                
            await session.delete(friend_request)

            await session.commit()
    
    async def get_user_rooms(self, user_id: int) -> list[APIUserChatRoom]:
        async with self._db_session_factory() as session:
            await self._ensure_user_exists_session(user_id, session)

            query = (
                sqlalchemy.select(SQLChatRoom)
                    .select_from(SQLChatRoomUser)
                    .join(SQLChatRoom, SQLChatRoom.id == SQLChatRoomUser.room_id)
                    .where(SQLChatRoomUser.user_id == user_id)
                    .options(sqlalchemy.orm.selectinload(SQLChatRoom.last_message))
            )
            
            return [
                APIUserChatRoom.model_validate(x)
                for x
                in await session.scalars(query)]
    
    async def search_users_by_username(self,
                                       self_id: int,
                                       username: str,
                                       limit: int = 20,
                                       offset: int = 0) -> APIUserSearchResult:
        # NOTE Use FULLTEXT index when search becomes slow
        async with self._db_session_factory() as session:
            query = sqlalchemy.select(
                SQLUser.id,
                SQLUser.username,
                SQLUser.activity_status,
                SQLUser.last_active,
                SQLUser.created_at) \
                .where(
                    sqlalchemy.and_(
                        SQLUser.username.ilike(f'%{username}%'),
                        SQLUser.id != self_id)) \
                .order_by(SQLUser.username) \
                .limit(limit) \
                .offset(offset)
            results = (await session.execute(query)).all()

            return APIUserSearchResult(
                query=username,
                offset=offset,
                limit=limit,
                users=[APIUserForeign.model_validate(x) for x in results])
    
    async def get_user_friends_activity(self, user_id: int) -> list[APIFriendActivity]:
        async with self._db_session_factory() as session:
            query = sqlalchemy.select(
                SQLUser.id,
                SQLUser.activity_status,
                sqlalchemy.literal_column('1', sqlalchemy.Boolean).label('user_exists')) \
                .select_from(SQLUser) \
                .outerjoin(SQLFriend, SQLFriend.friend_id == SQLUser.id) \
                .outerjoin(SQLUser.__table__.alias('f'), SQLFriend.friend_id == sqlalchemy.literal_column('f.id')) \
                .where(SQLUser.id == user_id)
            
            rows = (await session.execute(query)).all()
            if not rows:
                self._raise_user_not_found(user_id)

            return [APIFriendActivity.model_validate(x) for x in rows]
        
    async def get_user_friends(self, user_id: int) -> list[APIFriend]:
        async with self._db_session_factory() as session:
            self._ensure_user_exists_session(user_id, session)

            query = sqlalchemy.select(
                SQLUser.id.label('user_id'),
                SQLUser.username,
                SQLUser.last_active,
                SQLUser.activity_status) \
                .join(SQLFriend, SQLFriend.friend_id == SQLUser.id) \
                .where(SQLFriend.user_id == user_id) \
                .order_by(SQLUser.activity_status)
            results = (await session.execute(query)).all()

            return [APIFriend.model_validate(x) for x in results]
    
    async def get_user_profile_picture(self, user_id: int) -> bytes | None:
        await self._ensure_user_exists(user_id)

        profile_picture_path = self._get_profile_picture_path(user_id)
        if profile_picture_path.exists():
            return await self._read_profile_picture(profile_picture_path)
        
        return None
    
    def delete_user_profile_picture(self, user_id: int) -> None:
        self._ensure_user_exists(user_id)
        self._delete_user_profile_picture(user_id)
    
    async def change_user_activity_status(self,
                                          user_id: int,
                                          status: UserActivityStatus,
                                          now: datetime.datetime) -> tuple[UserActivityStatus, datetime.datetime]:
        async with self._db_session_factory(expire_on_commit=False) as session:
            user = await self._get_user_by_id_session(user_id, session)
            user.user_activity_status = status
            user.last_active = now
            
            await session.flush()
            await session.refresh(user)

            await session.commit()
            
            return (user.activity_status, user.last_active)
        
    async def refresh_user_activity(self, user_id: int, now: datetime.datetime) -> None:
        async with self._db_session_factory() as session:
            user = await self._get_user_by_id_session(user_id, session)
            user.last_active = now

            await session.commit()
        
    async def change_user_profile_picture(self, user_id: int, image_file: fastapi.UploadFile) -> None:
        await self._ensure_user_exists(user_id)

        profile_picture_path = self._get_profile_picture_path(user_id)
        if profile_picture_path.exists():
            await self._remove_profile_picture(user_id)

        try:
            with Image.open(image_file.file) as img:
                img = img.resize(
                    size=(self._profile_picture_size, self._profile_picture_size),
                    resample=Image.Resampling.LANCZOS)
                
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                img.save(self._get_profile_picture_path(user_id))
        except Image.UnidentifiedImageError:
            ErrorProfilePictureInvalidType(image_file.content_type) \
                .raise_(fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        except Exception:
            ErrorProfilePictureSaveFailed() \
                .raise_(fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def get_user_friend_requests(self, user_id: int) -> list[APIFriendRequest]:
        async with self._db_session_factory() as session:
            # TODO Use single query for user existence like in friends activity list
            await self._ensure_user_exists_session(user_id, session)

            query = sqlalchemy.select(
                SQLFriendRequest.sender_id.label('user_id'),
                SQLUser.username,
                SQLUser.activity_status,
                SQLUser.last_active) \
                .join(SQLUser, SQLUser.id == SQLFriendRequest.sender_id) \
                .where(SQLFriendRequest.receiver_id == user_id) \
                .order_by(SQLFriendRequest.sent_at)
            results = await session.execute(query)
            return [APIFriendRequest.model_validate(x) for x in results.all()]
    
    async def _ensure_user_exists_session(self, user_id: int, session: AsyncSession) -> None:
        query = sqlalchemy.select(sqlalchemy.exists().where(SQLUser.id == user_id))
        if not await session.scalar(query):
            self._raise_user_not_found(user_id)
        
    async def _ensure_user_exists(self, user_id: int) -> None:
        async with self._db_session_factory() as session:
            await self._ensure_user_exists_session(user_id, session)

    def _get_profile_picture_path(self, user_id: int) -> pathlib.Path:
        return (self._profile_pictures_directory / str(user_id)).with_suffix('.jpg')

    async def _get_user_by_id_session(self, user_id: int, session: AsyncSession) -> SQLUser:
        query = sqlalchemy.Select(SQLUser).where(SQLUser.id == user_id)
        user = (await session.execute(query)).scalar_one_or_none()
        
        if user is None:
            self._raise_user_not_found(user_id)

        return user
        
    async def _get_user_by_id(self, user_id: int) -> SQLUser:
        async with self._db_session_factory() as session:
            return await self._get_user_by_id_session(user_id, session)

    def _raise_user_not_found(self, user_id: int) -> t.NoReturn:
        ErrorUserNotFoundID(user_id=user_id) \
            .raise_(fastapi.status.HTTP_404_NOT_FOUND)
        
    async def _read_profile_picture(self, path: pathlib.Path):
        return await asyncio.to_thread(path.read_bytes)
        
    async def _remove_profile_picture(self, path: pathlib.Path):
        await asyncio.to_thread(os.remove, path)

    async def _delete_user_profile_picture(self, user_id: int) -> None:
        profile_picture_path = self._get_profile_picture_path(user_id)
        if profile_picture_path.exists():
            await self._remove_profile_picture(profile_picture_path)