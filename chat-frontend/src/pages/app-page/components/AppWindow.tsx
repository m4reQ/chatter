import { PropsWithChildren } from "react";
import * as CSS from "./AppWindow.module.css";

interface AppWindowProps {
    width: string;
    alignItems?: AlignSetting;
    backgroundFilled?: boolean;
};

export default function AppWindow({width, children, alignItems = "start", backgroundFilled = false}: PropsWithChildren<AppWindowProps>) {
    return <div
        className={CSS.windowContainer + " font-rest"}
        style={{
            width: width,
            alignItems: alignItems,
            backgroundColor: backgroundFilled ? "#F4F3F5" : "#FFFFFF",
        }}>
        {children}
    </div>
}