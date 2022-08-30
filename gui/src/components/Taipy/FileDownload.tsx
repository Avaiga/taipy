/*
 * Copyright 2022 Avaiga Private Limited
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

import React, { useCallback, useContext, useEffect, useMemo, useRef } from "react";

import Fab from "@mui/material/Fab";
import Tooltip from "@mui/material/Tooltip";
import FileDownloadIco from "@mui/icons-material/FileDownload";

import { useDynamicProperty } from "../../utils/hooks";
import { noDisplayStyle, TaipyActiveProps } from "./utils";
import { TaipyContext } from "../../context/taipyContext";
import { createSendActionNameAction } from "../../context/taipyReducers";

interface FileDownloadProps extends TaipyActiveProps {
    content?: string;
    defaultContent: string;
    name?: string;
    label?: string;
    defaultLabel?: string;
    auto?: boolean;
    render?: boolean;
    defaultRender?: boolean;
    bypassPreview?: boolean;
    tp_onAction?: string;
}

const FileDownload = (props: FileDownloadProps) => {
    const { id, className, auto, name, bypassPreview, tp_onAction, label, defaultLabel = "" } = props;
    const aRef = useRef<HTMLAnchorElement>(null);
    const { dispatch } = useContext(TaipyContext);

    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const render = useDynamicProperty(props.render, props.defaultRender, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    useEffect(() => {
        if (auto && aRef.current && active && render) {
            aRef.current.click();
            tp_onAction && dispatch(createSendActionNameAction(id, tp_onAction));
        }
    }, [active, render, auto, dispatch, id, tp_onAction]);

    const clickHandler = useCallback(() => {
        if (aRef.current) {
            aRef.current.click();
            tp_onAction && dispatch(createSendActionNameAction(id, tp_onAction));
        }
    }, [dispatch, id, tp_onAction]);

    const [url, download] = useMemo(() => {
        const url = props.content || props.defaultContent || "";
        if (!url || url.startsWith("data:")) {
            return [url, name || true];
        }
        const usp = new URLSearchParams("");
        if (bypassPreview) {
            usp.append("bypass", "");
        }
        const ret = usp.toString();
        return [ret.length ? url + "?" + ret : url, !!bypassPreview && (name || true)];
    }, [props.content, bypassPreview, name, props.defaultContent]);

    const aProps = useMemo(() => (bypassPreview ? {} : { target: "_blank", rel: "noreferrer" }), [bypassPreview]);

    return render ? (
        <label htmlFor={id + "download-file"} className={className}>
            <a style={noDisplayStyle} id={id + "download-file"} download={download} href={url} {...aProps} ref={aRef} />
            {auto ? null : (
                <Tooltip title={hover || ""}>
                    <Fab
                        id={id}
                        size="small"
                        component="span"
                        aria-label="download"
                        variant="extended"
                        disabled={!active}
                        onClick={clickHandler}
                    >
                        <FileDownloadIco /> {label || defaultLabel}
                    </Fab>
                </Tooltip>
            )}
        </label>
    ) : null;
};

export default FileDownload;
