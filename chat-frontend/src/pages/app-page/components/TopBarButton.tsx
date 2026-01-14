import * as CSS from "./TopBarButton.module.css";

interface TopBarButtonProps {
    text: string;
    isSelected?: boolean;
    onClick: () => any;
}

export default function TopBarButton({text, onClick, isSelected = false}: TopBarButtonProps) {
    return <button
        className={CSS.topBarButton}
        style={{
            backgroundColor: isSelected ? "#F6EAFF" : undefined,
            color: isSelected ? "#C57FFF" : "#747474",
        }}
        onClick={(e) => {
            e.preventDefault();
            onClick();
        }}>
        {text}
    </button>;
}