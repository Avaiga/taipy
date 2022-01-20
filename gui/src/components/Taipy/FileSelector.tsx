import React, { ChangeEvent, useCallback, useContext, useEffect, useRef, useState } from "react";
import Fab from "@mui/material/Fab";
import LinearProgress from "@mui/material/LinearProgress";
import UploadFile from "@mui/icons-material/UploadFile";

import { TaipyContext } from "../../context/taipyContext";
import { createSendActionNameAction } from "../../context/taipyReducers";
import { useDynamicProperty } from "../../utils/hooks";
import { TaipyBaseProps } from "./utils";
import { uploadFile } from "../../workers/fileupload";

interface FileSelectorProps extends TaipyBaseProps {
    tp_onAction?: string;
    defaultLabel?: string;
    label?: string;
    multiple?: boolean;
    extensions?: string;
}

const handleDragOver = (evt: DragEvent) => {
    evt.stopPropagation();
    evt.preventDefault();
    evt.dataTransfer && (evt.dataTransfer.dropEffect = "copy");
};

const DROP_MESSAGE = "Drop here to Upload";

const defaultSx = { minWidth: "0px" };

const FileSelector = (props: FileSelectorProps) => {
    const { className, id, tp_onAction, defaultLabel = "", tp_varname = "", multiple = false, extensions } = props;
    const [label, setLabel] = useState(defaultLabel);
    const [dropLabel, setDropLabel] = useState("");
    const [dropSx, setDropSx] = useState(defaultSx);
    const [upload, setUpload] = useState(false);
    const [progress, setProgress] = useState(0);
    const { state, dispatch } = useContext(TaipyContext);
    const fabRef = useRef<HTMLElement>(null);

    const active = useDynamicProperty(props.active, props.defaultActive, true);

    const handleFiles = useCallback(
        (files: FileList | undefined | null, evt: Event | ChangeEvent) => {
            evt.stopPropagation();
            evt.preventDefault();
            if (files) {
                setUpload(true);
                uploadFile(tp_varname, files, setProgress, state.id).then(
                    (value) => {
                        setUpload(false);
                        tp_onAction && dispatch(createSendActionNameAction(id, tp_onAction));
                    },
                    (reason) => {
                        setUpload(false);
                    }
                );
            }
        },
        [state.id, id, tp_onAction, tp_varname, dispatch]
    );

    const handleChange = useCallback(
        (e: ChangeEvent<HTMLInputElement>) => handleFiles(e.target.files, e),
        [handleFiles]
    );

    useEffect(() => {
        setLabel((val) => {
            if (props.label !== undefined && val !== props.label) {
                return props.label;
            }
            return val;
        });
    }, [props.label]);

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

    const handleDragOverWithLabel = useCallback((evt: DragEvent) => {
        setDropSx((sx) =>
            sx.minWidth === defaultSx.minWidth
                ? { minWidth: (evt.currentTarget as HTMLElement).clientWidth + "px" }
                : sx
        );
        setDropLabel(DROP_MESSAGE);
        handleDragOver(evt);
    }, []);

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
                style={{ display: "none" }}
                id={id + "upload-file"}
                name="upload-file"
                type="file"
                accept={extensions}
                multiple={multiple}
                onChange={handleChange}
            />

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
                <UploadFile /> {dropLabel || label}
            </Fab>
            {upload ? <LinearProgress value={progress} /> : null}
        </label>
    );
};

export default FileSelector;
