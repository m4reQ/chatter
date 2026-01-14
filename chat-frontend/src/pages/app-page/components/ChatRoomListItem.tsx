import { useQuery } from "react-query";
import { UserChatRoom } from "../../../models/ChatRoom.ts";
import { makeAPIRequest } from "../../../backend.ts";
import { Message, MessageType } from "../../../models/Message.ts";
import dateFormat from "dateformat";
import * as CSS from "./ChatRoomListItem.module.css";

interface ChatRoomListItemProps {
    room: UserChatRoom;
    isSelected: boolean;
    onSelect: () => any;
};

async function getChatRoomImageURL(roomID: number) {
    const response = await makeAPIRequest({
        method: "GET",
        url: `/room/${roomID}/image`,
        responseType: "blob",
    });
    return response.status == 200
        ? URL.createObjectURL(response.data)
        : undefined;
}

function formatLastMessage(message?: Message) {
    if (!message) {
        return "";
    }

    switch (message.type) {
        case MessageType.Text:
            return `${message.sender_username}: ${message.content}`;
        case MessageType.Image:
            return `${message.sender_username} sent an image.`;
        case MessageType.File:
            return `${message.sender_username} sent a file.`;
    }
}

export default function ChatRoomListItem({ room, isSelected, onSelect }: ChatRoomListItemProps) {
    const imageQuery = useQuery(
        ["chat-room-image", room.id],
        () => getChatRoomImageURL(room.id));

    return <button
        className={CSS.item}
        onClick={e => {
            e.preventDefault();
            onSelect();
        }}
        style={{
            backgroundColor: isSelected ? "#F4F4F4" : "transparent",
        }}>
        <img
            className={CSS.icon}
            src={imageQuery.isSuccess && imageQuery.data
                ? imageQuery.data
                : "/assets/icons/profile_picture_stub.svg"} />
        <div className={CSS.inner}>
            <span className={CSS.text}>
                {room.name}
            </span>
            <span className={`${CSS.text} ${CSS.auxText}`}>
                {formatLastMessage(room.last_message)}
            </span>
        </div>
        <span className={CSS.auxText}>
            {room.last_message
                ? dateFormat(room.last_message.sent_at, "HH:MM")
                : ""}
        </span>
    </button>
}