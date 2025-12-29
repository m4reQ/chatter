import Navbar from "./components/Navbar.tsx";
import ChatWindow from "./components/chat-window/ChatWindow.tsx";
import ChatsSideBar from "./components/ChatsSidebar.tsx";
import { useEffect, useState } from "react";
import { User, UserActivityStatus } from "../../User.ts";
import { NavigateFunction, useNavigate } from "react-router";
import "./AppPage.css";
import api, { makeAPIRequestWithJWT, setupInterceptors } from "../../backend.ts";
import assert from "assert";
import { UserSelf, UserWithProfilePicture } from "../../models/User.ts";
import { AxiosError } from "axios";
import { useQuery } from "react-query";
import SharedFilesWindow from "./components/SharedFilesWindow.tsx";

async function getUser(navigate: NavigateFunction) {
    setupInterceptors(navigate);

    const jwt = localStorage.getItem("userJWT");
    if (!jwt) {
        localStorage.removeItem("userJWT");
        navigate("/login");
        return;
    }

    const userResponse = await makeAPIRequestWithJWT({
        jwt: jwt,
        method: "GET",
        url: "/user",
    });
    
    const userData = userResponse.data as UserWithProfilePicture;
    
    const profilePictureResponse = await makeAPIRequestWithJWT({
        jwt: jwt,
        method: "GET",
        url: "/user/profile-picture",
        responseType: "blob",
    });
    userData.profilePictureURL = profilePictureResponse.status === 200
        ? URL.createObjectURL(profilePictureResponse.data)
        : undefined;
    
    return userData;
}

export default function AppPage({ }) {
    const navigate = useNavigate();
    const userQuery = useQuery(
        "user-query",
        () => getUser(navigate));
    
    // TODO Loading animation
    return userQuery.isSuccess && userQuery.data
        ? <div className="app-page-container">
            <Navbar user={userQuery.data} />
            <div className="main-content-container">
                <ChatsSideBar user={userQuery.data} />
                <ChatWindow />
                <SharedFilesWindow />
            </div>
        </div>
        : <></>;
}