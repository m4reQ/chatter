import AppWindow from "../AppWindow.tsx";
import TopBarContainer from "../TopBarContainer.tsx";
import TopBarButton from "../TopBarButton.tsx";
import NewMessageBar from "./NewMessageBar.tsx";
import { useState } from "react";
import { ChatRoom } from "../../../../models/ChatRoom.ts";
import { UserSelf } from "../../../../models/User.ts";
import { useQuery } from "react-query";
import { makeAPIRequestWithJWT, setupInterceptors } from "../../../../backend.ts";
import { NavigateFunction, useNavigate } from "react-router";
import { Message } from "../../../../models/Message.ts";
import MessageItem from "./MessageItem.tsx";
import { mapQueryResult } from "../../../../utils.ts";
import MessageGroup from "../../../../models/MessageGroup.ts";
import MessageGroupItem from "./MessageGroupItem.tsx";
import * as CSS from "./ChatWindow.module.css";

interface ChatWindowProps {
    user: UserSelf;
    roomID?: number;
};

async function getRoomLastMessages(
    userJWT: string,
    roomID: number,
    messagesOffset: number,
    navigate: NavigateFunction) {
    setupInterceptors(navigate);

    const response = await makeAPIRequestWithJWT({
        jwt: userJWT,
        method: "GET",
        url: `/room/${roomID}/messages?offset=${messagesOffset}`
    });

    const messages = response.data as Message[];
    if (messages.length === 0) {
        return [];
    }

    let messageGroups = [MessageGroup.fromMessage(messages[0])];

    for (let i = 1; i < messages.length; i++) {
        const message = messages[i];
        const lastGroup = messageGroups.at(-1)!;
        if (message.sender_id === lastGroup.senderID) {
            lastGroup.pushMessage(message);
        } else {
            messageGroups.push(MessageGroup.fromMessage(message));
        }
    }

    return messageGroups;
}

export default function ChatWindow({user, roomID = undefined}: ChatWindowProps) {
    const navigate = useNavigate();
    const [selectedButtonIdx, setSelectedButtonIdx] = useState(0);
    const [messagesOffset, setMessagesOffset] = useState(0);
    const messagesQuery = useQuery(
        [user.id, roomID, messagesOffset],
        () => roomID
            ? getRoomLastMessages(user.jwt, roomID, messagesOffset, navigate)
            : [],
    )

    return <AppWindow
        width="60%"
        backgroundFilled>
        <TopBarContainer title="Group Chat">
            <div className={CSS.topBarButtonsContainer}>
                <TopBarButton
                    text="Messages"
                    isSelected={selectedButtonIdx == 0}
                    onClick={() => setSelectedButtonIdx(0)}/>
                <TopBarButton
                    text="Users"
                    isSelected={selectedButtonIdx == 1}
                    onClick={() => setSelectedButtonIdx(1)}/>
            </div>
        </TopBarContainer>
        {roomID
            ? <>
                <div className={CSS.messagesContainer}>
                    {mapQueryResult({
                        query: messagesQuery,
                        onLoading: () => <div className={CSS.loadingBox}>
                            <span>Loading messages...</span>
                            <img src="/assets/icons/loading.gif" />
                        </div>,
                        onSuccess: (data) => data.map(
                            x => <MessageGroupItem
                                roomID={roomID}
                                group={x}
                                key={`${x.senderID} ${x.firstSent}`}
                                userID={user.id} />)
                    })}
                </div>
                <NewMessageBar userJWT={user.jwt} roomID={roomID}/>
            </>
            : null}
    </AppWindow>;
}