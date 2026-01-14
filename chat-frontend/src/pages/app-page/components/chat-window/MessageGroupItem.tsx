import { useQuery } from "react-query";
import { makeAPIRequest } from "../../../../backend.ts";
import dateFormat from "dateformat";
import {MessageItem, ImageMessageItem} from "./MessageItem.tsx";
import MessageGroup from "../../../../models/MessageGroup.ts";
import { MessageType } from "../../../../models/Message.ts";
import * as CSS from "./MessageGroupItem.module.css";

interface MessageGroupItemProps {
    group: MessageGroup;
    userID: number;
    roomID: number;
}

export default function MessageGroupItem({group, roomID, userID}: MessageGroupItemProps) {
    const userImageQuery = useQuery(
        ["user-image", group.senderID],
        async () => {
            const response = await makeAPIRequest({
                method: "GET",
                url: `/user/${group.senderID}/profile-picture`,
                responseType: "blob",
            });

            if (response.status === 204) {
                return null;
            }

            return URL.createObjectURL(response.data);
        });

    return <div
        className={CSS.container}
        style={{
            alignSelf: group.senderID === userID ? "end" : "start"
        }}>
        <img
            className={CSS.senderImg}
            src={userImageQuery.isSuccess && userImageQuery.data
                ? userImageQuery.data
                : "/assets/icons/profile_picture_stub.svg"} />
        <div className={CSS.messagesContainer}>
            {group.messages.map(
                x => {
                    switch (x.type) {
                        case MessageType.Text:
                            return <MessageItem key={x.id} message={x}/>;
                        case MessageType.Image:
                            return <ImageMessageItem
                                key={x.id}
                                message={x}
                                roomID={roomID} />;
                    }
                })}
            <span className={CSS.senderUsername}>{`${group.senderUsername}, ${dateFormat(group.firstSent, "HH:MM")}`}</span>
        </div>
    </div>;
}