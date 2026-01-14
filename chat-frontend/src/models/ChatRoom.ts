import { Message } from "./Message.ts";
import { UserForeign } from "./User.ts";

export enum ChatRoomType {
    Public = "PUBLIC",
    Private = "PRIVATE",
    InviteOnly = "INVITE_ONLY",
    Internal = "INTERNAL",
};

export interface ChatRoom {
    id: number;
    name: string;
    description?: string;
    type: ChatRoomType;
    created_at: Date;
    owner?: UserForeign;
    users: UserForeign[];
};

export interface UserChatRoom {
    id: number;
    name: string;
    type: ChatRoomType;
    joined_at: Date;
    is_owner: boolean;
    last_message?: Message;
    image_url?: string;
}