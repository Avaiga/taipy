import React from "react";
import { SxProps, Theme } from "@mui/material";
import Chip from "@mui/material/Chip";

export enum Status {
    SUBMITTED = 1,
    BLOCKED = 2,
    PENDING = 3,
    RUNNING = 4,
    CANCELED = 5,
    FAILED = 6,
    COMPLETED = 7,
    SKIPPED = 8,
    ABANDONED = 9,
}

const StatusChip = ({ status, sx }: { status: number; sx?: SxProps<Theme> }) => {
    const statusText = Status[status];
    let colorFill: "warning" | "default" | "success" | "error" = "warning";

    if (status === Status.COMPLETED || status === Status.SKIPPED) {
        colorFill = "success";
    } else if (status === Status.FAILED) {
        colorFill = "error";
    } else if (status === Status.CANCELED || status === Status.ABANDONED) {
        colorFill = "default";
    }

    const variant = status === Status.FAILED || status === Status.RUNNING ? "filled" : "outlined";

    return statusText ? <Chip label={statusText} variant={variant} color={colorFill} sx={sx} /> : null;
};

export default StatusChip;
