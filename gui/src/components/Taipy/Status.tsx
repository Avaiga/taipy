import React, { useMemo } from "react";
import Chip from "@mui/material/Chip";
import Avatar from "@mui/material/Avatar";
import { Theme } from "@mui/material";

import { getInitials } from "../../utils";
import { TaipyBaseProps } from "./utils";

interface StatusProps extends TaipyBaseProps {
    value: { status: string; message: string };
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

const status2ThemeColor = (status: string) => (theme: Theme) => theme.palette[status2Color(status)].main;

const Status = (props: StatusProps) => {
    const value = useMemo(() => {
        if (props.value === undefined) {
            return JSON.parse(props.defaultValue);
        } else {
            return props.value;
        }
    }, [props.value, props.defaultValue]);
    const sxA = useMemo(() => ({bgcolor: status2ThemeColor(value.status)}), [value.status])
    const avatar = useMemo(() => <Avatar sx={sxA}>{getInitials(value.status)}</Avatar>, [value.status, sxA]);
    return <Chip variant="outlined" color={status2Color(value.status)} avatar={avatar} label={value.message} />;
};

export default Status;
