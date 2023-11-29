import React from "react";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Button from "@mui/material/Button";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import { Close } from "@mui/icons-material";

const IconButtonSx = { p: 0 };

interface ConfirmDialogProps {
    title: string;
    message: string;
    confirm: string;
    onConfirm: () => void;
    open: boolean;
    onClose: () => void;
}

const ConfirmDialog = ({ title, message, confirm, open, onClose, onConfirm }: ConfirmDialogProps) => (
    <Dialog onClose={onClose} open={open}>
        <DialogTitle>
            <Grid container direction="row" justifyContent="space-between" alignItems="center">
                <Typography variant="h5">{title}</Typography>
                <Tooltip title="close">
                    <IconButton onClick={onClose} sx={IconButtonSx}>
                        <Close />
                    </IconButton>
                </Tooltip>
            </Grid>
        </DialogTitle>
        <DialogContent dividers>
            <Typography>{message}</Typography>
        </DialogContent>

        <DialogActions>
            <Button variant="outlined" color="inherit" onClick={onClose}>
                Cancel
            </Button>

            <Button variant="contained" color="primary" onClick={onConfirm}>
                {confirm}
            </Button>
        </DialogActions>
    </Dialog>
);

export default ConfirmDialog;
