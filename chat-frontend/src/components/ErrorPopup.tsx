import * as CSS from "./ErrorPopup.module.css";

interface ErrorPopupProps {
    onClose: () => any,
    retryAction?: () => any,
};

export default function ErrorPopup({
    onClose,
    retryAction = undefined,
    }: ErrorPopupProps) {
    return <div className={CSS.errorPopup}>
        <img src="assets/icons/error.png" className={CSS.errorIcon}/>
        <button className={CSS.closeButton} onClick={() => onClose()}>
            <img src="assets/icons/close.svg" />
        </button>
        <span className={`${CSS.header} font-rest`}>
            Something went wrong
        </span>
        <span className={`${CSS.mainText} font-rest`}>
            We couldn't complete your request, due to a server error. Please try again or <a href="http://github.com/m4reQ/chat/issues/new" className="link">contact our support</a>.
        </span>
        <button
            className="button-generic"
            onClick={() => {
                retryAction?.();
                onClose(); }}>
            Retry
        </button>
    </div>;
}