import { useState } from "react";
import * as CSS from "./NewMessageBar.module.css";
import { makeAPIRequestWithJWT } from "../../../../backend.ts";
import { MessageType } from "../../../../models/Message.ts";

interface NewMessageBarProps {
    userJWT: string;
    roomID: number;
}

export default function NewMessageBar({userJWT, roomID}: NewMessageBarProps) {
    const [sendIsHovered, setSendIsHovered] = useState(false);

    return <form
        className={CSS.container}
        method="post"
        onSubmit={e => {
            e.preventDefault();
            
            const data = new FormData(e.currentTarget);

            makeAPIRequestWithJWT({
                jwt: userJWT,
                method: "POST",
                url: `/room/${roomID}/messages`,
                data: data,
            });

            e.currentTarget.reset();
        }}>
        <input
            className={CSS.messageInput}
            autoComplete="off"
            name="text"
            type="text"
            placeholder="Write your message..." />
        <button
            className={CSS.button}
            type="button">
            <img src="/assets/icons/new-message-bar/add-emoji.svg" />
        </button>
        <button
            className={CSS.button}
            type="button">
            <img src="/assets/icons/new-message-bar/add-attachment.svg" />
        </button>
        <button
            className={CSS.button}
            type="submit">
            <img
                src={sendIsHovered
                    ? "/assets/icons/new-message-bar/send-hover.svg"
                    : "/assets/icons/new-message-bar/send.svg"}
                onMouseEnter={() => setSendIsHovered(true)}
                onMouseLeave={() => setSendIsHovered(false)}/>
        </button>
    </form>;
}