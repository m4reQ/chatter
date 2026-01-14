import { Activity, useState } from "react";
import { UserWithProfilePicture } from "../../../models/User.ts";
import NavbarButton from "./NavbarButton.tsx";
import SettingsPopup from "./settings-popup/SettingsPopup.tsx";
import "./Navbar.css";

interface NavbarProps {
    user: UserWithProfilePicture;
};

export default function Navbar({user}: NavbarProps) {
    const [settingsExpanded, setSettingsExpanded] = useState(false);
    const [currentSelectedButton, setCurrentSelectedButton] = useState(1);

    return <div className="navbar">
        <img src="assets/icons/app_icon.svg" />
        <div className="navbar-selector">
            <NavbarButton
                imgSrc="assets/icons/navbar_selector_friends.svg"
                onClick={() => {setCurrentSelectedButton(0)}}
                isSelected={currentSelectedButton === 0} />
            <NavbarButton
                imgSrc="assets/icons/navbar_selector_chat.svg"
                onClick={() => {setCurrentSelectedButton(1)}}
                isSelected={currentSelectedButton === 1} />
            <NavbarButton
                imgSrc="assets/icons/navbar_selector_add_friend.svg"
                onClick={() => {setCurrentSelectedButton(2)}}
                isSelected={currentSelectedButton === 2} />
        </div>
        <Activity mode={settingsExpanded ? "visible" : "hidden"}>
            <SettingsPopup
                username={user.username}
                profilePictureURL={user.profilePictureURL}
                onClose={() => {setSettingsExpanded(false)}}/>
        </Activity>
        <div style={{width: "90%", display: "grid"}}>
            <img
                className="navbar-profile-picture"
                src={user.profilePictureURL ?? "assets/icons/profile_picture_stub.svg"} />
            <button
                style={{
                    width: "30%",
                    gridArea: "1 / 1",
                    justifySelf: "end",
                    alignSelf: "start",
                }}
                onClick={e => {
                    e.preventDefault();
                    setSettingsExpanded(!settingsExpanded);
                }}>
                <img
                    src="assets/icons/settings-popup/expand_popup.svg"
                    style={{
                        width: "100%",
                        aspectRatio: "1",
                    }}/>
            </button>
        </div>
    </div>
}