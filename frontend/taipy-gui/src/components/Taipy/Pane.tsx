/*
 * Copyright 2023 Avaiga Private Limited
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

import React, { ReactNode, useCallback, useEffect, useMemo, useState } from "react";
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import Drawer from "@mui/material/Drawer";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";

import { createSendActionNameAction, createSendUpdateAction } from "../../context/taipyReducers";
import { useClassNames, useDispatch, useDynamicProperty, useModule } from "../../utils/hooks";
import TaipyRendered from "../pages/TaipyRendered";
import { TaipyActiveProps, TaipyChangeProps } from "./utils";

type AnchorType = "left" | "bottom" | "right" | "top" | undefined;

interface PaneProps extends TaipyActiveProps, TaipyChangeProps {
    children?: ReactNode;
    open?: boolean;
    defaultOpen?: string | boolean;
    anchor?: AnchorType;
    persistent?: boolean;
    onClose?: string;
    page?: string;
    partial?: boolean;
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
        onClose,
        page,
        partial,
        defaultOpen,
        height = "30vh",
        width = "30vw",
        updateVarName,
        propagate = true,
    } = props;
    const [open, setOpen] = useState(defaultOpen === "true" || defaultOpen === true);
    const dispatch = useDispatch();
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    const drawerSx = useMemo(
        () => getDrawerSx(anchor === "left" || anchor === "right", width, height),
        [width, height, anchor]
    );
    const headerSx = useMemo(() => getHeaderSx(anchor), [anchor]);

    const handleClose = useCallback(() => {
        if (active) {
            if (onClose) {
                dispatch(createSendActionNameAction(id, module, onClose));
            } else if (updateVarName) {
                dispatch(createSendUpdateAction(updateVarName, false, module, props.onChange, propagate));
            } else {
                setOpen(false);
            }
        }
    }, [active, dispatch, id, onClose, updateVarName, propagate, props.onChange, module]);

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
            <Tooltip title={hover || ""}>
                <>
                    {page ? <TaipyRendered path={"/" + page} partial={partial} fromBlock={true} /> : null}
                    {props.children}
                </>
            </Tooltip>
        </Drawer>
    ) : null;
};

export default Pane;
