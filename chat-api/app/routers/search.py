from typing import Union
from fastapi import Depends, APIRouter, status
from fastapi.security.oauth2 import OAuth2PasswordBearer
from dependency_injector.wiring import Provide, inject

from app.services.auth_service import AuthorizationService
from app.services.search_service import SearchService
from app.models.search_result import APIRoomsSearchResult, APIUsersSearchResult
from app.models.errors import ErrorUserJWTExpired, ErrorUserJWTInvalid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')
router = APIRouter(
    prefix='/search',
    tags=['search'])

@inject
def get_user_id_from_jwt(user_jwt: str = Depends(oauth2_scheme),
                         auth_service: AuthorizationService = Depends(Provide['auth_service'])):
    return auth_service.decode_jwt(user_jwt)

@router.get(
    '/user',
    name='Search users',
    responses={
        status.HTTP_200_OK: {'model': APIUsersSearchResult},
        status.HTTP_401_UNAUTHORIZED: {'model': Union[ErrorUserJWTExpired, ErrorUserJWTInvalid]}
    })
@inject
async def get_search_users(query: str,
                           limit: int = 20,
                           offset: int = 0,
                           user_id: int = Depends(get_user_id_from_jwt),
                           search_service: SearchService = Depends(Provide['search_service'])):
    return await search_service.search_users(user_id, query, limit, offset)

@router.get(
    '/room',
    name='Search chat rooms',
    responses={
        status.HTTP_200_OK: {'model': APIRoomsSearchResult},
        status.HTTP_401_UNAUTHORIZED: {'model': Union[ErrorUserJWTExpired, ErrorUserJWTInvalid]}
    })
@inject
async def get_search_rooms(query: str,
                           limit: int = 20,
                           offset: int = 0,
                           user_id: int = Depends(get_user_id_from_jwt),
                           search_service: SearchService = Depends(Provide['search_service'])):
    return await search_service.search_rooms(user_id, query, limit, offset)