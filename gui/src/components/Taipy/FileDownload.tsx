import React, { useCallback, useContext, useEffect, useMemo, useRef } from "react";

import Fab from "@mui/material/Fab";
import FileDownloadIco from "@mui/icons-material/FileDownload";

import { useDynamicProperty } from "../../utils/hooks";
import { noDisplayStyle, TaipyBaseProps } from "./utils";
import { TaipyContext } from "../../context/taipyContext";
import { createSendActionNameAction } from "../../context/taipyReducers";

interface FileDownloadProps extends TaipyBaseProps {
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
    const { id, className, auto, name, bypassPreview, tp_varname, tp_onAction, label, defaultLabel = "" } = props;
    const aRef = useRef<HTMLAnchorElement>(null);
    const { dispatch } = useContext(TaipyContext);

    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const render = useDynamicProperty(props.render, props.defaultRender, true);

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
        if (tp_varname) {
            usp.append("varname", tp_varname);
        }
        const ret = usp.toString();
        return [ret.length ? url + "?" + ret : url, !!bypassPreview && (name || true)];
    }, [props.content, bypassPreview, tp_varname, name, props.defaultContent]);

    const aProps = useMemo(() => (bypassPreview ? {} : { target: "_blank", rel: "noreferrer" }), [bypassPreview]);

    return render ? (
        <label htmlFor={id + "download-file"} className={className}>
            <a style={noDisplayStyle} id={id + "download-file"} download={download} href={url} {...aProps} ref={aRef} />
            {auto ? null : (
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
            )}
        </label>
    ) : null;
};

export default FileDownload;
