import enum
import typing
import fastapi
import fastapi.security
import pydantic
from dependency_injector.wiring import inject, Provide

from app.media_type import MediaType
from app.services.room_service import RoomService, RoomUsersOrder
from app.services.auth_service import AuthorizationService
from app.services.message_service import MessageService
from app.models.chat_room import RoomType
from app.models.errors import ErrorRoomAlreadyExists, ErrorRoomAlreadyJoined, ErrorRoomInternalJoin, ErrorRoomInvalidTypeChange, ErrorRoomNameTooLong, ErrorRoomNotFound, ErrorRoomNotOwner, ErrorRoomPrivateJoin, ErrorRoomUserNotJoined, ErrorUserJWTExpired, ErrorUserJWTInvalid
from app.models.message import MessageIncoming, MessageType

class CreateRoomData(pydantic.BaseModel):
    name: str
    description: str | None
    type: RoomType

class UpdateRoomData(pydantic.BaseModel):
    name: str | None = None
    description: str | None = None
    type: RoomType | None = None

class PutRoomMessageData(pydantic.BaseModel):
    content: str
    type: MessageType

class CreateRoomResponse(pydantic.BaseModel):
    room_id: int

oauth2_scheme = fastapi.security.oauth2.OAuth2PasswordBearer(tokenUrl='auth/login')
router = fastapi.APIRouter(
    prefix='/room',
    tags=['room'])

@inject
def get_user_id_from_jwt(user_jwt: str = fastapi.Depends(oauth2_scheme),
                         auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service'])) -> int:
    return auth_service.decode_jwt(user_jwt)

@router.get(
    '/{room_id}',
    name='Get chat room')
@inject
async def get_room(room_id: int,
                   users_order: RoomUsersOrder = RoomUsersOrder.USERNAME,
                   room_service: RoomService = fastapi.Depends(Provide['room_service'])):
    return await room_service.get_room_by_id(room_id, users_order)

@router.put(
    '/{room_id}',
    name='Update room',
    responses={
        fastapi.status.HTTP_400_BAD_REQUEST: {'model': ErrorRoomInvalidTypeChange},
        fastapi.status.HTTP_409_CONFLICT: {'model': ErrorRoomAlreadyExists},
        fastapi.status.HTTP_404_NOT_FOUND: {'model': ErrorRoomNotFound},
        fastapi.status.HTTP_401_UNAUTHORIZED: {'model': typing.Union[ErrorRoomNotOwner, ErrorUserJWTExpired, ErrorUserJWTInvalid]}
    })
@inject
async def update_room(room_id: int,
                      data: UpdateRoomData,
                      user_id: int = fastapi.Depends(get_user_id_from_jwt),
                      room_service: RoomService = fastapi.Depends(Provide['room_service'])):
    await room_service.update_room(room_id, user_id, data.name, data.description, data.type)

@router.delete(
    '/{room_id}',
    name='Delete chat room')
@inject
async def delete_room(room_id: int,
                      user_id: int,
                      room_service: RoomService = fastapi.Depends(Provide['room_service'])):
    await room_service.delete_room(room_id, user_id)

@router.get(
    '/{room_id}/users',
    name='Get chat room users')
@inject
async def get_chat_room_users(room_id: int,
                              offset: int = 0,
                              limit: int = 10,
                              room_service: RoomService = fastapi.Depends(Provide['room_service'])):
    return await room_service.get_room_users(room_id, offset, limit)

# TODO Use websocket
@router.get(
    '/{room_id}/messages',
    name='Get last chat room messages')
@inject
async def get_last_room_messages(room_id: int,
                                 offset: int = 0,
                                 limit: int = 10,
                                 room_service: RoomService = fastapi.Depends(Provide['room_service'])):
    return await room_service.get_last_room_messages(room_id, offset, limit)

@router.post(
    '/{room_id}/messages',
    name='Send message to chat room',
    status_code=fastapi.status.HTTP_202_ACCEPTED,
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: {'model': ErrorRoomUserNotJoined},
        fastapi.status.HTTP_401_UNAUTHORIZED: {'model': typing.Union[ErrorUserJWTExpired, ErrorUserJWTInvalid]},
    })
@inject
async def put_room_message(room_id: int,
                           message_data: PutRoomMessageData,
                           user_id: int = fastapi.Depends(get_user_id_from_jwt),
                           room_service: RoomService = fastapi.Depends(Provide['room_service']),
                           message_service: MessageService = fastapi.Depends(Provide['message_service'])):
    await room_service.check_user_belongs_to(user_id, room_id)

    message = MessageIncoming(
        sender_id=user_id,
        room_id=room_id,
        content=message_data.content,
        type=message_data.type)
    await message_service.upload_message(message)

@router.get(
    '/{room_id}/image',
    name='Get chat room image')
@inject
async def get_room_image(room_id: int,
                         room_service: RoomService = fastapi.Depends(Provide['room_service'])):
    image_data = await room_service.get_room_image(room_id)

    content: bytes | None = None
    status_code = fastapi.status.HTTP_204_NO_CONTENT
    if image_data is not None:
        content = image_data
        status_code = fastapi.status.HTTP_200_OK

    return fastapi.Response(
        content=content,
        status_code=status_code,
        media_type=MediaType.IMAGE_JPEG)

@router.post(
    '/{room_id}/join',
    name='Join chat room',
    responses={
        fastapi.status.HTTP_401_UNAUTHORIZED: {'model': typing.Union[ErrorUserJWTExpired, ErrorUserJWTInvalid]},
        fastapi.status.HTTP_404_NOT_FOUND: {'model': ErrorRoomNotFound},
        fastapi.status.HTTP_400_BAD_REQUEST: {'model': typing.Union[ErrorRoomPrivateJoin, ErrorRoomInternalJoin]},
        fastapi.status.HTTP_409_CONFLICT: {'model': ErrorRoomAlreadyJoined},
    })
@inject
async def join_chat_room(room_id: int,
                         user_id: int = fastapi.Depends(get_user_id_from_jwt),
                         room_service: RoomService = fastapi.Depends(Provide['room_service'])):
    await room_service.join_room(room_id, user_id)

@router.post(
    '/',
    name='Create chat room',
    status_code=fastapi.status.HTTP_201_CREATED,
    response_model=CreateRoomResponse,
    responses={
        fastapi.status.HTTP_409_CONFLICT: {'model': ErrorRoomAlreadyExists},
        fastapi.status.HTTP_400_BAD_REQUEST: {'model': ErrorRoomNameTooLong},
        fastapi.status.HTTP_401_UNAUTHORIZED: {'model': typing.Union[ErrorUserJWTExpired, ErrorUserJWTInvalid]}
    })
@inject
async def create_room(data: CreateRoomData,
                      user_jwt: str = fastapi.Depends(oauth2_scheme),
                      auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service']),
                      room_service: RoomService = fastapi.Depends(Provide['room_service'])):
    user_id = auth_service.decode_jwt(user_jwt)
    room_id = await room_service.create_room(user_id, data.name, data.description, data.type)
    return CreateRoomResponse(room_id=room_id)
