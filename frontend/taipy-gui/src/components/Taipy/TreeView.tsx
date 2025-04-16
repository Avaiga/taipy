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

import React, {
    useState,
    useCallback,
    useEffect,
    useMemo,
    SyntheticEvent,
    HTMLAttributes,
    forwardRef,
    CSSProperties,
    RefObject,
} from "react";
import Box from "@mui/material/Box";
import { SimpleTreeView as MuiTreeView } from "@mui/x-tree-view/SimpleTreeView";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import { TreeItemContentProps, useTreeItemState, TreeItemProps } from "@mui/x-tree-view/TreeItem";
import { TreeItem2 } from "@mui/x-tree-view/TreeItem2";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";

import { createSendActionNameAction, createSendUpdateAction } from "../../context/taipyReducers";
import {
    DragItem,
    dragSx,
    isLovParent,
    LovImage,
    paperBaseSx,
    SelTreeProps,
    showItem,
    useLovListMemo,
} from "./lovUtils";
import {
    useClassNames,
    useDispatch,
    useDispatchRequestUpdateOnFirstRender,
    useDynamicProperty,
    useModule,
} from "../../utils/hooks";
import { LovItem } from "../../utils/lov";
import { expandSx, getUpdateVar } from "./utils";
import { Icon } from "../../utils/icon";
import { getComponentClassName } from "./TaipyStyle";
import { useDrag, useDrop } from "react-dnd";

const treeSlots = { expandIcon: ChevronRightIcon };

const CustomContent = forwardRef(function CustomContent(props: TreeItemContentProps, ref) {
    // need a display name
    const { classes, className, label, itemId, icon: iconProp, expansionIcon, displayIcon } = props;
    const {
        allowSelection,
        lovIcon,
        height,
        dragType = "",
        dropTypes,
        index = -1,
        handleDrop,
        lovVarName,
        targetId,
    } = props as unknown as CustomTreeProps;

    const { disabled, expanded, selected, focused, handleExpansion, handleSelection, preventSelection } =
        useTreeItemState(itemId);

    const icon = iconProp || expansionIcon || displayIcon;

    const classNames = [className, classes.root];
    if (expanded) {
        classNames.push(classes.expanded);
    }
    if (selected) {
        classNames.push(classes.selected);
    }
    if (allowSelection && focused) {
        classNames.push(classes.focused);
    }
    if (disabled) {
        classNames.push(classes.disabled);
    }

    const getDragItem = useCallback(
        () => (dragType && !disabled ? { id: itemId, index: -1 } : null),
        [dragType, disabled, itemId]
    );

    const [{ isDragging }, drag] = useDrag(
        () => ({
            type: dragType,
            item: getDragItem,
            collect: (monitor) => ({
                isDragging: monitor.isDragging(),
            }),
            end: (item: DragItem, monitor) => {
                const dropResult = monitor.getDropResult();
                if (dropResult) {
                    handleDrop?.(item.id, item.index, lovVarName || "", item.targetId);
                }
            },
        }),
        [dragType, getDragItem]
    );
    const [, drop] = useDrop<DragItem, void, { handlerId: string }>(
        () => ({
            accept: dropTypes || "",
            hover: (item: DragItem) => {
                item.index = index;
                item.targetId = targetId;
            },
        }),
        [dropTypes, index, targetId]
    );
    drag(drop(ref as RefObject<HTMLDivElement>));

    const divStyle = useMemo(() => expandSx(height ? { height: height } : undefined, isDragging ? dragSx: undefined) as CSSProperties, [height, isDragging]);

    return (
        <div
            className={classNames.join(" ")}
            onMouseDown={preventSelection}
            ref={ref as RefObject<HTMLDivElement>}
            style={divStyle}
        >
            <div onClick={handleExpansion} className={classes.iconContainer}>
                {icon}
            </div>
            <Typography
                onClick={allowSelection ? handleSelection : handleExpansion}
                component="div"
                className={classes.label}
            >
                {lovIcon ? <LovImage item={lovIcon} disableTypo={true} height={height} /> : label}
            </Typography>
        </div>
    );
});

interface CustomTreeProps extends HTMLAttributes<HTMLElement> {
    allowSelection: boolean;
    lovIcon?: Icon;
    height?: string;
    dragType?: string;
    dropTypes?: string[];
    index?: number;
    handleDrop?: (itemId: string, dropIndex: number, targetVarName: string, targetId?: string) => void;
    lovVarName?: string;
    targetId?: string;
}

const CustomTreeItem = (props: TreeItemProps & CustomTreeProps) => {
    const { allowSelection, lovIcon, height, dragType, dropTypes, handleDrop, lovVarName, targetId, ...tiProps } =
        props;
    const ctProps = {
        allowSelection,
        lovIcon,
        height,
        dragType,
        dropTypes,
        handleDrop,
        lovVarName,
        targetId,
    } as CustomTreeProps;
    return <TreeItem2 ContentComponent={CustomContent} ContentProps={ctProps} {...tiProps} />;
};

const renderTree = (
    lov: LovItem[],
    active: boolean,
    searchValue: string,
    selectLeafsOnly: boolean,
    rowHeight?: string,
    dragType?: string,
    dropTypes?: string[],
    index: number = 0,
    handleDrop: ((itemId: string, dropIndex: number, targetVarName: string, targetId?: string) => void) | undefined = undefined,
    lovVarName?: string,
    id?: string
) => {
    return lov.map((li) => {
        const children = li.children ? renderTree(li.children, active, searchValue, selectLeafsOnly, rowHeight, dragType, dropTypes, index, handleDrop, lovVarName, id) : [];
        if (!children.filter((c) => c).length && !showItem(li, searchValue)) {
            return null;
        }
        return (
            <CustomTreeItem
                key={li.id}
                itemId={li.id}
                label={typeof li.item === "string" ? li.item : "undefined item"}
                disabled={!active}
                allowSelection={selectLeafsOnly ? !children || children.length == 0 : true}
                lovIcon={typeof li.item !== "string" ? (li.item as Icon) : undefined}
                height={rowHeight}
                dragType={dragType}
                dropTypes={dropTypes}
                index={index}
                handleDrop={handleDrop}
                lovVarName={lovVarName}
                targetId={id}
            >
                {children}
            </CustomTreeItem>
        );
    });
};

const boxSx = { width: "100%" } as CSSProperties;
const textFieldSx = { mb: 1, px: 1, display: "flex" };

interface TreeViewProps extends SelTreeProps {
    defaultExpanded?: string | boolean;
    expanded?: string[] | boolean;
    selectLeafsOnly?: boolean;
    rowHeight?: string;
}

const TreeView = (props: TreeViewProps) => {
    const {
        id,
        defaultValue = "",
        value,
        updateVarName = "",
        defaultLov = "",
        filter = false,
        multiple = false,
        propagate = true,
        lov,
        updateVars = "",
        width = "100%",
        height,
        valueById,
        selectLeafsOnly = false,
        rowHeight,
    } = props;
    const [searchValue, setSearchValue] = useState("");
    const [selectedValue, setSelectedValue] = useState<string[]>([]);
    const [oneExpanded, setOneExpanded] = useState(false);
    const [refreshExpanded, setRefreshExpanded] = useState(false);
    const [expandedNodes, setExpandedNodes] = useState<string[]>([]);
    const dispatch = useDispatch();
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    useDispatchRequestUpdateOnFirstRender(dispatch, id, module, updateVars, updateVarName);

    const lovVarName = useMemo(() => getUpdateVar(updateVars, "lov"), [updateVars]);

    const lovList = useLovListMemo(lov, defaultLov, true);
    const treeSx = useMemo(
        () => ({ bgcolor: "transparent", overflowY: "auto", width: "100%", maxWidth: width }),
        [width]
    );
    const paperSx = useMemo(() => {
        const sx = height === undefined ? paperBaseSx : { ...paperBaseSx, maxHeight: height };
        return { ...sx, overflow: "hidden", py: 1 };
    }, [height]);

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
    const [, dropRef] = useDrop(
        () => ({
            accept: dropTypes,
            hover: (item: DragItem) => {
                item.index = -1;
                item.targetId = id;
            },
        }),
        [dropTypes, id]
    );
    const handleDrop = useCallback(
        (itemId: string, dropIndex: number, targetVarName: string, targetId?: string) => {
            dispatch(
                createSendActionNameAction(props.onAction, module, {
                    reason: "drop",
                    source_var: lovVarName,
                    source_id: id,
                    item_id: itemId,
                    drop_index: dropIndex,
                    target_var: targetVarName,
                    target_id: targetId,
                })
            );
        },
        [lovVarName, dispatch, module, props.onAction, id]
    );

    useEffect(() => {
        let refExp = false;
        let oneExp = false;
        if (props.expanded === undefined) {
            if (typeof props.defaultExpanded === "boolean") {
                oneExp = !props.defaultExpanded;
            } else if (typeof props.defaultExpanded === "string") {
                try {
                    const val = JSON.parse(props.defaultExpanded);
                    if (Array.isArray(val)) {
                        setExpandedNodes(val.map((v) => "" + v));
                    } else {
                        setExpandedNodes(["" + val]);
                    }
                    refExp = true;
                } catch (e) {
                    console.info(`Tree.expanded cannot parse property\n${(e as Error).message || e}`);
                }
            }
        } else if (typeof props.expanded === "boolean") {
            oneExp = !props.expanded;
        } else {
            try {
                if (Array.isArray(props.expanded)) {
                    setExpandedNodes(props.expanded.map((v) => "" + v));
                } else {
                    setExpandedNodes(["" + props.expanded]);
                }
                refExp = true;
            } catch (e) {
                console.info(`Tree.expanded wrongly formatted property\n${(e as Error).message || e}`);
            }
        }
        setOneExpanded(oneExp);
        setRefreshExpanded(refExp);
    }, [props.defaultExpanded, props.expanded]);

    useEffect(() => {
        if (value !== undefined) {
            setSelectedValue(Array.isArray(value) ? value : [value]);
        } else if (defaultValue) {
            let parsedValue;
            try {
                parsedValue = JSON.parse(defaultValue);
            } catch {
                parsedValue = defaultValue;
            }
            setSelectedValue(Array.isArray(parsedValue) ? parsedValue : [parsedValue]);
        }
    }, [defaultValue, value, multiple]);

    const clickHandler = useCallback(
        (event: SyntheticEvent, nodeIds: string[] | string | null) => {
            const ids = nodeIds === null ? [] : Array.isArray(nodeIds) ? nodeIds : [nodeIds];
            setSelectedValue(ids);
            updateVarName &&
                dispatch(
                    createSendUpdateAction(
                        updateVarName,
                        ids,
                        module,
                        props.onChange,
                        propagate,
                        valueById ? undefined : lovVarName
                    )
                );
        },
        [updateVarName, dispatch, propagate, lovVarName, valueById, props.onChange, module]
    );

    const handleInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => setSearchValue(e.target.value), []);

    const handleNodeToggle = useCallback(
        (event: React.SyntheticEvent, nodeIds: string[]) => {
            const expVar = getUpdateVar(updateVars, "expanded");
            if (oneExpanded) {
                setExpandedNodes((en) => {
                    if (en.length < nodeIds.length) {
                        // node opened: keep only parent nodes
                        nodeIds = nodeIds.filter((n, i) => i == 0 || isLovParent(lovList, n, nodeIds[0]));
                    }
                    if (refreshExpanded) {
                        dispatch(createSendUpdateAction(expVar, nodeIds, module, props.onChange, propagate));
                    }
                    return nodeIds;
                });
            } else {
                setExpandedNodes(nodeIds);
                if (refreshExpanded) {
                    dispatch(createSendUpdateAction(expVar, nodeIds, module, props.onChange, propagate));
                }
            }
        },
        [oneExpanded, refreshExpanded, lovList, propagate, updateVars, dispatch, props.onChange, module]
    );

    const treeProps = useMemo(
        () => ({ multiSelect: multiple, selectedItems: selectedValue }),
        [multiple, selectedValue]
    );

    return (
        <Box id={id} sx={boxSx} className={`${className} ${getComponentClassName(props.children)}`} ref={dropRef}>
            <Tooltip title={hover || ""}>
                <Paper sx={paperSx}>
                    <Box>
                        {filter && (
                            <TextField
                                margin="dense"
                                placeholder="Search field"
                                value={searchValue}
                                onChange={handleInput}
                                disabled={!active}
                                sx={textFieldSx}
                            />
                        )}
                    </Box>
                    <MuiTreeView
                        aria-label="tree"
                        slots={treeSlots}
                        sx={treeSx}
                        onSelectedItemsChange={clickHandler}
                        expandedItems={expandedNodes}
                        onExpandedItemsChange={handleNodeToggle}
                        {...treeProps}
                    >
                        {renderTree(lovList, !!active, searchValue, selectLeafsOnly, rowHeight, props.dragType, dropTypes, -1, handleDrop, lovVarName, id)}
                    </MuiTreeView>
                </Paper>
            </Tooltip>
            {props.children}
        </Box>
    );
};

export default TreeView;
