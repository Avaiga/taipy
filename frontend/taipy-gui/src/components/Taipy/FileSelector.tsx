/*
 * Copyright 2021-2025 Avaiga Private Limited
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

import React, {
    ChangeEvent,
    CSSProperties,
    ReactNode,
    useCallback,
    useContext,
    useEffect,
    useMemo,
    useRef,
    useState,
} from "react";
import UploadFile from "@mui/icons-material/UploadFile";
import Button from "@mui/material/Button";
import LinearProgress from "@mui/material/LinearProgress";
import Tooltip from "@mui/material/Tooltip";
import { SxProps } from "@mui/material";
import { nanoid } from "nanoid";

import { TaipyContext } from "../../context/taipyContext";
import { createNotificationAction, createSendActionNameAction } from "../../context/taipyReducers";
import { useClassNames, useDynamicProperty, useModule } from "../../utils/hooks";
import { uploadFile } from "../../workers/fileupload";
import { getComponentClassName } from "./TaipyStyle";
import { expandSx, getCssSize, noDisplayStyle, TaipyActiveProps } from "./utils";

interface FileSelectorProps extends TaipyActiveProps {
    onAction?: string;
    label?: string;
    defaultLabel?: string;
    multiple?: boolean;
    selectionType?: string;
    extensions?: string;
    dropMessage?: string;
    notify?: boolean;
    width?: string | number;
    icon?: ReactNode;
    withBorder?: boolean;
    onUploadAction?: string;
    uploadData?: string;
}

const handleDragOver = (evt: DragEvent) => {
    evt.stopPropagation();
    evt.preventDefault();
    evt.dataTransfer && (evt.dataTransfer.dropEffect = "copy");
};

const defaultSx = { minWidth: "0px" };

const FileSelector = (props: FileSelectorProps) => {
    const {
        id,
        onAction,
        defaultLabel = "",
        updateVarName = "",
        multiple = false,
        selectionType = "file",
        extensions = ".csv,.xlsx",
        dropMessage = "Drop here to Upload",
        label,
        notify = true,
        withBorder = true,
    } = props;
    const [dropLabel, setDropLabel] = useState("");
    const [dropSx, setDropSx] = useState<SxProps | undefined>(defaultSx);
    const [upload, setUpload] = useState(false);
    const [progress, setProgress] = useState(0);
    const { state, dispatch } = useContext(TaipyContext);
    const butRef = useRef<HTMLElement>(null);
    const inputId = useMemo(() => (id || `tp-${nanoid()}`) + "-upload-file", [id]);
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    const directoryProps = useMemo(
        () =>
            selectionType.toLowerCase().startsWith("d") || "folder" == selectionType.toLowerCase()
                ? { webkitdirectory: "", directory: "", mozdirectory: "", nwdirectory: "" }
                : undefined,
        [selectionType]
    );

    useEffect(
        () =>
            setDropSx((sx: SxProps | undefined) =>
                expandSx(
                    sx,
                    props.width ? { width: getCssSize(props.width) } : undefined,
                    withBorder ? undefined : { border: "none" }
                )
            ),
        [props.width, withBorder]
    );

    const handleFiles = useCallback(
        (files: FileList | undefined | null, evt: Event | ChangeEvent) => {
            evt.stopPropagation();
            evt.preventDefault();
            if (files?.length) {
                setUpload(true);
                uploadFile(
                    updateVarName,
                    module,
                    props.onUploadAction,
                    props.uploadData,
                    files,
                    setProgress,
                    state.id
                ).then(
                    (value) => {
                        setUpload(false);
                        onAction && dispatch(createSendActionNameAction(id, module, onAction));
                        notify &&
                            dispatch(
                                createNotificationAction({
                                    nType: "success",
                                    message: value,
                                    system: false,
                                    duration: 3000,
                                    snackbarId: "FileSelector action"
                                })
                            );
                        const fileInput = document.getElementById(inputId) as HTMLInputElement;
                        fileInput && (fileInput.value = "");
                    },
                    (reason) => {
                        setUpload(false);
                        notify &&
                            dispatch(
                                createNotificationAction({
                                    nType: "error",
                                    message: reason,
                                    system: false,
                                    duration: 3000,
                                    snackbarId: "FileSelector failure"
                                })
                            );
                        const fileInput = document.getElementById(inputId) as HTMLInputElement;
                        fileInput && (fileInput.value = "");
                    }
                );
            }
        },
        [state.id, id, onAction, props.onUploadAction, props.uploadData, notify, updateVarName, dispatch, module, inputId]
    );

    const handleChange = useCallback(
        (e: ChangeEvent<HTMLInputElement>) => handleFiles(e.target.files, e),
        [handleFiles]
    );

    const handleDrop = useCallback(
        (e: DragEvent) => {
            setDropLabel("");
            setDropSx((sx: SxProps | undefined) => expandSx(sx, defaultSx));
            handleFiles(e.dataTransfer?.files, e);
        },
        [handleFiles]
    );

    const handleDragLeave = useCallback(() => {
        setDropLabel("");
        setDropSx((sx: SxProps | undefined) => expandSx(sx, defaultSx));
    }, []);

    const handleDragOverWithLabel = useCallback(
        (evt: DragEvent) => {
            const target = evt.currentTarget as HTMLElement;
            setDropSx((sx: SxProps | undefined) =>
                expandSx(
                    sx,
                    (sx as CSSProperties).minWidth === defaultSx.minWidth && target
                        ? { minWidth: target.clientWidth + "px" }
                        : undefined
                )
            );
            setDropLabel(dropMessage);
            handleDragOver(evt);
        },
        [dropMessage]
    );

    useEffect(() => {
        const butElt = butRef.current;
        const thisHandleDrop = handleDrop;
        if (butElt) {
            butElt.addEventListener("dragover", handleDragOverWithLabel);
            butElt.addEventListener("dragleave", handleDragLeave);
            butElt.addEventListener("drop", thisHandleDrop);
        }
        return () => {
            if (butElt) {
                butElt.removeEventListener("dragover", handleDragOverWithLabel);
                butElt.removeEventListener("dragleave", handleDragLeave);
                butElt.removeEventListener("drop", thisHandleDrop);
            }
        };
    }, [handleDrop, handleDragLeave, handleDragOverWithLabel]);

    return (
        <label htmlFor={inputId} className={`${className} ${getComponentClassName(props.children)}`}>
            <input
                style={noDisplayStyle}
                id={inputId}
                name="upload-file"
                type="file"
                accept={extensions}
                multiple={multiple}
                {...directoryProps}
                onChange={handleChange}
                disabled={!active || upload}
            />
            <Tooltip title={hover || ""}>
                <span>
                    <Button
                        id={id}
                        component="span"
                        aria-label="upload"
                        variant={withBorder ? "outlined" : undefined}
                        disabled={!active || upload}
                        sx={dropSx}
                        ref={butRef}
                    >
                        {props.icon || <UploadFile />} {dropLabel || label || defaultLabel}
                    </Button>
                </span>
            </Tooltip>
            {upload ? <LinearProgress value={progress} /> : null}
            {props.children}
        </label>
    );
};

export default FileSelector;
