/*
 * Copyright 2021-2024 Avaiga Private Limited
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

import React, { MouseEvent, ReactNode, useCallback, useMemo } from "react";
import Button from "@mui/material/Button";
import DialogTitle from "@mui/material/DialogTitle";
import MuiDialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import Tooltip from "@mui/material/Tooltip";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import { SxProps, Theme } from "@mui/system";

import { createSendActionNameAction } from "../../context/taipyReducers";
import TaipyRendered from "../pages/TaipyRendered";
import { TaipyActiveProps } from "./utils";
import { useClassNames, useDispatch, useDynamicProperty, useModule } from "../../utils/hooks";

interface DialogProps extends TaipyActiveProps {
    title: string;
    onAction?: string;
    closeLabel?: string;
    labels?: string;
    page?: string;
    partial?: boolean;
    open?: boolean;
    defaultOpen?: string | boolean;
    children?: ReactNode;
    height?: string | number;
    width?: string | number;
    localAction?: (idx: number) => void;
}

const closeSx: SxProps<Theme> = {
    color: (theme: Theme) => theme.palette.grey[500],
    marginTop: "-0.6em",
    marginLeft: "auto",
    alignSelf: "start",
};
const titleSx = { m: 0, p: 2, display: "flex", paddingRight: "0.1em" };

const Dialog = (props: DialogProps) => {
    const {
        id,
        title,
        defaultOpen,
        open,
        onAction = "",
        localAction,
        closeLabel = "Close",
        page,
        partial,
        width,
        height,
    } = props;
    const dispatch = useDispatch();
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    const handleAction = useCallback(
        (evt: MouseEvent<HTMLElement>) => {
            const { idx = "-1" } = evt.currentTarget.dataset;
            if (localAction) {
                 localAction(parseInt(idx, 10));
            } else {
                dispatch(createSendActionNameAction(id, module, onAction, parseInt(idx, 10)));
            }
        },
        [dispatch, id, onAction, module, localAction]
    );

    const labels = useMemo(() => {
        if (props.labels) {
            try {
                return JSON.parse(props.labels) as string[];
            } catch (e) {
                console.info(`Error parsing dialog.labels\n${(e as Error).message || e}`);
            }
        }
        return [];
    }, [props.labels]);

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
            onClose={handleAction}
            open={open === undefined ? defaultOpen === "true" || defaultOpen === true : !!open}
            className={className}
            PaperProps={paperProps}
        >
            <Tooltip title={hover || ""}>
                <DialogTitle sx={titleSx}>
                    {title}
                    <IconButton aria-label="close" onClick={handleAction} sx={closeSx} title={closeLabel} data-idx="-1">
                        <CloseIcon />
                    </IconButton>
                </DialogTitle>
            </Tooltip>

            <DialogContent dividers>
                {page ? <TaipyRendered path={"/" + page} partial={partial} fromBlock={true} /> : null}
                {props.children}
            </DialogContent>
            {labels.length ? (
                <DialogActions>
                    {labels.map((l, i) => (
                        <Button onClick={handleAction} disabled={!active} key={"label" + i} data-idx={i}>
                            {l}
                        </Button>
                    ))}
                </DialogActions>
            ) : null}
        </MuiDialog>
    );
};

export default Dialog;
