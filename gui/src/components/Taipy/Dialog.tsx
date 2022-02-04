import React, { ReactNode, useCallback, useContext, useMemo } from "react";
import Button from "@mui/material/Button";
import DialogTitle from "@mui/material/DialogTitle";
import MuiDialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import { Theme } from "@mui/material";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import { SxProps } from "@mui/system";

import { TaipyContext } from "../../context/taipyContext";
import { createSendActionNameAction } from "../../context/taipyReducers";
import TaipyRendered from "../pages/TaipyRendered";
import { TaipyActiveProps } from "./utils";
import { useDynamicProperty } from "../../utils/hooks";

interface DialogProps extends TaipyActiveProps {
    title: string;
    cancelAction?: string;
    validateAction?: string;
    cancelLabel?: string;
    validateLabel?: string;
    pageId: string;
    open?: boolean;
    defaultOpen?: string | boolean;
    children?: ReactNode;
    height?: string | number;
    width?: string | number;
}

const closeSx: SxProps<Theme> = {
    position: "absolute",
    right: 8,
    top: 8,
    color: (theme: Theme) => theme.palette.grey[500],
};
const titleSx = { m: 0, p: 2 };

const Dialog = (props: DialogProps) => {
    const {
        id,
        title,
        defaultOpen,
        open,
        cancelAction,
        validateAction = "ValidateAction",
        pageId,
        cancelLabel = "Cancel",
        validateLabel = "Validate",
        className,
        width,
        height,
    } = props;
    const { dispatch } = useContext(TaipyContext);

    const active = useDynamicProperty(props.active, props.defaultActive, true);

    const handleClose = useCallback(() => {
        dispatch(createSendActionNameAction(id, cancelAction || validateAction));
    }, [dispatch, id, cancelAction, validateAction]);

    const handleValidate = useCallback(() => {
        dispatch(createSendActionNameAction(id, validateAction));
    }, [dispatch, id, validateAction]);

    const paperProps = useMemo(() => {
        if (width !== undefined || height !== undefined) {
            const res = { sx: {} } as Record<string, Record<string, unknown>>;
            if (width !== undefined) {
                res.sx.width = width;
                res.sx.maxWidth = width;
            }
            if (height !== undefined) {
                res.sx.height = height;
            }
            return res;
        }
        return {};
    }, [width, height]);

    return (
        <MuiDialog
            id={id}
            onClose={handleClose}
            open={open === undefined ? defaultOpen === "true" || defaultOpen === true : !!open}
            className={className}
            PaperProps={paperProps}
        >
            <DialogTitle sx={titleSx}>
                {title}
                <IconButton
                    aria-label="close"
                    onClick={handleClose}
                    sx={closeSx}
                    title={cancelAction ? cancelLabel : validateLabel}
                >
                    <CloseIcon />
                </IconButton>
            </DialogTitle>

            <DialogContent dividers>
                {pageId ? <TaipyRendered path={"/" + pageId} /> : null}
                {props.children}
            </DialogContent>
            <DialogActions>
                {cancelAction && (
                    <Button onClick={handleClose} disabled={!active}>
                        {cancelLabel}
                    </Button>
                )}
                <Button onClick={handleValidate} autoFocus disabled={!active}>
                    {validateLabel}
                </Button>
            </DialogActions>
        </MuiDialog>
    );
};

export default Dialog;
