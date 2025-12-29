import { PropsWithChildren } from "react";
import * as CSS from "./TopBarContainer.module.css";

interface TopBarContainerProps extends PropsWithChildren {
    title: string;
}

export default function TopBarContainer({title, children}: TopBarContainerProps) {
    return <div className={CSS.topBarContainer}>
        <span className={CSS.header}>{title}</span>
        {children}
    </div>;
}