import { useEffect, useState } from "react";
import { makeAPIRequest, makeAPIRequestWithJWT } from "../../../../backend.ts";
import * as CSS from "./RoomSearchResultItem.module.css";

interface RoomSearchResultItemProps {
    userJWT: string;
    id: number;
    name: string;
    description?: string;
};

export default function RoomSearchResultItem({userJWT, id, name, description = undefined}: RoomSearchResultItemProps) {
    const [roomImageSrc, setRoomImageSrc] = useState<string>();
    const [isRoomJoined, setIsRoomJoined] = useState(false);
    const [isJoinInProgress, setIsJoinInProgress] = useState(false);

    useEffect(() => {
        makeAPIRequest({method: "GET", url: `room/${id}/image`, responseType: "blob"})
            .then(response => {
                if (response.status === 200) {
                    setRoomImageSrc(URL.createObjectURL(response.data));
                }
            });

        return () => {
            if (roomImageSrc) {
                URL.revokeObjectURL(roomImageSrc);
            }
        };
    },
    []);

    return <div className={`${CSS.container} font-rest`}>
        <img
            src={roomImageSrc ?? "/assets/icons/profile_picture_stub.svg"}
            className={CSS.roomImage}/>
        <span className={CSS.roomName}>{name}</span>
        {isRoomJoined
            ? <img src="/assets/icons/room_joined.svg" className={CSS.joinButton}/>
            : <button
                disabled={isJoinInProgress}
                className={CSS.joinButton}
                onClick={e => {
                    e.preventDefault();
                    
                    setIsJoinInProgress(true);

                    makeAPIRequestWithJWT({jwt: userJWT, method: "POST", url: `room/${id}/join`})
                        .then(_ => {
                            setIsJoinInProgress(false);
                            setIsRoomJoined(true);
                        });
                }}>
                <img src="/assets/icons/create_room.svg" />
            </button>}
    </div>
}