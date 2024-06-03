/*
 * Copyright 2021-2024 Avaiga Private Limited
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

import React, { useCallback, useEffect, useMemo, useRef } from "react";

import Button from "@mui/material/Button";
import Tooltip from "@mui/material/Tooltip";
import FileDownloadIco from "@mui/icons-material/FileDownload";

import { useClassNames, useDispatch, useDynamicProperty, useModule } from "../../utils/hooks";
import { noDisplayStyle, TaipyActiveProps } from "./utils";
import { createSendActionNameAction } from "../../context/taipyReducers";
import { runXHR } from "../../utils/downloads";

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
    onAction?: string;
}

const FileDownload = (props: FileDownloadProps) => {
    const { id, auto, name = "", bypassPreview = true, onAction, label, defaultLabel = "" } = props;
    const aRef = useRef<HTMLAnchorElement>(null);
    const dispatch = useDispatch();
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const render = useDynamicProperty(props.render, props.defaultRender, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);
    const linkId = useMemo(() => (id || `tp-${Date.now()}-${Math.random()}`) + "-download-file", [id]);

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
        return [ret.length ? url + "?" + ret : url, bypassPreview && (name || true)];
    }, [props.content, bypassPreview, name, props.defaultContent]);

    useEffect(() => {
        if (auto && aRef.current && active && render) {
            if (url) {
                runXHR(
                    aRef.current,
                    url,
                    name,
                    onAction ? () => dispatch(createSendActionNameAction(id, module, onAction, name, url)) : undefined
                );
            } else {
                onAction && dispatch(createSendActionNameAction(id, module, onAction, name, url));
            }
        }
    }, [active, render, auto, name, url, dispatch, id, onAction, module]);

    const clickHandler = useCallback(() => {
        if (aRef.current) {
            if (url) {
                runXHR(
                    aRef.current,
                    url,
                    name,
                    onAction ? () => dispatch(createSendActionNameAction(id, module, onAction, name, url)) : undefined
                );
            } else {
                onAction && dispatch(createSendActionNameAction(id, module, onAction, name, url));
            }
        }
    }, [url, name, dispatch, id, onAction, module]);

    const aProps = useMemo(() => (bypassPreview ? {} : { target: "_blank", rel: "noreferrer" }), [bypassPreview]);

    return render ? (
        <label htmlFor={linkId}>
            <a style={noDisplayStyle} id={linkId} download={download} {...aProps} ref={aRef} />
            {auto ? null : (
                <Tooltip title={hover || ""}>
                    <Button id={id} variant="outlined" aria-label="download" disabled={!active} onClick={clickHandler} className={className}>
                        <FileDownloadIco /> {label || defaultLabel}
                    </Button>
                </Tooltip>
            )}
        </label>
    ) : null;
};

export default FileDownload;
