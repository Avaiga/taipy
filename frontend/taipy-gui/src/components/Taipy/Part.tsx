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

import React, { ReactNode, useCallback, useContext, useMemo, useRef } from "react";
import Box from "@mui/material/Box";

import { useClassNames, useDynamicProperty, useModule } from "../../utils/hooks";
import TaipyRendered from "../pages/TaipyRendered";
import { expandSx, getCssSize, TaipyBaseProps } from "./utils";
import { TaipyContext } from "../../context/taipyContext";
import { getComponentClassName } from "./TaipyStyle";
import { useDrag, useDrop } from "react-dnd";
import { createSendActionNameAction } from "../../context/taipyReducers";
import { DragItem, dragSx } from "./lovUtils";

interface PartProps extends TaipyBaseProps {
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
    dragType?: string;
    dropTypes?: string;
    onAction?: string;
    dragParameters?: string;
}

const IframeStyle = {
    width: "100%",
    height: "100%",
};

const Part = (props: PartProps) => {
    const { id, partial, defaultPartial } = props;
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

    // Droppable area for drag and drop
    const dropTypes = useMemo(() => {
        if (props.dropTypes) {
            try {
                return JSON.parse(props.dropTypes);
            } catch (e) {
                console.error("Invalid dropTypes JSON string", e);
            }
        }
        return [];
    }, [props.dropTypes]);
    const handleDrop = useCallback(
        (itemId: string, _dropIndex: number, _targetVarName: string, targetId?: string, dragParameters?: unknown) => {
            dispatch(
                createSendActionNameAction(props.onAction, module, {
                    reason: "drop",
                    source_id: id,
                    item_id: itemId,
                    target_id: targetId,
                    drag_parameters: dragParameters,
                })
            );
        },
        [dispatch, module, props.onAction, id]
    );
    const dragParameters = useMemo(() => {
        if (props.dragType && props.dragParameters) {
            try {
                return JSON.parse(props.dragParameters);
            } catch (e) {
                console.error("Invalid dragParameters JSON string", e);
            }
        }
        return undefined;
    }
    , [props.dragType, props.dragParameters]);

    const itemRef = useRef<HTMLDivElement>(null);
    const getDragItem = useCallback(() => (props.dragType ? { id: "", index: -1 } : null), [props.dragType]);

    const [{ isDragging }, drag] = useDrag(
        () => ({
            type: props.dragType || "",
            item: getDragItem,
            collect: (monitor) => ({
                isDragging: monitor.isDragging(),
            }),
            end: (item: DragItem, monitor) => {
                const dropResult = monitor.getDropResult();
                if (dropResult) {
                    handleDrop?.(item.id, item.index, "", item.targetId, dragParameters);
                }
            },
        }),
        [props.dragType, getDragItem, id]
    );
    const [, drop] = useDrop(
        () => ({
            accept: dropTypes || "",
            hover: (item: DragItem) => {
                item.index = -1;
                item.targetId = id;
            },
        }),
        [dropTypes]
    );
    drag(drop(itemRef));

    const boxSx = useMemo(
        () =>
            expandSx(
                height ? { height: height } : undefined,
                props.width ? { width: getCssSize(props.width) } : undefined,
                isDragging ? dragSx : undefined
            ),
        [height, props.width, isDragging]
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
