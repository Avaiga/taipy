import React, { ChangeEvent, useCallback, useContext, useEffect, useRef, useState } from "react";
import Fab from "@mui/material/Fab";
import LinearProgress from "@mui/material/LinearProgress";
import UploadFile from "@mui/icons-material/UploadFile";

import { TaipyContext } from "../../context/taipyContext";
import { createSendActionNameAction } from "../../context/taipyReducers";
import { useDynamicProperty } from "../../utils/hooks";
import { TaipyBaseProps } from "./utils";
import uploadFile from "../../workers/fileupload";

interface FileSelectorProps extends TaipyBaseProps {
    tp_onAction: string;
    defaultLabel?: string;
    label?: string;
    multiple?: boolean;
}

const handleDragOver = (evt: DragEvent) => {
    evt.stopPropagation();
    evt.preventDefault();
    evt.dataTransfer && (evt.dataTransfer.dropEffect = "copy");
};

const fabHoverSx = {
    "&:hover": {
        border: "yellow",
    },
};

const FileSelector = (props: FileSelectorProps) => {
    const { className, id, tp_onAction, defaultLabel = "", tp_varname = "", multiple = false } = props;
    const [label, setLabel] = useState(defaultLabel);
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
                        console.log(value);
                        tp_onAction && dispatch(createSendActionNameAction(id, tp_onAction));
                    },
                    (reason) => {
                        console.error(reason);
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

    const handleDrop = useCallback((e: DragEvent) => handleFiles(e.dataTransfer?.files, e), [handleFiles]);

    useEffect(() => {
        setLabel((val) => {
            if (props.label !== undefined && val !== props.label) {
                return props.label;
            }
            return val;
        });
    }, [props.label]);

    useEffect(() => {
        if (fabRef.current) {
            fabRef.current.addEventListener("dragover", handleDragOver, false);
            fabRef.current.addEventListener("drop", handleDrop, false);
        }
    }, [handleDrop]);

    return (
        <label htmlFor={id + "upload-file"} className={className}>
            <input
                style={{ display: "none" }}
                id={id + "upload-file"}
                name="upload-file"
                type="file"
                multiple={multiple}
                onChange={handleChange}
            />

            <Fab
                id={id}
                color="secondary"
                size="small"
                component="span"
                aria-label="add"
                variant="extended"
                disabled={!active || upload}
                ref={fabRef}
                sx={fabHoverSx}
            >
                <UploadFile /> {label}
            </Fab>
            {upload ? <LinearProgress value={progress} /> : null}
        </label>
    );
};

export default FileSelector;
