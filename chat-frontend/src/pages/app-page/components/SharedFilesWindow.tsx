import AppWindow from "./AppWindow.tsx";
import TopBarContainer from "./TopBarContainer.tsx";
import * as CSS from "./SharedFilesWindow.module.css";

export default function SharedFilesWindow({}) {
    return <AppWindow width="20%">
        <TopBarContainer title="Shared Files" />
    </AppWindow>
}