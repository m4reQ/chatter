import { Activity, useState } from "react";
import TopBarButton from "../TopBarButton.tsx";
import TopBarContainer from "../TopBarContainer.tsx";
import JoinRoomContent from "./JoinRoomContent.tsx";
import * as CSS from "./RoomPopup.module.css";
import CreateRoomContent from "./CreateRoomContent.tsx";

interface RoomPopupProps {
    userJWT: string;
    onClose: () => any;
};

// TODO Rename this component
export default function RoomPopup({userJWT, onClose}: RoomPopupProps) {
    const [selectedButtonIdx, setSelectedButtonIdx] = useState(0);

    return <div className={CSS.background + " font-rest"}>
        <div className={CSS.container}>
            <TopBarContainer title="Rooms">
                <div className={CSS.topBarButtonsContainer}>
                    <TopBarButton
                        text="Join"
                        isSelected={selectedButtonIdx == 0}
                        onClick={() => setSelectedButtonIdx(0)}/>
                    <TopBarButton
                        text="Create"
                        isSelected={selectedButtonIdx == 1}
                        onClick={() => setSelectedButtonIdx(1)}/>
                </div>
            </TopBarContainer>
            <button
                className={CSS.closeButton}
                onClick={e => {
                    e.preventDefault();
                    onClose();
                }}>
                <img src="/assets/icons/close.svg" />
            </button>
            <Activity mode={selectedButtonIdx === 0 ? "visible" : "hidden"}>
                <JoinRoomContent userJWT={userJWT}/>
            </Activity>
            <Activity mode={selectedButtonIdx === 1 ? "visible" : "hidden"}>
                <CreateRoomContent />
            </Activity>
        </div>
    </div>;
}