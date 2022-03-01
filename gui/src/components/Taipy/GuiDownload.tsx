import React, { useContext, useEffect, useRef } from "react";

import { noDisplayStyle } from "./utils";
import { TaipyContext } from "../../context/taipyContext";
import { createDownloadAction, createSendActionNameAction, FileDownloadProps } from "../../context/taipyReducers";

interface GuiDownloadProps {
    download?: FileDownloadProps;
}
const GuiDownload = ({ download }: GuiDownloadProps) => {
    const { name, onAction, content } = download || {};
    const aRef = useRef<HTMLAnchorElement>(null);
    const { dispatch } = useContext(TaipyContext);

    useEffect(() => {
        if (aRef.current && content) {
            aRef.current.click();
            onAction && dispatch(createSendActionNameAction("Gui.download", onAction, content));
            dispatch(createDownloadAction());
        }
    }, [content, dispatch, onAction]);

    return <a style={noDisplayStyle} id={"Gui-download-file"} download={name || true} href={content} ref={aRef} />;
};

export default GuiDownload;
