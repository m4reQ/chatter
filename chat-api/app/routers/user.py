import os
import pydantic
import datetime
import fastapi
import fastapi.security
from dependency_injector.wiring import Provide, inject

from app.services import UserService, AuthorizationService, DatetimeService
from app.models.user import APIUserForeign, APIUserSelf, SQLUser, UserActivityStatus
from app.models.errors import ErrorFriendRequestAlreadySent, ErrorSelfFriendRequest, ErrorUserNotFoundID
from app.media_type import MediaType

class ChangeUserActivityStatusResponse(pydantic.BaseModel):
    activity_status: UserActivityStatus
    last_active: datetime.datetime
    message: str = 'Successfully changed user activity status.'

class SendFriendRequestResponse(pydantic.BaseModel):
    message: str = 'Sent friend request.'

class AcceptFriendRequestResponse(pydantic.BaseModel):
    message: str = 'Friend request accepted.'

class RejectFriendRequestResponse(pydantic.BaseModel):
    message: str = 'Friend request rejected.'

oauth2_scheme = fastapi.security.oauth2.OAuth2PasswordBearer(tokenUrl='auth/login')
router = fastapi.APIRouter(
    prefix='/user',
    tags=['user'])

@inject
async def get_user_from_jwt(user_jwt: str = fastapi.Depends(oauth2_scheme),
                            auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service']),
                            user_service: UserService = fastapi.Depends(Provide['user_service'])):
    return await user_service.get_user(auth_service.decode_jwt(user_jwt))

@inject
def get_user_id_from_jwt(user_jwt: str = fastapi.Depends(oauth2_scheme),
                         auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service'])) -> int:
    return auth_service.decode_jwt(user_jwt)

@router.get(
    '/',
    name='Get user')
async def get_user(user: SQLUser = fastapi.Depends(get_user_from_jwt)) -> APIUserSelf:
    '''
    Retrieves basic informations about the user
    '''

    return APIUserSelf.model_validate(user)

@router.put(
    '/change-activity-status/{status}',
    name='Change user activity status')
@inject
async def change_user_activity_status(status: UserActivityStatus,
                                      user_id: int = fastapi.Depends(get_user_id_from_jwt),
                                      user_service: UserService = fastapi.Depends(Provide['user_service']),
                                      datetime_service: DatetimeService = fastapi.Depends(Provide['datetime_service'])):
    activity_status, last_active = await user_service.change_user_activity_status(
        user_id,
        status,
        datetime_service.get_datetime_utc_now())
    return ChangeUserActivityStatusResponse(
        activity_status=activity_status,
        last_active=last_active)

@router.put(
    '/refresh-activity',
    name='Refresh activity',
    status_code=fastapi.status.HTTP_204_NO_CONTENT)
@inject
async def refresh_user_activity(user_id: int = fastapi.Depends(get_user_id_from_jwt),
                                user_service: UserService = fastapi.Depends(Provide['user_service']),
                                datetime_service: DatetimeService = fastapi.Depends(Provide['datetime_service'])):
    await user_service.refresh_user_activity(user_id, datetime_service.get_datetime_utc_now())

@router.get('/profile-picture')
@inject
async def get_user_profile_picture(user_id: int = fastapi.Depends(get_user_id_from_jwt),
                                   data_directory: str = fastapi.Depends(Provide['config.fs.data_directory'])):
    filepath = os.path.join(data_directory, 'profile_pictures', str(user_id) + '.jpg')
    if not os.path.exists(filepath):
        return fastapi.Response(
            content=None,
            status_code=fastapi.status.HTTP_204_NO_CONTENT,
            media_type=MediaType.IMAGE_JPEG)
    
    return fastapi.responses.FileResponse(
        filepath,
        media_type=MediaType.IMAGE_JPEG)

@router.put('/profile-picture')
@inject
async def change_user_profile_picture(image_file: fastapi.UploadFile,
                                      user_id: int = fastapi.Depends(get_user_id_from_jwt),
                                      user_service: UserService = fastapi.Depends(Provide['user_service'])):
    await user_service.change_user_profile_picture(user_id, image_file)
    return {'message': 'Successfully changed user profile picture'}

@router.delete('/profile-picture')
@inject
async def delete_user_profile_picture(user_id: int = fastapi.Depends(get_user_id_from_jwt),
                                      user_service: UserService = fastapi.Depends(Provide['user_service'])):
    user_service.delete_user_profile_picture(user_id)
    return {'message': 'Successfully deleted user profile picture'}

@router.get('/friends')
@inject
async def get_user_friends(user_id: int = fastapi.Depends(get_user_id_from_jwt),
                           user_service: UserService = fastapi.Depends(Provide['user_service'])):
    return await user_service.get_user_friends(user_id)

@router.get('/friend-requests')
@inject
async def get_user_friend_requests(user_id: int = fastapi.Depends(get_user_id_from_jwt),
                                   user_service: UserService = fastapi.Depends(Provide['user_service'])):
    return await user_service.get_user_friend_requests(user_id)

@router.post(
    '/send-friend-request/{to_id}',
    name='Send friend request',
    status_code=fastapi.status.HTTP_201_CREATED,
    responses={
        fastapi.status.HTTP_400_BAD_REQUEST: {'model': ErrorSelfFriendRequest},
        fastapi.status.HTTP_404_NOT_FOUND: {'model': ErrorUserNotFoundID},
        fastapi.status.HTTP_409_CONFLICT: {'model': ErrorFriendRequestAlreadySent}
    })
@inject
async def send_friend_request(to_id: int,
                              user_id: int = fastapi.Depends(get_user_id_from_jwt),
                              user_service: UserService = fastapi.Depends(Provide['user_service'])):
    await user_service.create_friend_request(user_id, to_id)
    return SendFriendRequestResponse()

@router.post(
    '/accept-friend-request/{from_id}',
    name='Accept friend request')
@inject
async def accept_friend_request(from_id: int,
                                user_id: int = fastapi.Depends(get_user_id_from_jwt),
                                user_service: UserService = fastapi.Depends(Provide['user_service'])):
    await user_service.process_friend_request(user_id, from_id, accept=True)
    return AcceptFriendRequestResponse()

@router.post(
    '/reject-friend-request/{from_id}',
    name='Reject friend request')
@inject
async def reject_friend_request(from_id: int,
                                user_id: int = fastapi.Depends(get_user_id_from_jwt),
                                user_service: UserService = fastapi.Depends(Provide['user_service'])):
    await user_service.process_friend_request(user_id, from_id, accept=False)
    return RejectFriendRequestResponse()

@router.get('/rooms')
@inject
async def get_user_rooms(user_id: int = fastapi.Depends(get_user_id_from_jwt),
                         user_service: UserService = fastapi.Depends(Provide['user_service'])):
    return await user_service.get_user_rooms(user_id)

@router.get('/{user_id}')
@inject
async def get_user_by_id(user_id: int,
                         user_service: UserService = fastapi.Depends(Provide['user_service'])):
    return APIUserForeign.model_validate(user_service.get_user(user_id))

@router.get('/{user_id}/profile-picture')
@inject
async def get_user_profile_picture(user_id: int,
                                   user_service: UserService = fastapi.Depends(Provide['user_service'])):
    profile_picture_data = user_service.get_user_profile_picture(user_id)
    
    content: bytes | None = None
    status_code = fastapi.status.HTTP_204_NO_CONTENT
    if profile_picture_data is not None:
        content = profile_picture_data
        status_code = fastapi.status.HTTP_200_OK
        
    return fastapi.Response(
        content=content,
        status_code=status_code,
        media_type=MediaType.IMAGE_JPEG)

