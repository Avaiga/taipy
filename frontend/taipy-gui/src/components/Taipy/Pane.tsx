/*
 * Copyright 2021-2025 Avaiga Private Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

import React, { CSSProperties, JSX, ReactNode, useCallback, useEffect, useMemo, useState } from "react";
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import Drawer from "@mui/material/Drawer";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";

import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import ExpandLess from "@mui/icons-material/ExpandLess";
import ExpandMore from "@mui/icons-material/ExpandMore";

import { createSendActionNameAction, createSendUpdateAction } from "../../context/taipyReducers";
import { useClassNames, useDispatch, useDynamicProperty, useModule } from "../../utils/hooks";
import TaipyRendered from "../pages/TaipyRendered";
import { getSuffixedClassNames, TaipyActiveProps, TaipyChangeProps } from "./utils";
import { getComponentClassName } from "./TaipyStyle";

type AnchorType = "left" | "bottom" | "right" | "top" | undefined;

interface PaneProps extends TaipyActiveProps, TaipyChangeProps {
    children?: ReactNode;
    open?: boolean;
    defaultOpen?: string | boolean;
    anchor?: string;
    persistent?: boolean;
    title?: string;
    defaultTitle?: string;
    onClose?: string;
    page?: string;
    partial?: boolean;
    height?: string | number;
    width?: string | number;
    showButton?: boolean;
}

const getHeaderSx = (anchor: AnchorType): CSSProperties => {
    const baseStyle = { display: "flex", alignItems: "center" };
    switch (anchor) {
        case "top":
        case "bottom":
            return baseStyle;
        case "right":
            return { ...baseStyle, flexDirection: "row-reverse" };
        default:
            return { ...baseStyle, justifyContent: "flex-end" };
    }
};
const getHeaderIcon = (anchor: AnchorType, open = true): JSX.Element => {
    switch (anchor) {
        case "right":
            return open ? <ChevronRightIcon /> : <ChevronLeftIcon />;
        case "top":
            return open ? <ExpandLess /> : <ExpandMore />;
        case "bottom":
            return open ? <ExpandMore /> : <ExpandLess />;
        default:
            return open ? <ChevronLeftIcon /> : <ChevronRightIcon />;
    }
};
const getTitleSx = (anchor: AnchorType): CSSProperties => {
    switch (anchor) {
        case "right":
            return { flexGrow: 1, paddingRight: 2 };
        default:
            return { flexGrow: 1, paddingLeft: 2 };
    }
};
const getDrawerSx = (anchor: AnchorType, width: string | number, height: string | number) => {
    const horizontal = anchor === "left" || anchor === "right";
    return {
        width: horizontal ? width : undefined,
        height: horizontal ? undefined : anchor === "bottom" ? 0 : height,
        flexShrink: 0,
        "& .MuiDrawer-paper": {
            width: horizontal ? width : undefined,
            height: horizontal ? undefined : height,
            boxSizing: "border-box",
        },
    };
};
const buttonDrawerSx = {
    "& .MuiDrawer-paper": {
        width: "fit-content",
        height: "fit-content",
        background: "transparent",
    },
};

const Pane = (props: PaneProps) => {
    const {
        id,
        persistent = false,
        onClose,
        page,
        partial,
        defaultOpen,
        height = "30vh",
        width = "30vw",
        updateVarName,
        propagate = true,
        showButton = false,
    } = props;
    const [open, setOpen] = useState(defaultOpen === "true" || defaultOpen === true);
    const dispatch = useDispatch();
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);
    const title = useDynamicProperty(props.title, props.defaultTitle, undefined);
    const anchor = useMemo<AnchorType>(
        () =>
            props.anchor
                ? props.anchor.toLowerCase().startsWith("l")
                    ? "left"
                    : props.anchor.toLowerCase().startsWith("r")
                      ? "right"
                      : props.anchor.toLowerCase().startsWith("t")
                        ? "top"
                        : props.anchor.toLowerCase().startsWith("b")
                          ? "bottom"
                          : "left"
                : "left",
        [props.anchor],
    );
    const drawerSx = useMemo(() => getDrawerSx(anchor, width, height), [width, height, anchor]);
    const headerSx = useMemo(() => getHeaderSx(anchor), [anchor]);
    const headerIcon = useMemo(() => getHeaderIcon(anchor), [anchor]);
    const closedHeaderIcon = useMemo(() => getHeaderIcon(anchor, false), [anchor]);
    const titleSx = useMemo(() => getTitleSx(anchor), [anchor]);
    const handleClose = useCallback(() => {
        if (active) {
            setOpen(false);
            if (onClose) {
                Promise.resolve().then(() => dispatch(createSendActionNameAction(id, module, onClose, false)));
            } else if (updateVarName) {
                Promise.resolve().then(() =>
                    dispatch(createSendUpdateAction(updateVarName, false, module, props.onChange, propagate)),
                );
            }
        }
    }, [active, dispatch, id, onClose, updateVarName, propagate, props.onChange, module]);

    const handleOpen = useCallback(() => {
        if (active) {
            setOpen(true);
            if (onClose) {
                Promise.resolve().then(() => dispatch(createSendActionNameAction(id, module, onClose, true)));
            } else if (updateVarName) {
                Promise.resolve().then(() =>
                    dispatch(createSendUpdateAction(updateVarName, true, module, props.onChange, propagate)),
                );
            }
        }
    }, [active, dispatch, id, onClose, updateVarName, propagate, props.onChange, module]);

    useEffect(() => {
        if (props.open !== undefined) {
            setOpen(props.open);
        }
    }, [props.open]);

    return open ? (
        <Drawer
            sx={drawerSx}
            variant={persistent ? "permanent" : undefined}
            anchor={anchor}
            open={open}
            onClose={handleClose}
            className={`${className} ${getComponentClassName(props.children)}`}
        >
            {persistent ? (
                <>
                    <Tooltip title={hover || ""}>
                        <Box sx={headerSx} className={getSuffixedClassNames(className, "-header")}>
                            {title ? <Box sx={titleSx}>{title}</Box> : null}
                            <IconButton onClick={handleClose} disabled={!active}>
                                {headerIcon}
                            </IconButton>
                        </Box>
                    </Tooltip>
                    <Divider />
                </>
            ) : null}
            <>
                {page ? <TaipyRendered path={"/" + page} partial={partial} fromBlock={true} /> : null}
                {props.children}
            </>
        </Drawer>
    ) : showButton ? (
        <Drawer
            variant="permanent"
            sx={buttonDrawerSx}
            anchor={anchor}
            open={true}
            className={getSuffixedClassNames(className, "-button")}
        >
            <Tooltip
                title={
                    title ? (
                        hover ? (
                            <>
                                {title}
                                <br />
                                {hover}
                            </>
                        ) : (
                            title
                        )
                    ) : (
                        hover || ""
                    )
                }
            >
                <span>
                    <IconButton onClick={handleOpen} disabled={!active}>
                        {closedHeaderIcon}
                    </IconButton>
                </span>
            </Tooltip>
        </Drawer>
    ) : null;
};

export default Pane;
