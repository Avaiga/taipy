import React, { useCallback, useContext  } from "react";
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
import { TaipyBaseProps } from "./utils";

interface DialogProps extends TaipyBaseProps {
    title: string;
    cancelAction: string;
    validateAction: string;
    cancelActionText: string;
    validateActionText: string;
    pageId: string;
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
        defaultValue,
        value,
        cancelAction,
        validateAction = "ValidateAction",
        pageId,
        cancelActionText = "Cancel",
        validateActionText = "Validate",
    } = props;
    const { dispatch } = useContext(TaipyContext);

    const handleClose = useCallback(() => {
        dispatch(createSendActionNameAction(id, cancelAction || validateAction));
    }, [dispatch, id, cancelAction, validateAction]);

    const handleValidate = useCallback(() => {
        dispatch(createSendActionNameAction(id, validateAction));
    }, [dispatch, id, validateAction]);

    return (
        <MuiDialog onClose={handleClose} open={value === undefined ? defaultValue === "true" : !!value}>
            <DialogTitle sx={titleSx}>
                {title}
                <IconButton
                    aria-label="close"
                    onClick={handleClose}
                    sx={closeSx}
                    title={cancelAction ? cancelActionText : validateActionText}
                >
                    <CloseIcon />
                </IconButton>
            </DialogTitle>

            <DialogContent dividers>
                <TaipyRendered path={"/" + pageId} />
            </DialogContent>
            <DialogActions>
                {cancelAction && <Button onClick={handleClose}>{cancelActionText}</Button>}
                <Button onClick={handleValidate} autoFocus>
                    {validateActionText}
                </Button>
            </DialogActions>
        </MuiDialog>
    );
};

export default Dialog;
