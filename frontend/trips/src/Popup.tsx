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

import React, { Activity, ReactNode, useEffect, useRef } from "react";

import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { useClassNames, useDynamicProperty } from "taipy-gui";

interface PopupProps {
    id?: string;
    updateVarName?: string;
    updateVars: string;
    libClassName?: string;
    className?: string;
    dynamicClassName?: string;
    children?: ReactNode;
    title?: string;
    defaultTitle?: string;
    content?: string;
    defaultContent?: string;
    visible?: boolean;
    defaultVisible?: boolean;
}

const paperSx = {
    position: "absolute",
    bottom: 0,
    right: 0,
    m: 0,
    p: 2,
    borderWidth: 0,
    borderTopWidth: 1,
    cursor: "move",
    width: "fit-content",
    maxWidth: "100%",
    height: "fit-content",
    maxHeight: "100vh",
    overflowY: "auto",
    zIndex: 1300,
};
const stackSx = {
    justifyContent: "space-between",
    gap: 2,
};
const boxSx = {
    flexShrink: 1,
    alignSelf: "center",
};
const boldSx = { fontWeight: "bold" };

const dragElement = (element: HTMLElement) => {
    var pos1 = 0,
        pos2 = 0,
        pos3 = 0,
        pos4 = 0;

    const dragMouseDown = (e: MouseEvent) => {
        e = e || window.event;
        e.preventDefault();
        // get the mouse cursor position at startup:
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        // call a function whenever the cursor moves:
        document.onmousemove = elementDrag;
    };

    const elementDrag = (e: MouseEvent) => {
        e = e || window.event;
        e.preventDefault();
        // calculate the new cursor position:
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        // set the element's new position:
        element.style.top = element.offsetTop - pos2 + "px";
        element.style.left = element.offsetLeft - pos1 + "px";
    };

    const closeDragElement = () => {
        // stop moving when mouse button is released:
        document.onmouseup = null;
        document.onmousemove = null;
    };

    element.onmousedown = dragMouseDown;
};

const Popup = (props: PopupProps) => {
    const { id = `popup_${Math.random().toString(36).substring(2, 9)}` } = props;

    const paperRef = useRef<HTMLDivElement>(null);
    const visible = useDynamicProperty(props.visible, props.defaultVisible, false);
    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const title = useDynamicProperty(props.title, props.defaultTitle, "");
    const content = useDynamicProperty(props.content, props.defaultContent, "") || "";

    useEffect(() => {
        if (paperRef.current && visible) {
            dragElement(paperRef.current);
        }
    }, [visible]);

    useEffect(() => {
        if (paperRef.current && id && localStorage && visible) {
            const pos = localStorage.getItem(`${id}-post`)?.split(",");
            if (pos && pos.length === 2) {
                paperRef.current.style.left = `${pos[0]}px`;
                paperRef.current.style.top = `${pos[1]}px`;
            }
        }
        return () => {
            if (paperRef.current && id && localStorage) {
                localStorage.setItem(`${id}-post`, `${paperRef.current.offsetLeft},${paperRef.current.offsetTop}`);
            }
        };
    }, [visible]);

    return (
        <Activity mode={visible ? "visible" : "hidden"}>
            <Paper
                id={id}
                role="dialog"
                aria-modal="false"
                aria-label="Popup"
                square
                variant="outlined"
                tabIndex={-1}
                sx={paperSx}
                className={className}
                ref={paperRef}
            >
                <Stack direction="column" sx={stackSx}>
                    <Box sx={boxSx}>
                        <Typography sx={boldSx}>{title}</Typography>
                    </Box>
                    <div style={boxSx} dangerouslySetInnerHTML={{ __html: content }} />
                </Stack>
            </Paper>
        </Activity>
    );
};
export default Popup;
