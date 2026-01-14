import uuid

from app.error import Error, OAuthError
from app.models.chat_room import RoomType

class ErrorOAuthInvalidClient(OAuthError):
    error_description: str = 'Invalid username or password provided.'
    error: str = 'invalid_client'

class ErrorOAuthInvalidRequest(OAuthError):
    error_description: str
    error: str = 'invalid_request'

class ErrorOAuthUnauthorizedClient(OAuthError):
    error_description: str
    error: str = 'unauthorized_client'

class ErrorEmailCodeExpired(Error):
    code: str
    error_code: str = 'email_code_expired'
    error_message: str = 'Email verification code has expired.'

class ErrorEmailCodeInvalid(Error):
    code: str
    error_code: str = 'email_code_invalid'
    error_message: str = 'Email verification code is invalid.'

class ErrorUserNotFoundID(Error):
    user_id: int
    error_code: str = 'user_not_found'
    error_message: str = 'User with given ID was not found.'

class ErrorUserNotFoundUsername(Error):
    username: str
    error_code: str = 'user_not_found'
    error_message: str = 'User with given username was not found.'

class ErrorUserAlreadyExists(Error):
    username: str
    email: str
    error_code: str = 'user_already_exists'
    error_message: str = 'User with given username or email already exists.'

class ErrorAPIKeyMalformed(Error):
    api_key: str | uuid.UUID
    error_code: str = 'api_key_malformed'
    error_message: str = 'Provided API key is in invalid format.'

class ErrorAPIKeyInvalid(Error):
    api_key: str | uuid.UUID
    error_code: str = 'api_key_invalid'
    error_message: str = 'Provided API key is not valid.'

class ErrorAPIKeyInactive(Error):
    api_key: str | uuid.UUID
    error_code: str = 'api_key_inactive'
    error_message: str = 'Provided API key is not active.'

class ErrorInvalidPasswordEncoding(Error):
    password: str
    error_code: str = 'password_encoding_invalid',
    error_message: str = 'Password must be a valid UTF-8 string.',

class ErrorInvalidPasswordFormat(Error):
    password: str
    validation_regex: str
    error_code: str = 'password_format_invalid'
    error_message: str = 'Password must respect provided validation rules.'

class ErrorInvalidPassword(Error):
    password: str
    error_code: str = 'password_invalid'
    error_message: str = 'Invalid password provided.'

class ErrorEmailInvalid(Error):
    email: str
    error_code: str = 'email_invalid'
    error_message: str = 'Provided email address is not valid.'

class ErrorEmailNotFound(Error):
    email: str
    error_code: str = 'email_not_found'
    error_message: str = 'Provided email address does not exist.'

class ErrorEmailNotConfirmed(Error):
    error_code: str = 'email_not_confirmed'
    error_message: str = 'This action requires user to have their email confirmed first.'

class ErrorEmailNotDelivered(Error):
    email: str
    error_code: str = 'email_not_delivered'
    error_message: str = 'Could not deliver email messsage to the provided address'

class ErrorIPInfoRetrieveFailed(Error):
    ip_address: str
    error_code: str = 'ipinfo_retrieve_fail'
    error_message: str = 'Failed to retrieve IP info for the request.'

class ErrorSelfFriendRequest(Error):
    id_from: int
    id_to: int
    error_code: str = 'friend_request_self'
    error_message: str = 'Cannot issue friend request to self.'

class ErrorFriendRequestAlreadySent(Error):
    id_from: int
    id_to: int
    error_code: str = 'friend_request_already_sent'
    error_message: str = 'Friend request has been already sent.'

class ErrorFriendRequestNotFound(Error):
    user_id: int
    from_id: int
    error_code: str = 'friend_request_not_found'
    error_message: str = 'Friend request with specified user and sender IDs was not found.'

class ErrorImageInvalidType(Error):
    media_type: str
    error_code: str = 'image_invalid_type'
    error_message: str = 'Unsupported media type of profile picture image file.'

class ErrorFileSaveFailed(Error):
    error_code: str = 'file_save_failed'
    error_message: str = 'Failed to process or save profile picture image.'

class ErrorUserJWTExpired(Error):
    token: str
    error_code: str = 'jwt_expired'
    error_message: str = 'User JWT expired.'

class ErrorUserJWTInvalid(Error):
    token: str
    error_code: str = 'jwt_invalid'
    error_message: str = 'User JWT is invalid.'

class ErrorRoomAlreadyExists(Error):
    room_name: str
    error_code: str = 'room_already_exists'
    error_message: str = 'Chat room with provided name already exists.'

class ErrorRoomNameTooLong(Error):
    room_name: str
    room_description: str
    error_code: str = 'room_name_too_long'
    error_message: str = 'Provided chat room name and/or description are too long.'

class ErrorRoomNotFound(Error):
    room_id: int
    error_code: str = 'room_not_found'
    error_message: str = 'Chat room with provided ID was not found.'

class ErrorRoomAlreadyJoined(Error):
    room_id: int
    user_id: int
    error_code: str = 'room_already_joined'
    error_message: str = 'User already joined specified chat room.'

class ErrorRoomPrivateJoin(Error):
    room_id: int
    error_code: str = 'room_private_join'
    error_message: str = 'Cannot join private room without invitation.'

class ErrorRoomInternalJoin(Error):
    room_id: int
    error_code: str = 'room_internal_join'
    error_message: str = 'Cannot join internal room.'

class ErrorRoomInvalidTypeChange(Error):
    room_id: int
    type: RoomType
    error_code: str = 'room_invalid_type_change'
    error_message: str = 'Cannot manually change room type to INTERNAL.'

class ErrorRoomNotOwner(Error):
    room_id: int
    user_id: int
    error_code: str = 'room_not_owner'
    error_message: str = 'Tried to modify chat room which is not owned by the user.'
    
class ErrorRoomUserNotJoined(Error):
    user_id: int
    room_id: int
    error_code: str = 'room_not_joined'
    error_message: str = 'User does not belong to the specified room.'

class ErrorRoomDeleteInternal(Error):
    room_id: int
    error_code: str = 'room_delete_internal'
    error_message: str = 'Cannot manually delete internal chat room.'

class ErrorDatabaseFail(Error):
    error_code: str = 'database_fail'
    error_message: str = 'Database operation failed.'

class ErrorInvalidMessage(Error):
    error_code: str = 'invalid_message'
    error_message: str = 'Either message text or file attachment must be specified.'

class ErrorAttachmentNotFound(Error):
    attachment_id: str
    room_id: int
    error_code: str = 'attachment_not_found'
    error_message: str = 'Attachment with given ID was not found.'