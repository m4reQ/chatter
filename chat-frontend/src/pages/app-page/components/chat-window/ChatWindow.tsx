import AppWindow from "../AppWindow.tsx";
import TopBarContainer from "../TopBarContainer.tsx";
import TopBarButton from "./TopBarButton.tsx";
import { useState } from "react";
import * as CSS from "./ChatWindow.module.css";

export default function ChatWindow({}) {
    const [selectedButtonIdx, setSelectedButtonIdx] = useState(0);

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
    </AppWindow>;
}