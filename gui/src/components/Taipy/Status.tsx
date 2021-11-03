import React, { MouseEvent, ReactNode, useMemo } from "react";
import Chip from "@mui/material/Chip";
import Avatar from "@mui/material/Avatar";

import { getInitials } from "../../utils";

export interface StatusType {
    status: string;
    message: string;
}

interface StatusProps {
    id?: string;
    value: StatusType;
    onClose?: (evt: MouseEvent) => void;
    icon?: ReactNode;
}

const status2Color = (status: string): "error" | "info" | "success" | "warning" => {
    status = (status || "").toLowerCase();
    status = status.length == 0 ? " " : status.charAt(0);
    switch (status) {
        case "s":
            return "success";
        case "w":
            return "warning";
        case "e":
            return "error";
    }
    return "info";
};

const Status = (props: StatusProps) => {
    const {value} = props;

    const chipProps = useMemo(() => {
        const cp: Record<string, unknown> = {};
        cp.color = status2Color(value.status);
        cp.avatar = <Avatar sx={{ bgcolor: `${cp.color}.main` }}>{getInitials(value.status)}</Avatar>;
        if (props.onClose) {
            cp.onDelete = props.onClose;
        }
        if (props.icon) {
            cp.deleteIcon = props.icon;
        }
        return cp;
    }, [value.status, props.onClose, props.icon]);

    return <Chip variant="outlined" {...chipProps} label={value.message} sx={{alignSelf: "flex-start"}} />;
};

export default Status;
