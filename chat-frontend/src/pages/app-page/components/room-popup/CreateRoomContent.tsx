import { ChangeEvent, FormEvent, useEffect, useState } from "react";
import { NavigateFunction, useNavigate } from "react-router";
import { makeAPIRequestWithJWT, setupInterceptors } from "../../../../backend.ts";
import { ChatRoomType } from "../../../../models/ChatRoom.ts";
import * as CSS from "./CreateRoomContent.module.css";

async function createChatRoom(
    roomName: string,
    roomDescription: string | null,
    isPrivate: boolean,
    roomImage: File | null,
    userJWT: string,
    navigate: NavigateFunction) {
    setupInterceptors(navigate);

    const response = await makeAPIRequestWithJWT({
        jwt: userJWT,
        method: "POST",
        url: "/room",
        data: {
            "name": roomName,
            "description": roomDescription,
            "type": isPrivate ? ChatRoomType.Private : ChatRoomType.Public,
        },
    });

    // TODO Handle create errors (name / description too long) (room with given name already exists)

    if (roomImage) {
        const roomID = response.data.room_id as number;

        const formData = new FormData();
        formData.append("image_file", roomImage);
        
        const imageResponse = await makeAPIRequestWithJWT({
            jwt: userJWT,
            method: "PUT",
            url: `/room/${roomID}/image`,
            data: formData,
        });
        
        // TODO Handle image setting error
    }
}

export default function CreateRoomContent({}) {
    const [selectedRoomImage, setSelectedRoomImage] = useState<File | null>(null);
    const [roomImageURL, setRoomImageURL] = useState<string | null>(null);
    const [userJWT, setUserJWT] = useState<string>();
    const [createInProgress, setCreateInProgress] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const jwt = localStorage.getItem("userJWT") as string;
        if (!jwt) {
            navigate("/login");
            return;
        }

        setUserJWT(jwt);
    },
    []);

    useEffect(() => {
        if (!selectedRoomImage) {
            setRoomImageURL(null);
            return;
        }

        const url = URL.createObjectURL(selectedRoomImage);
        setRoomImageURL(url);

        return () => URL.revokeObjectURL(url);
    },
    [selectedRoomImage])

    function onRoomImageSelected(e: ChangeEvent<HTMLInputElement>) {
        if (!e.target.files || e.target.files.length === 0) {
            setSelectedRoomImage(null);
            return;
        }

        setSelectedRoomImage(e.target.files[0]);
    }

    function onSubmit(e: FormEvent<HTMLFormElement>) {
        e.preventDefault();

        const data = new FormData(e.currentTarget);
        
        setCreateInProgress(true);
        createChatRoom(
            data.get("roomName") as string,
            data.get("roomDescription") as string | null,
            (data.get("isPrivateRoom") as string) === "true",
            selectedRoomImage,
            userJWT!,
            navigate)
            .then(() => {
                setCreateInProgress(false);
            });
    }

    return <form className={CSS.container + " font-rest"} onSubmit={onSubmit}>
        <div className={CSS.inner}>
            <div className={CSS.column}>
                <div className={CSS.inputGroup}>
                    <span>Room name</span>
                    <input className="font-rest" type="text" name="roomName" placeholder="Choose your room name..."/>
                </div>
                <div className={CSS.inputGroup}>
                    <span>Description</span>
                    <textarea className={CSS.descriptionInput + " font-rest"} name="roomDescription" placeholder="Add your room description..."/>
                </div>
                <div className={CSS.checkBoxContainer}>
                    <input type="checkbox" defaultChecked={false} name="isPrivateRoom"/>
                    <span>Private room</span>
                </div>
            </div>
            <div className={CSS.column}>
                <span>Room image</span>
                <img
                    className={CSS.roomImage} 
                    src={roomImageURL ?? "/assets/icons/room-popup/room-image-stub.svg"} />
                <input
                    type="file"
                    accept=".png,.jpg,.jpeg"
                    onChange={onRoomImageSelected} />
            </div>
        </div>
        <button
            type="submit"
            disabled={createInProgress}>
            {createInProgress ? "Creating..." : "Create"}
        </button>
    </form>;
}