import NavbarButton from "./NavbarButton.tsx";
import "./Navbar.css";
import { useEffect, useRef, useState } from "react";
import { UserWithProfilePicture } from "../../../models/User.ts";
import SettingsListItem from "./SettingsListItem.tsx";
import { useNavigate } from "react-router";

interface NavbarProps {
    user: UserWithProfilePicture;
};

export default function Navbar({user}: NavbarProps) {
    const navigate = useNavigate();
    const [settingsExpanded, setSettingsExpanded] = useState(false);
    const [currentSelectedButton, setCurrentSelectedButton] = useState(1);
    const settingsRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        function clickListener(e: PointerEvent) {
            if (!settingsRef.current) {
                return;
            }

            if (!settingsRef.current.contains(e.target)) {
                setSettingsExpanded(false);
            }
        }

        document.addEventListener("click", clickListener, true);
        
        return () => {document.removeEventListener("click", clickListener)};
    })

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
        {settingsExpanded
            ? <div
                ref={settingsRef}
                style={{
                    backgroundColor: "#F5F5F5",
                    display: "flex",
                    flexDirection: "column",
                    borderRadius: "24px",
                    position: "absolute",
                    bottom: "12%",
                    left: "100%",
                    zIndex: 50,
                    alignContent: "center",
                    padding: "1em",
                    gap: "0.5em",
                    boxShadow: "0px 0px 8px rgba(47, 47, 47, 0.2)",
                    fontSize: "1em"
                }}>
                <div
                    style={{
                        display: "flex",
                        flexDirection: "row",
                        backgroundColor: "#F5F5F5",
                        borderRadius: "10px",
                        boxShadow: "0px 0px 8px rgba(47, 47, 47, 0.2)",
                        width: "100%",
                        alignItems: "center",
                        padding: "0.5em 0.8em",
                        boxSizing: "border-box"
                    }}>
                    <img
                        style={{
                            borderRadius: "100%",
                            aspectRatio: "1",
                            height: "2em"
                        }}
                        src={user.profilePictureURL ?? "assets/icons/profile_picture_stub.svg"} />
                    <span
                        className="font-rest"
                        style={{
                            flexGrow: 1,
                            textAlign: "center"
                        }}>
                        {user.username}
                    </span>
                </div>
                <SettingsListItem
                    imgSrc="assets/icons/settings_popup/change_profile_picture.svg"
                    title="Change your profile picture"
                    onClick={() => {}}/>
                <SettingsListItem
                    imgSrc="assets/icons/settings_popup/open_settings.svg"
                    title="Settings"
                    onClick={() => {}}/>
                <SettingsListItem
                    imgSrc="assets/icons/settings_popup/log_out.svg"
                    title="Log out"
                    onClick={() => {
                        localStorage.removeItem("userJWT");
                        navigate("/login");
                    }}/>
            </div>
            : null}
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
                    src="assets/icons/settings_popup/expand_popup.svg"
                    style={{
                        width: "100%",
                        aspectRatio: "1",
                    }}/>
            </button>
        </div>
    </div>
}