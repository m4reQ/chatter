export enum UserActivityStatus {
    Active = "ACTIVE",
    Offline = "OFFLINE",
    BRB = "BRB",
    DontDisturb = "DONT_DISTURB",
};

export interface UserSelf {
    id: number;
    username: string;
    email: string;
    is_email_verified: boolean;
    accepts_friend_requests: boolean;
    created_at: Date;
    last_active: Date;
    activity_status: UserActivityStatus;
    profilePictureURL?: string;
    jwt: string;
};

export interface UserForeign {
    id: number;
    username: string;
    accepts_friend_requests: boolean;
    created_at: Date;
    last_active: Date;
    activity_status: UserActivityStatus;
};

export interface UserWithProfilePicture extends UserSelf {
    profilePictureURL?: string;
}