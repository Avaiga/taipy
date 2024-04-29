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

import React, { useCallback, SyntheticEvent, useState, useEffect, useMemo, ComponentType, MouseEvent } from "react";
import { Theme, alpha } from "@mui/material";
import Badge, { BadgeOrigin } from "@mui/material/Badge";
import Box from "@mui/material/Box";
import FormControlLabel from "@mui/material/FormControlLabel";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import Switch from "@mui/material/Switch";
import Tooltip from "@mui/material/Tooltip";
import { ChevronRight, FlagOutlined, PushPinOutlined } from "@mui/icons-material";
import { SimpleTreeView } from "@mui/x-tree-view/SimpleTreeView";
import { TreeItem } from "@mui/x-tree-view/TreeItem";

import {
    useDispatch,
    useModule,
    getUpdateVar,
    createSendUpdateAction,
    useDispatchRequestUpdateOnFirstRender,
    createRequestUpdateAction,
} from "taipy-gui";

import { Cycles, Cycle, DataNodes, NodeType, Scenarios, Scenario, DataNode, Sequence } from "./utils/types";
import {
    Cycle as CycleIcon,
    Datanode as DatanodeIcon,
    Sequence as SequenceIcon,
    Scenario as ScenarioIcon,
} from "./icons";
import {
    BadgePos,
    BadgeSx,
    BaseTreeViewSx,
    EmptyArray,
    FlagSx,
    ParentItemSx,
    iconLabelSx,
    tinyIconButtonSx,
    tinySelPinIconButtonSx,
} from "./utils";

export interface EditProps {
    id: string;
}

const treeSlots = { expandIcon: ChevronRight };

type Entities = Cycles | Scenarios | DataNodes;
type Entity = Cycle | Scenario | Sequence | DataNode;
type Pinned = Record<string, boolean>;

interface CoreSelectorProps {
    id?: string;
    updateVarName?: string;
    entities?: Entities;
    coreChanged?: Record<string, unknown>;
    updateVars: string;
    onChange?: string;
    error?: string;
    displayCycles?: boolean;
    showPrimaryFlag?: boolean;
    propagate?: boolean;
    value?: string | string[];
    defaultValue?: string;
    height: string;
    libClassName?: string;
    className?: string;
    dynamicClassName?: string;
    multiple?: boolean;
    lovPropertyName: string;
    leafType: NodeType;
    editComponent?: ComponentType<EditProps>;
    showPins?: boolean;
    onSelect?: (id: string | string[]) => void;
}

const tinyPinIconButtonSx = (theme: Theme) => ({
    ...tinyIconButtonSx,
    backgroundColor: alpha(theme.palette.text.secondary, 0.15),
    color: "text.secondary",

    "&:hover": {
        backgroundColor: alpha(theme.palette.secondary.main, 0.75),
        color: "secondary.contrastText",
    },
});

const switchBoxSx = { ml: 2 };

const CoreItem = (props: {
    item: Entity;
    displayCycles: boolean;
    showPrimaryFlag: boolean;
    leafType: NodeType;
    editComponent?: ComponentType<EditProps>;
    pins: [Pinned, Pinned];
    onPin?: (e: MouseEvent<HTMLElement>) => void;
    hideNonPinned: boolean;
}) => {
    const [id, label, items = EmptyArray, nodeType, primary] = props.item;
    const isPinned = props.pins[0][id];
    const isShown = props.hideNonPinned ? props.pins[1][id] : true;

    return !props.displayCycles && nodeType === NodeType.CYCLE ? (
        <>
            {items.map((item) => (
                <CoreItem
                    key={item[0]}
                    item={item}
                    displayCycles={false}
                    showPrimaryFlag={props.showPrimaryFlag}
                    leafType={props.leafType}
                    pins={props.pins}
                    onPin={props.onPin}
                    hideNonPinned={props.hideNonPinned}
                />
            ))}
        </>
    ) : isShown ? (
        <TreeItem
            key={id}
            itemId={id}
            data-selectable={nodeType === props.leafType}
            label={
                <Grid container alignItems="center" direction="row" flexWrap="nowrap" spacing={1}>
                    <Grid item xs sx={iconLabelSx}>
                        {nodeType === NodeType.CYCLE ? (
                            <CycleIcon fontSize="small" color="primary" />
                        ) : nodeType === NodeType.SCENARIO ? (
                            props.showPrimaryFlag && primary ? (
                                <Badge
                                    badgeContent={<FlagOutlined sx={FlagSx} />}
                                    color="primary"
                                    anchorOrigin={BadgePos as BadgeOrigin}
                                    sx={BadgeSx}
                                >
                                    <ScenarioIcon fontSize="small" color="primary" />
                                </Badge>
                            ) : (
                                <ScenarioIcon fontSize="small" color="primary" />
                            )
                        ) : nodeType === NodeType.SEQUENCE ? (
                            <SequenceIcon fontSize="small" color="primary" />
                        ) : (
                            <DatanodeIcon fontSize="small" color="primary" />
                        )}
                        {label}
                    </Grid>
                    {props.editComponent && nodeType === props.leafType ? (
                        <Grid item xs="auto">
                            <props.editComponent id={id} />
                        </Grid>
                    ) : null}
                    {props.onPin ? (
                        <Grid item xs="auto">
                            <Tooltip title={isPinned ? "Unpin" : "Pin"}>
                                <IconButton
                                    data-id={id}
                                    data-pinned={isPinned ? "pinned" : undefined}
                                    onClick={props.onPin}
                                    size="small"
                                    sx={isPinned ? tinySelPinIconButtonSx : tinyPinIconButtonSx}
                                >
                                    <PushPinOutlined />
                                </IconButton>
                            </Tooltip>
                        </Grid>
                    ) : null}
                </Grid>
            }
            sx={nodeType === NodeType.NODE ? undefined : ParentItemSx}
        >
            {items.map((item) => (
                <CoreItem
                    key={item[0]}
                    item={item}
                    displayCycles={true}
                    showPrimaryFlag={props.showPrimaryFlag}
                    leafType={props.leafType}
                    editComponent={props.editComponent}
                    pins={props.pins}
                    onPin={props.onPin}
                    hideNonPinned={props.hideNonPinned}
                />
            ))}
        </TreeItem>
    ) : null;
};

const findEntityAndParents = (
    id: string,
    tree: Entity[],
    parentIds: Entity[] = []
): [Entity, Entity[], string[]] | undefined => {
    for (const entity of tree) {
        if (entity[0] === id) {
            return [entity, parentIds, getChildrenIds(entity)];
        }
        if (entity[2]) {
            const res = findEntityAndParents(id, entity[2], [entity, ...parentIds]);
            if (res) {
                return res;
            }
        }
    }
};

const getChildrenIds = (entity: Entity): string[] => {
    const res: string[] = [];
    entity[2]?.forEach((child) => {
        res.push(child[0]);
        res.push(...getChildrenIds(child));
    });
    return res;
};

const getExpandedIds = (nodeId: string, exp?: string[], entities?: Entities) => {
    const ret = entities && findEntityAndParents(nodeId, entities);
    if (ret && ret[1]) {
        const res = ret[1].map((r) => r[0]);
        return exp ? [...exp, ...res] : res;
    }
    return exp || [];
};

const CoreSelector = (props: CoreSelectorProps) => {
    const {
        id = "",
        entities,
        displayCycles = true,
        showPrimaryFlag = true,
        propagate = true,
        multiple = false,
        lovPropertyName,
        leafType,
        value,
        defaultValue,
        showPins = true,
        updateVarName,
        updateVars,
        onChange,
        onSelect,
        coreChanged,
    } = props;

    const [selectedItems, setSelectedItems] = useState<string[]>([]);
    const [pins, setPins] = useState<[Pinned, Pinned]>([{}, {}]);
    const [hideNonPinned, setShowPinned] = useState(false);
    const [expandedItems, setExpandedItems] = useState<string[]>([]);

    const dispatch = useDispatch();
    const module = useModule();

    useDispatchRequestUpdateOnFirstRender(dispatch, id, module, updateVars, undefined, true);

    const onItemExpand = useCallback((e: SyntheticEvent, itemId: string, expanded: boolean) => {
        setExpandedItems((old) => {
            if (!expanded) {
                return old.filter((id) => id != itemId);
            }
            return [...old, itemId];
        });
    }, []);

    const onNodeSelect = useCallback(
        (e: SyntheticEvent, nodeId: string, isSelected: boolean) => {
            const { selectable = "false" } = e.currentTarget.parentElement?.dataset || {};
            const isSelectable = selectable === "true";
            if (!isSelectable && multiple) {
                return;
            }
            setSelectedItems((old) => {
                const res = isSelected ? [...old, nodeId] : old.filter((id) => id !== nodeId);
                const scenariosVar = getUpdateVar(updateVars, lovPropertyName);
                const val = multiple ? res : isSelectable ? nodeId : "";
                setTimeout(() => dispatch(createSendUpdateAction(updateVarName, val, module, onChange, propagate, scenariosVar)), 1);
                onSelect && isSelectable && onSelect(val);
                return res;
            });
        },
        [updateVarName, updateVars, onChange, onSelect, multiple, propagate, dispatch, module, lovPropertyName]
    );

    useEffect(() => {
        if (value !== undefined && value !== null) {
            setSelectedItems(Array.isArray(value) ? value : value ? [value]: []);
            setExpandedItems((exp) => typeof value === "string" ? getExpandedIds(value, exp, props.entities) : exp);
        } else if (defaultValue) {
            try {
                const parsedValue = JSON.parse(defaultValue);
                if (Array.isArray(parsedValue)) {
                    setSelectedItems(parsedValue);
                    if (parsedValue.length > 1) {
                        setExpandedItems((exp) => getExpandedIds(parsedValue[0], exp, props.entities));
                    }
                } else {
                    setSelectedItems([parsedValue]);
                    setExpandedItems((exp) => getExpandedIds(parsedValue, exp, props.entities));
                }
            } catch {
                setSelectedItems([defaultValue]);
                setExpandedItems((exp) => getExpandedIds(defaultValue, exp, props.entities));
            }
        } else if (value === null) {
            setSelectedItems([]);
        }
    }, [defaultValue, value, props.entities]);

    useEffect(() => {
        if (entities && !entities.length) {
            setSelectedItems((old) => {
                if (old.length) {
                    const lovVar = getUpdateVar(updateVars, lovPropertyName);
                    setTimeout(() => dispatch(
                        createSendUpdateAction(updateVarName, multiple ? [] : "", module, onChange, propagate, lovVar)
                    ), 1);
                    return [];
                }
                return old;
            });
            }
    }, [entities, updateVars, lovPropertyName, updateVarName, multiple, module, onChange, propagate, dispatch]);

    // Refresh on broadcast
    useEffect(() => {
        if (coreChanged?.scenario) {
            const updateVar = getUpdateVar(updateVars, lovPropertyName);
            updateVar && dispatch(createRequestUpdateAction(id, module, [updateVar], true));
        }
    }, [coreChanged, updateVars, module, dispatch, id, lovPropertyName]);

    const treeViewSx = useMemo(() => ({ ...BaseTreeViewSx, maxHeight: props.height || "50vh" }), [props.height]);

    const onShowPinsChange = useCallback(() => setShowPinned((sp) => !sp), []);

    const onPin = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            if (showPins && props.entities) {
                const { id = "", pinned = "" } = e.currentTarget.dataset || {};
                if (!id) {
                    return;
                }
                const [entity = undefined, parents = [], childIds = []] =
                    findEntityAndParents(id, props.entities) || [];
                if (!entity) {
                    return;
                }
                setPins(([pins, shows]) => {
                    if (pinned === "pinned") {
                        delete pins[id];
                        delete shows[id];
                        for (const parent of parents) {
                            const pinned = ((parent[2] as Entity[]) || []).some((child) => shows[child[0]]);
                            if (!pinned) {
                                delete shows[parent[0]];
                            } else {
                                break;
                            }
                        }
                        parents.forEach((parent) => delete pins[parent[0]]);
                        childIds.forEach((cId) => {
                            delete pins[cId];
                            delete shows[cId];
                        });
                    } else {
                        pins[id] = true;
                        shows[id] = true;
                        for (const parent of parents) {
                            const nonPinned = ((parent[2] as Entity[]) || []).some((child) => !pins[child[0]]);
                            if (!nonPinned) {
                                pins[parent[0]] = true;
                            } else {
                                break;
                            }
                        }
                        parents.forEach((p) => (shows[p[0]] = true));
                        childIds.forEach((cId) => {
                            pins[cId] = true;
                            shows[cId] = true;
                        });
                    }
                    return [pins, shows];
                });
            }
        },
        [showPins, props.entities]
    );

    return (
        <>
            {showPins ? (
                <Box sx={switchBoxSx}>
                    <FormControlLabel
                        control={
                            <Switch
                                onChange={onShowPinsChange}
                                checked={hideNonPinned}
                                disabled={!hideNonPinned && !Object.keys(pins[0]).length}
                            />
                        }
                        label="Pinned only"
                    />
                </Box>
            ) : null}
            <SimpleTreeView
                slots={treeSlots}
                sx={treeViewSx}
                onItemSelectionToggle={onNodeSelect}
                selectedItems={selectedItems}
                multiSelect={multiple}
                expandedItems={expandedItems}
                onItemExpansionToggle={onItemExpand}
            >
                {entities
                    ? entities.map((item) => (
                          <CoreItem
                              key={item ? item[0] : ""}
                              item={item}
                              displayCycles={displayCycles}
                              showPrimaryFlag={showPrimaryFlag}
                              leafType={leafType}
                              editComponent={props.editComponent}
                              onPin={showPins ? onPin : undefined}
                              pins={pins}
                              hideNonPinned={hideNonPinned}
                          />
                      ))
                    : null}
            </SimpleTreeView>
        </>
    );
};

export default CoreSelector;
