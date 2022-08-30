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

import React, { ChangeEvent, useCallback, useContext, useEffect, useRef, useState } from "react";
import Fab from "@mui/material/Fab";
import LinearProgress from "@mui/material/LinearProgress";
import Tooltip from "@mui/material/Tooltip";
import UploadFile from "@mui/icons-material/UploadFile";

import { TaipyContext } from "../../context/taipyContext";
import { createAlertAction, createSendActionNameAction } from "../../context/taipyReducers";
import { useDynamicProperty } from "../../utils/hooks";
import { noDisplayStyle, TaipyActiveProps } from "./utils";
import { uploadFile } from "../../workers/fileupload";

interface FileSelectorProps extends TaipyActiveProps {
    tp_onAction?: string;
    defaultLabel?: string;
    label?: string;
    multiple?: boolean;
    extensions?: string;
    dropMessage?: string;
}

const handleDragOver = (evt: DragEvent) => {
    evt.stopPropagation();
    evt.preventDefault();
    evt.dataTransfer && (evt.dataTransfer.dropEffect = "copy");
};

const defaultSx = { minWidth: "0px" };

const FileSelector = (props: FileSelectorProps) => {
    const {
        className,
        id,
        tp_onAction,
        defaultLabel = "",
        updateVarName = "",
        multiple = false,
        extensions = ".csv,.xlsx",
        dropMessage = "Drop here to Upload",
        label,
    } = props;
    const [dropLabel, setDropLabel] = useState("");
    const [dropSx, setDropSx] = useState(defaultSx);
    const [upload, setUpload] = useState(false);
    const [progress, setProgress] = useState(0);
    const { state, dispatch } = useContext(TaipyContext);
    const fabRef = useRef<HTMLElement>(null);

    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    const handleFiles = useCallback(
        (files: FileList | undefined | null, evt: Event | ChangeEvent) => {
            evt.stopPropagation();
            evt.preventDefault();
            if (files) {
                setUpload(true);
                uploadFile(updateVarName, files, setProgress, state.id).then(
                    (value) => {
                        setUpload(false);
                        tp_onAction && dispatch(createSendActionNameAction(id, tp_onAction));
                        dispatch(
                            createAlertAction({ atype: "success", message: value, system: false, duration: 3000 })
                        );
                    },
                    (reason) => {
                        setUpload(false);
                        dispatch(
                            createAlertAction({ atype: "error", message: reason, system: false, duration: 3000 })
                        );
                    }
                );
            }
        },
        [state.id, id, tp_onAction, updateVarName, dispatch]
    );

    const handleChange = useCallback(
        (e: ChangeEvent<HTMLInputElement>) => handleFiles(e.target.files, e),
        [handleFiles]
    );

    const handleDrop = useCallback(
        (e: DragEvent) => {
            setDropLabel("");
            setDropSx(defaultSx);
            handleFiles(e.dataTransfer?.files, e);
        },
        [handleFiles]
    );

    const handleDragLeave = useCallback(() => {
        setDropLabel("");
        setDropSx(defaultSx);
    }, []);

    const handleDragOverWithLabel = useCallback(
        (evt: DragEvent) => {
            setDropSx((sx) =>
                sx.minWidth === defaultSx.minWidth
                    ? { minWidth: (evt.currentTarget as HTMLElement).clientWidth + "px" }
                    : sx
            );
            setDropLabel(dropMessage);
            handleDragOver(evt);
        },
        [dropMessage]
    );

    useEffect(() => {
        const fabElt = fabRef.current;
        const thisHandleDrop = handleDrop;
        if (fabElt) {
            fabElt.addEventListener("dragover", handleDragOverWithLabel);
            fabElt.addEventListener("dragleave", handleDragLeave);
            fabElt.addEventListener("drop", thisHandleDrop);
        }
        return () => {
            if (fabElt) {
                fabElt.removeEventListener("dragover", handleDragOverWithLabel);
                fabElt.removeEventListener("dragleave", handleDragLeave);
                fabElt.removeEventListener("drop", thisHandleDrop);
            }
        };
    }, [handleDrop, handleDragLeave, handleDragOverWithLabel]);

    return (
        <label htmlFor={id + "upload-file"} className={className}>
            <input
                style={noDisplayStyle}
                id={id + "upload-file"}
                name="upload-file"
                type="file"
                accept={extensions}
                multiple={multiple}
                onChange={handleChange}
            />
            <Tooltip title={hover || ""}>
                <Fab
                    id={id}
                    size="small"
                    component="span"
                    aria-label="upload"
                    variant="extended"
                    disabled={!active || upload}
                    ref={fabRef}
                    sx={dropSx}
                >
                    <UploadFile /> {dropLabel || label || defaultLabel}
                </Fab>
            </Tooltip>
            {upload ? <LinearProgress value={progress} /> : null}
        </label>
    );
};

export default FileSelector;
