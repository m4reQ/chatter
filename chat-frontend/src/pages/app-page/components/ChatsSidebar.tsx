import { Activity, useState } from "react";
import { NavigateFunction, useNavigate } from "react-router";
import { useQuery } from "react-query";
import { mapQueryResult } from "../../../utils.ts";
import ActivityIndicator, { ColorString } from "./ActivityIndicator.tsx";
import ActivityStatusSelector, { ActivityStatusSelectorItem } from "./ActivityStatusSelector.tsx";
import AppWindow from "./AppWindow.tsx";
import ChatRoomListItem from "./ChatRoomListItem.tsx";
import TopBarContainer from "./TopBarContainer.tsx";
import RoomPopup from "./room-popup/RoomPopup.tsx";
import { makeAPIRequestWithJWT, setupInterceptors } from "../../../backend.ts";
import { UserChatRoom } from "../../../models/ChatRoom.ts";
import { UserActivityStatus, UserWithProfilePicture } from "../../../models/User.ts";
import * as CSS from "./ChatsSidebar.module.css";

interface ChatsSideBarProps {
    user: UserWithProfilePicture;
    onRoomSelect: (roomID: number) => any;
}

interface ActivityStatusItem extends ActivityStatusSelectorItem {
    status: UserActivityStatus;
    indicatorColor: ColorString;
};

const activityStatusItems: ActivityStatusItem[] = [
    {
        status: UserActivityStatus.Active,
        statusText: "Active",
        indicatorColor: "#45C138",
        selectorBackgroundColor: "#BEECB9",
        selectorStrokeColor: "#539C4B"
    },
    {
        status: UserActivityStatus.BRB,
        statusText: "Be right back",
        indicatorColor: "#FFC300",
        selectorBackgroundColor: "#FFEAA6",
        selectorStrokeColor: "#AF8600",
    },
    {
        status: UserActivityStatus.DontDisturb,
        statusText: "Don't disturb",
        indicatorColor: "#FF3700",
        selectorBackgroundColor: "#FFA48B",
        selectorStrokeColor: "#862A08",
    },
    {
        status: UserActivityStatus.Offline,
        statusText: "Offline",
        indicatorColor: "#676767",
        selectorBackgroundColor: "#DEDEDE",
        selectorStrokeColor: "#676767",
    },
];

async function getUserChatRooms(navigate: NavigateFunction) {
    setupInterceptors(navigate);

    const jwt = localStorage.getItem("userJWT");
    if (!jwt) {
        localStorage.removeItem("userJWT");
        navigate("/login");
        return;
    }

    const response = await makeAPIRequestWithJWT({
        jwt: jwt,
        method: "GET",
        url: "/user/rooms",
    });
    return response.data as UserChatRoom[];
}

export default function ChatsSideBar({ user, onRoomSelect }: ChatsSideBarProps) {
    const navigate = useNavigate();
    const [roomPopupExpanded, setRoomPopupExpanded] = useState(false);
    const [currentChatRoomIdx, setCurrentChatRoomIdx] = useState(0);
    const chatRoomsQuery = useQuery(
        "chat-rooms",
        () => getUserChatRooms(navigate));

    function findUserActivityStatusIdx() {
        return activityStatusItems.findIndex(x => x.status === user.activity_status);
    }

    const [activityStatusIndex, setActivityStatusIndex] = useState(findUserActivityStatusIdx());

    return <>
        <AppWindow width="20%">
            <TopBarContainer title="Chats" />
            <div className={CSS.userInfoContainer}>
                <div className={CSS.profilePictureContainer}>
                    <img
                        className={CSS.profilePicture}
                        src={user.profilePictureURL ?? "/assets/icons/profile_picture_stub.svg"} />
                    <ActivityIndicator color={activityStatusItems[activityStatusIndex].indicatorColor} />
                </div>
                <span className={CSS.usernameLabel}>{user.username}</span>
                <ActivityStatusSelector
                    items={activityStatusItems}
                    initialIndex={activityStatusIndex}
                    onSelect={(idx) => {
                        setActivityStatusIndex(idx);
                    }} />
                <div className={CSS.chatRoomsListBar}>
                    <span>Last chats</span>
                    <div
                        style={{
                            display: "flex",
                            flexDirection: "row",
                            gap: "3px",
                        }}>
                        <button
                            onClick={e => {
                                e.preventDefault();
                                setRoomPopupExpanded(true);
                            }}>
                            <img src="assets/icons/create_room.svg" />
                        </button>
                        <button>
                            <img src="assets/icons/room_list_options.svg" />
                        </button>
                    </div>
                </div>
                <div className={CSS.chatRoomsList}>
                {mapQueryResult({
                    query: chatRoomsQuery,
                    onLoading: () => <span>Loading chat rooms...</span>,
                    onSuccess: data => data!.map(
                        (x, idx) => <ChatRoomListItem
                            key={x.id}
                            room={x}
                            isSelected={idx == currentChatRoomIdx}
                            onSelect={() => {
                                setCurrentChatRoomIdx(idx);
                                onRoomSelect(chatRoomsQuery.data![idx].id);
                            }} />)
                })}
                </div>
            </div>
        </AppWindow>
        <Activity mode={roomPopupExpanded ? "visible" : "hidden"}>
            <RoomPopup userJWT={user.jwt} onClose={() => setRoomPopupExpanded(false)} />
        </Activity>
    </>;
}