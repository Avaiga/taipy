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

import { useClassNames, useDynamicDictProperty, useDynamicProperty, useModule } from "../../utils/hooks";
import TaipyRendered from "../pages/TaipyRendered";
import { expandSx, getCssSize, TaipyBaseProps } from "./utils";
import { TaipyContext } from "../../context/taipyContext";
import { getComponentClassName } from "./TaipyStyle";
import { DndProps, draggedSx, droppableSx, useDrag, useDrop } from "./dndUtils";
import { createSendActionNameAction } from "../../context/taipyReducers";

interface PartProps extends TaipyBaseProps, DndProps {
    render?: boolean;
    defaultRender?: boolean;
    page?: string;
    defaultPage?: string;
    children?: ReactNode;
    partial?: boolean;
    defaultPartial?: boolean;
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

    const dragData = useDynamicDictProperty(
        props.dragData,
        props.defaultDragData || "",
        undefined as Record<string, unknown> | undefined
    );
    const dropData = useDynamicDictProperty(
        props.dropData,
        props.defaultDropData || "",
        undefined as Record<string, unknown> | undefined
    );
    const dropTypes = useMemo(() => {
        if (props.allowedDragTypes) {
            try {
                const drops = JSON.parse(props.allowedDragTypes);
                if (Array.isArray(drops) && drops.length) {
                    return drops as string[];
                }
                if (typeof drops === "string" && drops.length) {
                    return [drops];
                }
            } catch (e) {
                console.error("Error parsing dropTypes:", e);
            }
        }
        return undefined;
    }, [props.allowedDragTypes]);
    const dropHandler = useCallback(
        (
            sourceId?: string,
            sourceItemId?: string,
            sourceData?: Record<string, unknown>,
            sourceVarName?: string,
            targetItemId?: string
        ) => {
            dispatch(
                createSendActionNameAction(id, module, {
                    action: props.onAction,
                    reason: "drop",
                    source_id: sourceId,
                    source_item_id: sourceItemId,
                    source_data: sourceData,
                    source_var_name: sourceVarName,
                    target_id: id,
                    target_item_id: targetItemId,
                    target_data: dropData,
                })
            );
        },
        [props.onAction, dispatch, module, id, dropData]
    );

    const [isDragging] = useDrag(itemRef, dragType, dragData, undefined, undefined, id);
    const [isDraggedOver] = useDrop(itemRef, dropTypes, undefined, dropHandler);

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
