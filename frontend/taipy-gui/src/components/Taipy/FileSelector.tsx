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
import Button from "@mui/material/Button";
import LinearProgress from "@mui/material/LinearProgress";
import Tooltip from "@mui/material/Tooltip";
import UploadFile from "@mui/icons-material/UploadFile";

import { TaipyContext } from "../../context/taipyContext";
import { createAlertAction, createSendActionNameAction } from "../../context/taipyReducers";
import { useClassNames, useDynamicProperty, useModule } from "../../utils/hooks";
import { expandSx, getCssSize, noDisplayStyle, TaipyActiveProps } from "./utils";
import { uploadFile } from "../../workers/fileupload";
import { SxProps } from "@mui/material";

interface FileSelectorProps extends TaipyActiveProps {
    onAction?: string;
    defaultLabel?: string;
    label?: string;
    multiple?: boolean;
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
        extensions = ".csv,.xlsx",
        dropMessage = "Drop here to Upload",
        label,
        notify = true,
        withBorder = true,
    } = props;
    const [dropLabel, setDropLabel] = useState("");
    const [dropSx, setDropSx] = useState<SxProps>(defaultSx);
    const [upload, setUpload] = useState(false);
    const [progress, setProgress] = useState(0);
    const { state, dispatch } = useContext(TaipyContext);
    const butRef = useRef<HTMLElement>(null);
    const inputId = useMemo(() => (id || `tp-${Date.now()}-${Math.random()}`) + "-upload-file", [id]);
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    useEffect(
        () =>
            setDropSx((sx: SxProps) =>
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
                                createAlertAction({ atype: "success", message: value, system: false, duration: 3000 })
                            );
                    },
                    (reason) => {
                        setUpload(false);
                        notify &&
                            dispatch(
                                createAlertAction({ atype: "error", message: reason, system: false, duration: 3000 })
                            );
                    }
                );
            }
        },
        [state.id, id, onAction, props.onUploadAction, props.uploadData, notify, updateVarName, dispatch, module]
    );

    const handleChange = useCallback(
        (e: ChangeEvent<HTMLInputElement>) => handleFiles(e.target.files, e),
        [handleFiles]
    );

    const handleDrop = useCallback(
        (e: DragEvent) => {
            setDropLabel("");
            setDropSx((sx: SxProps) => ({ ...sx, ...defaultSx }));
            handleFiles(e.dataTransfer?.files, e);
        },
        [handleFiles]
    );

    const handleDragLeave = useCallback(() => {
        setDropLabel("");
        setDropSx((sx: SxProps) => ({ ...sx, ...defaultSx }));
    }, []);

    const handleDragOverWithLabel = useCallback(
        (evt: DragEvent) => {
            const target = evt.currentTarget as HTMLElement;
            setDropSx((sx: SxProps) =>
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
        <label htmlFor={inputId} className={className}>
            <input
                style={noDisplayStyle}
                id={inputId}
                name="upload-file"
                type="file"
                accept={extensions}
                multiple={multiple}
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
        </label>
    );
};

export default FileSelector;
