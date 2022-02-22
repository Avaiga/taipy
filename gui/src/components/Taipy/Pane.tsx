import React, { ReactNode, useCallback, useContext, useEffect, useMemo, useState } from "react";
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import Drawer from "@mui/material/Drawer";
import IconButton from "@mui/material/IconButton";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";

import { TaipyContext } from "../../context/taipyContext";
import { createSendActionNameAction, createSendUpdateAction } from "../../context/taipyReducers";
import { useDynamicProperty } from "../../utils/hooks";
import TaipyRendered from "../pages/TaipyRendered";
import { TaipyActiveProps } from "./utils";

type AnchorType = "left" | "bottom" | "right" | "top" | undefined;

interface PaneProps extends TaipyActiveProps {
    children?: ReactNode;
    open?: boolean;
    defaultOpen?: string | boolean;
    anchor?: AnchorType;
    persistent?: boolean;
    closeAction?: string;
    page?: string;
    height?: string | number;
    width?: string | number;
}

const getHeaderSx = (anchor: AnchorType) => {
    switch (anchor) {
        case "right":
        case "top":
        case "bottom":
            return { display: "flex", alignItems: "center" };
        default:
            return { display: "flex", alignItems: "center", justifyContent: "flex-end" };
    }
};
const getDrawerSx = (horizontal: boolean, width: string | number, height: string | number) => ({
    width: horizontal ? width : undefined,
    height: horizontal ? undefined : height,
    flexShrink: 0,
    "& .MuiDrawer-paper": {
        width: horizontal ? width : undefined,
        height: horizontal ? undefined : height,
        boxSizing: "border-box",
    },
});

const Pane = (props: PaneProps) => {
    const {
        id,
        anchor = "left",
        persistent = false,
        closeAction,
        page,
        defaultOpen,
        height = "30vh",
        width = "30vw",
        tp_varname,
        propagate = true,
        className,
    } = props;
    const { dispatch } = useContext(TaipyContext);
    const [open, setOpen] = useState(defaultOpen === "true" || defaultOpen === true);

    const active = useDynamicProperty(props.active, props.defaultActive, true);

    const drawerSx = useMemo(
        () => getDrawerSx(anchor === "left" || anchor === "right", width, height),
        [width, height, anchor]
    );
    const headerSx = useMemo(() => getHeaderSx(anchor), [anchor]);

    const handleClose = useCallback(() => {
        if (active) {
            if (closeAction) {
                dispatch(createSendActionNameAction(id, closeAction));
            } else if (tp_varname) {
                dispatch(createSendUpdateAction(tp_varname, false, propagate));
            } else {
                setOpen(false);
            }
        }
    }, [active, dispatch, id, closeAction, tp_varname, propagate]);

    useEffect(() => {
        if (props.open !== undefined) {
            setOpen(props.open);
        }
    }, [props.open]);

    return !persistent || (persistent && open) ? (
        <Drawer
            sx={drawerSx}
            variant={persistent ? "permanent" : undefined}
            anchor={anchor}
            open={open}
            onClose={handleClose}
            className={className}
        >
            {persistent ? (
                <>
                    <Box sx={headerSx}>
                        <IconButton onClick={handleClose} disabled={!active}>
                            {anchor === "left" ? <ChevronLeftIcon /> : <ChevronRightIcon />}
                        </IconButton>
                    </Box>
                    <Divider />
                </>
            ) : null}
            {page ? <TaipyRendered path={"/" + page} /> : null}
            {props.children}
        </Drawer>
    ) : null;
};

export default Pane;
