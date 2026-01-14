import * as CSS from "./SettingsListItem.module.css";

interface SettingsListItemProps {
    imgSrc: string;
    title: string;
    onClick: () => any;
};

export default function SettingsListItem({imgSrc, title, onClick}: SettingsListItemProps) {
    return <button
        onClick={e => {
            e.preventDefault();
            onClick()
        }}
        className={CSS.container}>
        <img
            src={imgSrc}
            className={CSS.icon}/>
        <span className={CSS.title + " font-rest"}>{title}</span>
        <img
            src="assets/icons/settings-popup/expand.svg"
            className={CSS.expandIcon}/>
    </button>;
}