import asyncio
import enum
import io
import os
import pathlib
import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.orm
import fastapi
from PIL import Image
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from app.models.chat_room import APIChatRoom, APIChatRoomUser, RoomType, SQLChatRoom
from app.models.chat_room_user import SQLChatRoomUser
from app.models.user import SQLUser, APIUserForeign
from app.models.errors import ErrorFileSaveFailed, ErrorImageInvalidType, ErrorRoomAlreadyExists, ErrorRoomAlreadyJoined, ErrorRoomDeleteInternal, ErrorRoomInternalJoin, ErrorRoomNameTooLong, ErrorRoomNotFound, ErrorRoomNotOwner, ErrorRoomPrivateJoin, ErrorRoomInvalidTypeChange, ErrorRoomUserNotJoined
from app.models.message import RoomMessage, SQLMessage

class RoomUsersOrder(enum.StrEnum):
    USERNAME = 'username'
    OWNERSHIP = 'ownership'
    JOIN_DATE = 'join_date'

class RoomService:
    def __init__(self,
                 db_sessionmaker: async_sessionmaker[AsyncSession],
                 data_directory: pathlib.Path,
                 room_image_size: int) -> None:
        self._db_sessionmaker = db_sessionmaker
        self._room_images_directory = data_directory / 'room_images'
        self._attachments_directory = data_directory / 'attachments'
        self._room_image_size = (room_image_size, room_image_size)

    async def delete_room(self, room_id: int, user_id: int):
        async with self._db_sessionmaker() as session:
            query = sqlalchemy.select(
                SQLChatRoom.type,
                sqlalchemy.func.if_(
                    SQLChatRoom.owner_id == user_id,
                    True,
                    False))
            room_type, is_owner = (await session.execute(query)).one()

            if room_type == RoomType.INTERNAL:
                ErrorRoomDeleteInternal(room_id) \
                    .raise_(fastapi.status.HTTP_400_BAD_REQUEST)
            
            if not is_owner:
                ErrorRoomNotOwner(room_id=room_id, user_id=user_id) \
                    .raise_(fastapi.status.HTTP_401_UNAUTHORIZED)
            
            query = sqlalchemy.delete(SQLChatRoom) \
                .where(SQLChatRoom.id == room_id)
            await session.execute(query)

            await session.commit()
    
    async def get_room_users(self, room_id: int, offset: int, limit: int):
        async with self._db_sessionmaker() as session:
            query = sqlalchemy.select(
                SQLChatRoomUser.user_id,
                SQLUser.username,
                SQLUser.activity_status,
                SQLUser.last_active,
                sqlalchemy.func.if_(
                    SQLChatRoomUser.user_id == SQLChatRoom.owner_id,
                    True,
                    False).label('is_owner')) \
                .join(SQLChatRoom, SQLChatRoom.id == SQLChatRoomUser.room_id) \
                .join(SQLUser, SQLUser.id == SQLChatRoomUser.user_id) \
                .where(SQLChatRoomUser.room_id == room_id) \
                .offset(offset) \
                .limit(limit)
            return [
                APIChatRoomUser.model_validate(x)
                for x
                in await session.execute(query)]
    
    async def get_last_room_messages(self, room_id: int, offset: int, limit: int):
        async with self._db_sessionmaker() as session:
            query = sqlalchemy.select(
                SQLMessage.id,
                SQLMessage.type,
                SQLMessage.content,
                SQLMessage.sent_at,
                SQLUser.id.label('sender_id'),
                SQLUser.username.label('sender_username')) \
                .join(SQLUser, SQLUser.id == SQLMessage.sender_id) \
                .where(SQLMessage.room_id == room_id) \
                .order_by(SQLMessage.sent_at.desc()) \
                .offset(offset) \
                .limit(limit)
            return [
                RoomMessage.model_validate(x)
                for x
                in (await session.execute(query)).all()]

    async def check_user_belongs_to(self, user_id: int, room_id: int):
        '''
        Checks if user joined the specified room before.

        :raises ErrorRoomUserNotJoined: If user doesn't belong to the specified room.
        '''
        
        async with self._db_sessionmaker() as session:
            query = sqlalchemy.select(
                sqlalchemy.exists()
                    .where(
                        SQLChatRoomUser.room_id == room_id,
                        SQLChatRoomUser.user_id == user_id))
            row_exists = (await session.execute(query)).scalar_one()
            if not row_exists:
                ErrorRoomUserNotJoined(user_id=user_id, room_id=room_id) \
                    .raise_(fastapi.status.HTTP_404_NOT_FOUND)

    async def update_room(self,
                          room_id: int,
                          user_id: int,
                          name: str | None = None,
                          description: str | None = None,
                          type: RoomType | None = None):
        async with self._db_sessionmaker() as session:
            query = sqlalchemy.select(SQLChatRoom) \
                .where(SQLChatRoom.id == room_id)
            room = await session.scalar(query)
            if room is None:
                self._raise_room_not_found(room_id)

            if room.owner_id != user_id:
                ErrorRoomNotOwner(room_id=room_id, user_id=user_id) \
                    .raise_(fastapi.status.HTTP_401_UNAUTHORIZED)
                
            if name is not None:
                room.name = name
            
            if description is not None:
                room.description = description

            if type is not None:
                if type == RoomType.INTERNAL:
                    ErrorRoomInvalidTypeChange(room_id=room_id, type=type) \
                        .raise_(fastapi.status.HTTP_400_BAD_REQUEST)

                room.type = type
            
            try:
                await session.commit()
            except sqlalchemy.exc.IntegrityError:
                ErrorRoomAlreadyExists(room_name=name) \
                    .raise_(fastapi.status.HTTP_409_CONFLICT)

    async def get_room_by_id(self, room_id: int, users_order: RoomUsersOrder) -> APIChatRoom:
        # TODO Implement room users ordering
        async with self._db_sessionmaker() as session:
            query = (
                sqlalchemy.select(SQLChatRoom)
                .where(SQLChatRoom.id == room_id)
                .options(
                    sqlalchemy.orm.selectinload(SQLChatRoom.users)
                        .selectinload(SQLChatRoomUser.user))
            )

            room = await session.scalar(query)

            if room is None:
                self._raise_room_not_found(room_id)
            
            return APIChatRoom(
                id=room.id,
                name=room.name,
                description=room.description,
                type=room.type,
                created_at=room.created_at,
                users=room.users)
        
    async def change_room_image(self, room_id: int, user_id: int, image_file: fastapi.UploadFile) -> None:
        async with self._db_sessionmaker() as session:
            query = (
                sqlalchemy.select(SQLChatRoom.owner_id)
                .where(SQLChatRoom.id == room_id))
            owner_id = (await session.execute(query)).scalar_one_or_none()
            if owner_id is None:
                ErrorRoomNotFound(room_id=room_id) \
                    .raise_(fastapi.status.HTTP_404_NOT_FOUND)
            
            if owner_id != user_id:
                ErrorRoomNotOwner(room_id=room_id, user_id=user_id) \
                    .raise_(fastapi.status.HTTP_401_UNAUTHORIZED)
            
        image_path = self._get_room_image_path(room_id)
        if image_path.exists():
            os.remove(image_path)
        
        try:
            await self._process_and_save_image(image_file.file, image_path)
        except Image.UnidentifiedImageError:
            ErrorImageInvalidType(image_file.content_type) \
                .raise_(fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        except Exception:
            ErrorFileSaveFailed() \
                .raise_(fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _process_and_save_image(self, file: io.BytesIO, filepath: pathlib.Path):
        return asyncio.to_thread(self._process_and_save_image_impl, file, filepath)

    def _process_and_save_image_impl(self, file: io.BytesIO, filepath: pathlib.Path) -> None:
        with Image.open(file) as img:
            img = img.resize(self._room_image_size, Image.Resampling.LANCZOS)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            img.save(filepath)
    
    async def create_room(self, owner_id: int, name: str, description: str | None, type: RoomType):
        async with self._db_sessionmaker(expire_on_commit=False) as session:
            room = SQLChatRoom(
                name=name,
                description=description,
                type=type,
                owner_id=owner_id)
            session.add(room)

            try:
                await session.flush()
            except sqlalchemy.exc.DataError:
                await session.rollback()

                ErrorRoomNameTooLong(room_name=name, room_description=description) \
                    .raise_(fastapi.status.HTTP_400_BAD_REQUEST)
            except sqlalchemy.exc.IntegrityError as e:
                await session.rollback()

                # TODO Check if error originates from user missing or conflicting room names
                ErrorRoomAlreadyExists(room_name=name) \
                    .raise_(fastapi.status.HTTP_409_CONFLICT)
            
            await session.refresh(room)

            room_user = SQLChatRoomUser(
                user_id=owner_id,
                room_id=room.id)
            session.add(room_user)

            # NOTE No need to check integrity here because potential conflict already happens at previous insert.
            # NOTE If an error happens here the database is in invalid state already.
            await session.commit()

            room_attachments_dir = self._attachments_directory / str(room.id)
            if not room_attachments_dir.exists():
                os.mkdir(room_attachments_dir)

            return room.id
    
    async def join_room(self, room_id: int, user_id: int):
        async with self._db_sessionmaker() as session:
            query = sqlalchemy.select(SQLChatRoom.type) \
                .where(SQLChatRoom.id == room_id)
            room_type = await session.scalar(query)
            if room_type is None:
                self._raise_room_not_found(room_id)

            if room_type == RoomType.PRIVATE:
                ErrorRoomPrivateJoin(room_id=room_id) \
                    .raise_(fastapi.status.HTTP_400_BAD_REQUEST)
            
            if room_type == RoomType.INTERNAL:
                ErrorRoomInternalJoin(room_id=room_id) \
                    .raise_(fastapi.status.HTTP_400_BAD_REQUEST)

            room_user = SQLChatRoomUser(
                room_id=room_id,
                user_id=user_id)
            session.add(room_user)

            try:
                await session.commit()
            except sqlalchemy.exc.IntegrityError:
                await session.rollback()

                # TODO Check if error comes from user or room not existing

                ErrorRoomAlreadyJoined(room_id=room_id, user_id=user_id) \
                    .raise_(fastapi.status.HTTP_409_CONFLICT)
                
    def _get_room_image_path(self, room_id: int) -> pathlib.Path:
        return self._room_images_directory / f'{room_id}.jpg'
    
    async def _ensure_room_exists_session(self, room_id: int, session: AsyncSession):
        query = sqlalchemy.select(sqlalchemy.exists().where(SQLChatRoom.id == room_id))
        if not await session.scalar(query):
            self._raise_room_not_found(room_id)
            
    def _raise_room_not_found(self, room_id: int):
        ErrorRoomNotFound(room_id=room_id) \
            .raise_(fastapi.status.HTTP_404_NOT_FOUND)
        
    async def _get_room_owner(self, owner_id: int | None, session: AsyncSession) -> APIUserForeign | None:
        if owner_id is None:
            return None
        
        query = sqlalchemy.select(SQLUser) \
            .where(SQLUser.id == owner_id)
        return APIUserForeign.model_validate(await session.scalar(query))
        
    async def _get_room_users(self, room_id: int, session: AsyncSession) -> list[APIUserForeign]:
        query = sqlalchemy.select(SQLUser) \
            .select_from(SQLChatRoomUser) \
            .where(SQLChatRoomUser.room_id == room_id) \
            .join(SQLUser, SQLUser.id == SQLChatRoomUser.user_id)
        return [APIUserForeign.model_validate(x) for x in await session.scalars(query)]