import { useQuery } from "react-query";
import { useNavigate } from "react-router";
import { useEffect } from "react";
import { Message } from "../../../../models/Message.ts";
import { makeAPIRequestWithJWT, setupInterceptors } from "../../../../backend.ts";
import * as CSS from "./MessageItem.module.css";
import { mapQueryResult } from "../../../../utils.ts";

interface MessageItemProps {
    message: Message;
}

interface ImageMessageItemProps {
    message: Message;
    roomID: number;
}

export function ImageMessageItem({message, roomID}: ImageMessageItemProps) {
    const navigate = useNavigate();
    const messageQuery = useQuery(
        [message.content],
        async () => {
            setupInterceptors(navigate);

            const userJWT = localStorage.getItem("userJWT");
            if (!userJWT) {
                navigate("/login");
                return "";
            }

            const response = await makeAPIRequestWithJWT({
                jwt: userJWT,
                method: "GET",
                url: `/room/${roomID}/attachments/${message.content}`,
                responseType: "blob"});
            return URL.createObjectURL(response.data);
        });
    
    useEffect(
        () => {
            return () => {
                if (messageQuery.isSuccess) {
                    URL.revokeObjectURL(messageQuery.data);
                }
            }
        },
        []);

    return mapQueryResult({
        query: messageQuery,
        onLoading: () => <div
            className={CSS.container}
            style={{
                width: "100%",
            }}>
            <img className={CSS.attachmentImg} src="/assets/icons/loading.gif" />
        </div>,
        onSuccess: (imageURL) => <img className={CSS.attachmentImg} src={imageURL} />,
    });
}

export function MessageItem({message}: MessageItemProps) {
    return <div className={CSS.container}>
        <span>{message.content}</span>
    </div>
}