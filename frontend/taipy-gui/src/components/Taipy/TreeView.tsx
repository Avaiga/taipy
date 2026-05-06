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
    forwardRef,
    Ref,
    CSSProperties,
    HTMLAttributes,
    ReactNode,
} from "react";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import { RichTreeView } from "@mui/x-tree-view/RichTreeView";
import { TreeItem, TreeItemProps } from "@mui/x-tree-view/TreeItem";
import { TreeViewBaseItem } from "@mui/x-tree-view/models";
import { useTreeItemModel } from "@mui/x-tree-view/hooks";

import { createSendUpdateAction } from "../../context/taipyReducers";
import { isLovParent, LovImage, paperBaseSx, SelTreeProps, showItem, useLovListMemo } from "./lovUtils";
import {
    useClassNames,
    useDispatch,
    useDispatchRequestUpdateOnFirstRender,
    useDynamicProperty,
    useModule,
} from "../../utils/hooks";
import { LovItem } from "../../utils/lov";
import { getUpdateVar } from "./utils";
import { Icon } from "../../utils/icon";
import { getComponentClassName } from "./TaipyStyle";

type TreeItemWithLabel = {
    id: string;
    label: string;
    lovIcon?: Icon;
    height?: string;
    allowSelection?: boolean;
};

interface CustomTreeProps extends HTMLAttributes<HTMLElement> {
    children?: ReactNode;
    className?: string;
    lovIcon?: Icon;
    height?: string;
    disabled?: boolean;
}

const CustomLabel = (props: CustomTreeProps) => {
    // need a display name
    const { lovIcon, height } = props;

    return (
        <div className={`${props.className}${props.disabled? " Mui-disabled": ""}`}>
            {lovIcon ? <LovImage item={lovIcon} disableTypo={true} height={height} /> : props.children}
        </div>
    );
};

const CustomTreeItem = forwardRef(function CustomTreeItem(props: TreeItemProps, ref: Ref<HTMLLIElement>) {
    const item = useTreeItemModel<TreeItemWithLabel>(props.itemId)!;
    const { lovIcon, height, allowSelection = true } = item;
    const ctProps = { lovIcon, height, disabled: props.disabled } as CustomTreeProps;
    return <TreeItem {...props} data-selectable={allowSelection} ref={ref} slots={{ label: CustomLabel }} slotProps={{ label: ctProps }} />;
});

const treeSlots = { expandIcon: ChevronRightIcon, item: CustomTreeItem };

const renderTree = (
    lov: LovItem[],
    searchValue: string,
    selectLeafsOnly: boolean,
    rowHeight?: string,
    forbidSelections: Record<string, true> = {}
) => {
    const items = lov
        .map((li) => {
            const [children] = li.children
                ? renderTree(li.children, searchValue, selectLeafsOnly, rowHeight, forbidSelections)
                : [[]];
            if (!children.length && !showItem(li, searchValue)) {
                return null;
            }
            if (selectLeafsOnly && children.length) {
                forbidSelections[li.id] = true;
            }
            return {
                id: li.id,
                label: typeof li.item === "string" ? li.item : "undefined item",
                lovIcon: typeof li.item !== "string" ? (li.item as Icon) : undefined,
                height: rowHeight,
                children,
            } as TreeViewBaseItem<TreeItemWithLabel>;
        })
        .filter((c) => c) as TreeViewBaseItem<TreeItemWithLabel>[];
    return [items, forbidSelections] as [TreeViewBaseItem<TreeItemWithLabel>[], Record<string, true>];
};

const boxSx = { width: "100%" } as CSSProperties;
const textFieldSx = { mb: 1, px: 1, display: "flex" };

interface TreeViewProps extends SelTreeProps {
    expanded?: string[] | boolean;
    defaultExpanded?: string | boolean;
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

    const slotProps = useMemo(
        () => ({
            item: {
                disabled: !active,
            },
        }),
        [active]
    );
    useDispatchRequestUpdateOnFirstRender(dispatch, id, module, updateVars, updateVarName);

    const lovList = useLovListMemo(lov, defaultLov, true);
    const treeSx = useMemo(
        () => ({ bgcolor: "transparent", overflowY: "auto", width: "100%", maxWidth: width }),
        [width]
    );
    const paperSx = useMemo(() => {
        const sx = height === undefined ? paperBaseSx : { ...paperBaseSx, maxHeight: height };
        return { ...sx, overflow: "hidden", py: 1 };
    }, [height]);

    const [items, forbidSelections] = useMemo(
        () => renderTree(lovList, searchValue, selectLeafsOnly, rowHeight),
        [lovList, searchValue, selectLeafsOnly, rowHeight]
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
                    console.info("Tree.expanded cannot parse property", e);
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
                console.info("Tree.expanded wrongly formatted property", e);
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
        (event: SyntheticEvent | null, nodeIds: string[] | string | null) => {
            const ids = nodeIds === null ? [] : Array.isArray(nodeIds) ? nodeIds : [nodeIds];
            const allowedIds = ids.filter((id) => !forbidSelections[id]);
            if (multiple) {
                if (allowedIds.length) {
                    setSelectedValue(allowedIds);
                }
            } else if (allowedIds.length) {
                setSelectedValue(allowedIds);
            }
            if (!allowedIds.length && (ids.length || !multiple)) {
                return;
            }
            updateVarName &&
                dispatch(
                    createSendUpdateAction(
                        updateVarName,
                        allowedIds,
                        module,
                        props.onChange,
                        propagate,
                        valueById ? undefined : getUpdateVar(updateVars, "lov")
                    )
                );
        },
        [forbidSelections, multiple, updateVarName, dispatch, propagate, updateVars, valueById, props.onChange, module]
    );

    const handleInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => setSearchValue(e.target.value), []);

    const handleNodeToggle = useCallback(
        (event: React.SyntheticEvent | null, nodeIds: string[]) => {
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

    return (
        <Box id={id} sx={boxSx} className={`${className} ${getComponentClassName(props.children)}`}>
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
                    <RichTreeView
                        slots={treeSlots}
                        slotProps={slotProps}
                        sx={treeSx}
                        onSelectedItemsChange={clickHandler}
                        expandedItems={expandedNodes}
                        onExpandedItemsChange={handleNodeToggle}
                        multiSelect={multiple}
                        selectedItems={selectedValue}
                        items={items}
                        disableSelection={!active}
                    />
                </Paper>
            </Tooltip>
            {props.children}
        </Box>
    );
};

export default TreeView;
