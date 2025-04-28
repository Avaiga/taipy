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

import React, { ReactNode, useContext, useEffect, useMemo, useRef, useState } from "react";
import {
    draggable,
    dropTargetForElements,
    // type ElementDropTargetEventBasePayload,
    // monitorForElements,
} from "@atlaskit/pragmatic-drag-and-drop/element/adapter";
import Box from "@mui/material/Box";

import { useClassNames, useDynamicJsonProperty, useDynamicProperty, useModule } from "../../utils/hooks";
import TaipyRendered from "../pages/TaipyRendered";
import { expandSx, getCssSize, TaipyBaseProps } from "./utils";
import { TaipyContext } from "../../context/taipyContext";
import { getComponentClassName } from "./TaipyStyle";
import { DndProps, draggedSx, droppableSx } from "./dndUtils";
import { createSendActionNameAction } from "../../context/taipyReducers";

interface PartProps extends TaipyBaseProps, DndProps {
    render?: boolean;
    defaultRender?: boolean;
    page?: string;
    defaultPage?: string;
    children?: ReactNode;
    defaultPartial?: boolean;
    partial?: boolean;
    height?: string;
    defaultHeight?: string;
    width?: string | number;
}

const IframeStyle = {
    width: "100%",
    height: "100%",
};

const Part = (props: PartProps) => {
    const { id, partial, defaultPartial, dragType } = props;
    const { state, dispatch } = useContext(TaipyContext);
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const render = useDynamicProperty(props.render, props.defaultRender, true);
    const height = useDynamicProperty(props.height, props.defaultHeight, undefined);
    const page = useDynamicProperty(props.page, props.defaultPage, "");
    const iFrame = useMemo(() => {
        if (page && !defaultPartial) {
            if (/^https?\:\/\//.test(page)) {
                return true;
            }
            const sPage = "/" + page;
            return !Object.keys(state.locations || {}).some((route) => sPage === route);
        }
        return false;
    }, [state.locations, page, defaultPartial]);

    const itemRef = useRef<HTMLDivElement>(null);
    const [isDragging, setDragging] = useState(false);
    const [isDraggedOver, setIsDraggedOver] = useState(false);

    const dragParams = useDynamicJsonProperty(
        props.dndParameters,
        props.defaultDndParameters || "",
        undefined as Record<string, unknown> | undefined
    );
    const dropTypes = useMemo(() => {
        if (props.dropTypes) {
            try {
                return JSON.parse(props.dropTypes);
            } catch (e) {
                console.error("Error parsing dropTypes: ", e);
            }
            return undefined;
        }
    }, [props.dropTypes]);

    useEffect(() => {
        const elt = itemRef.current;
        if (!elt) {
            return;
        }
        return draggable({
            element: elt,
            onDragStart: () => setDragging(true),
            onDrop: () => setDragging(false),
            getInitialData: () => ({ type: dragType, sourceId: id, dragParams }),
            canDrag: () => !!dragType,
        });
    }, [, dragType, id, dragParams]);

    useEffect(() => {
        const elt = itemRef.current;
        if (!elt) {
            return;
        }

        return dropTargetForElements({
            element: elt,
            onDragEnter: () => setIsDraggedOver(true),
            onDragLeave: () => setIsDraggedOver(false),
            onDrop: ({ source }) => {
                setIsDraggedOver(false);
                dispatch(
                    createSendActionNameAction(props.onAction, module, {
                        reason: "drop",
                        sourceId: source.data.sourceId as string,
                        sourceParams: source.data.dragParams as Record<string, unknown>,
                        targetId: id,
                        targetParams: dragParams,
                    })
                );
            },
            canDrop: ({ source }) => !!dropTypes && dropTypes.includes(source.data.type as string),
        });
    }, [dropTypes, id, dragParams, dispatch, module, props.onAction]);

    const boxSx = useMemo(
        () =>
            expandSx(
                height ? { height: height } : undefined,
                props.width ? { width: getCssSize(props.width) } : undefined,
                isDragging ? draggedSx : undefined,
                isDraggedOver ? droppableSx : undefined
            ),
        [height, props.width, isDragging, isDraggedOver]
    );
    return render ? (
        <Box id={id} className={`${className} ${getComponentClassName(props.children)}`} sx={boxSx} ref={itemRef}>
            {iFrame ? (
                <iframe src={page} style={IframeStyle} />
            ) : page ? (
                <TaipyRendered path={"/" + page} partial={partial} fromBlock={true} />
            ) : null}
            {props.children}
        </Box>
    ) : null;
};

export default Part;
