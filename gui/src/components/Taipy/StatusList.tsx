import React, { MouseEvent, useCallback, useEffect, useMemo, useState } from "react";
import Stack from "@mui/material/Stack";
import ArrowDownward from "@mui/icons-material/ArrowDownward";
import ArrowUpward from "@mui/icons-material/ArrowUpward";
import Popover, { PopoverOrigin } from "@mui/material/Popover";

import Status, { StatusType } from "./Status";
import { TaipyBaseProps } from "./utils";

interface StatusListProps extends TaipyBaseProps {
    value: StatusType[];
    withoutClose: boolean;
}

const getStatusIntValue = (status: string) => {
    status = status.toLowerCase();
    if (status.startsWith("i")) {
        return 1;
    } else if (status.startsWith("s")) {
        return 2;
    } else if (status.startsWith("w")) {
        return 3;
    } else if (status.startsWith("e")) {
        return 4;
    }
    return 0;
};

const getStatusStrValue = (status: number) => {
    switch (status) {
        case 1:
            return "info";
        case 2:
            return "success";
        case 3:
            return "warning";
        case 4:
            return "error";
        default:
            return "unknwon";
    }
};

const getId = (base: string | undefined, idx: number) => (base || "status") + idx;

const NO_STATUS = { status: "info", message: "No Status" };

const getGlobalStatus = (values: StatusDel[]) => {
    values = values.filter((val) => !val.hidden);
    if (values.length == 0) {
        return NO_STATUS;
    } else if (values.length == 1) {
        return values[0];
    } else {
        const status = values.reduce((prevVal, currentStatus) => {
            const newVal = getStatusIntValue(currentStatus.status);
            return prevVal > newVal ? prevVal : newVal;
        }, 0);
        return { status: getStatusStrValue(status), message: `${values.length} statuses` };
    }
};

const statusEqual = (v1: StatusDel, v2: StatusDel) => v1.status === v2.status && v1.message === v2.message;

const ORIGIN = {
    vertical: "bottom",
    horizontal: "left",
} as PopoverOrigin;

interface StatusDel extends StatusType {
    hidden?: boolean;
    id?: string;
}

const StatusList = (props: StatusListProps) => {
    const [values, setValues] = useState<StatusDel[]>([]);
    const [opened, setOpened] = useState(false);
    const [multiple, setMultiple] = useState(false);
    const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);

    useEffect(() => {
        let val;
        if (props.value === undefined) {
            val = (props.defaultValue ? JSON.parse(props.defaultValue) : []) as StatusType[] | StatusType;
        } else {
            val = props.value;
        }
        if (!Array.isArray(val)) {
            val = [val];
        }
        setValues(val as StatusDel[]);
        setMultiple(val.length > 1);
    }, [props.value, props.defaultValue]);

    const onClose = useCallback((val) => {
        setValues((vals) => {
            const res = vals.map((v) => {
                if (!v.hidden && statusEqual(v, val)) {
                    v.hidden = !v.hidden;
                }
                return v;
            });
            if (res.filter(v => !v.hidden).length < 2) {
                setOpened(false);
                setMultiple(false);
            }
            return res;
        });
    }, []);

    const onOpen = useCallback((evt: MouseEvent) => {
        setOpened((op) => {
            setAnchorEl(op ? null : (evt.currentTarget || evt.target as HTMLElement).parentElement)
            return !op});
    }, []);

    const globalProps = useMemo(
        () => (multiple ? { onClose: onOpen, icon: opened ? <ArrowUpward /> : <ArrowDownward /> } : {}),
        [multiple, opened, onOpen]
    );

    return (
        <>
            <Status id={props.id} value={getGlobalStatus(values)} {...globalProps} />
            <Popover open={opened} anchorEl={anchorEl} onClose={onOpen} anchorOrigin={ORIGIN}>
                <Stack direction="column" spacing={1}>
                    {values
                        .filter((val) => !val.hidden)
                        .map((val, idx) => {
                            const closeProp = props.withoutClose ? {} : { onClose: () => onClose(val) };
                            return <Status key={getId(props.id, idx)} id={getId(props.id, idx)} value={val} {...closeProp} />;
                        })}
                </Stack>
            </Popover>
        </>
    );
};

export default StatusList;
