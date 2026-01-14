import { useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import SettingsListItem from "./SettingsListItem.tsx";
import * as CSS from "./SettingsPopup.module.css";

interface SettingsPopupProps {
    username: string;
    profilePictureURL?: string;
    onClose: () => any;
}

export default function SettingsPopup({profilePictureURL, username, onClose}: SettingsPopupProps) {
    const settingsRef = useRef<HTMLDivElement>(null);
    const navigate = useNavigate();
    
    useEffect(() => {
        function clickListener(e: PointerEvent) {
            if (!settingsRef.current) {
                return;
            }

            if (!settingsRef.current.contains(e.target)) {
                onClose();
            }
        }

        document.addEventListener("click", clickListener, true);
        
        return () => {document.removeEventListener("click", clickListener)};
    });

    return <div ref={settingsRef} className={`${CSS.container} font-rest`}>
        <div className={CSS.headerContainer}>
            <img src={profilePictureURL ?? "assets/icons/profile_picture_stub.svg"} />
            <span>{username}</span>
        </div>
        <SettingsListItem
            imgSrc="assets/icons/settings-popup/change_profile_picture.svg"
            title="Change your profile picture"
            onClick={() => {}}/>
        <SettingsListItem
            imgSrc="assets/icons/settings-popup/open_settings.svg"
            title="Settings"
            onClick={() => {}}/>
        <SettingsListItem
            imgSrc="assets/icons/settings-popup/log_out.svg"
            title="Log out"
            onClick={() => {
                localStorage.removeItem("userJWT");
                navigate("/login");
            }}/>
    </div>
}