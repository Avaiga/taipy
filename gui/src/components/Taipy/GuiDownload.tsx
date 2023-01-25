/*
 * Copyright 2023 Avaiga Private Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

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
