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

import React, { useCallback, SyntheticEvent, useState, useEffect, useMemo } from "react";
import Badge, { BadgeOrigin } from "@mui/material/Badge";
import Box from "@mui/material/Box";
import { ChevronRight, ExpandMore, FlagOutlined } from "@mui/icons-material";
import TreeItem from "@mui/lab/TreeItem";
import TreeView from "@mui/lab/TreeView";

import {
    useDispatch,
    useModule,
    useDynamicProperty,
    getUpdateVar,
    createSendUpdateAction,
    useDispatchRequestUpdateOnFirstRender,
    createRequestUpdateAction,
} from "taipy-gui";

import { Cycles, Cycle, DataNodes, NodeType, Scenarios, Scenario, DataNode, Pipeline } from "./utils/types";
import {
    Cycle as CycleIcon,
    Datanode as DatanodeIcon,
    Pipeline as PipelineIcon,
    Scenario as ScenarioIcon,
} from "./icons";
import { BadgePos, BadgeSx, BaseTreeViewSx, FlagSx, MainBoxSx, ParentItemSx, useClassNames } from "./utils";

interface NodeSelectorProps {
    id?: string;
    updateVarName?: string;
    datanodes?: Cycles | Scenarios | DataNodes;
    coreChanged?: Record<string, unknown>;
    updateVars: string;
    onChange?: string;
    error?: string;
    defaultDisplayCycles: boolean;
    displayCycles: boolean;
    defaultShowPrimaryFlag: boolean;
    showPrimaryFlag: boolean;
    propagate?: boolean;
    value?: string;
    defaultValue?: string;
    height: string;
    libClassName?: string;
    className?: string;
    dynamicClassName?: string;
}

const treeItemLabelSx = {
    display: "flex",
    alignItems: "center",
    gap: 1,
};

const CoreItem = (props: {
    item: Cycle | Scenario | Pipeline | DataNode;
    displayCycles: boolean;
    showPrimaryFlag: boolean;
}) => {
    const [id, label, items = [], nodeType, primary] = props.item;

    return !props.displayCycles && nodeType === NodeType.CYCLE ? (
        <>
            {items.map((item) => (
                <CoreItem key={item[0]} item={item} displayCycles={false} showPrimaryFlag={props.showPrimaryFlag} />
            ))}
        </>
    ) : (
        <TreeItem
            key={id}
            nodeId={id}
            data-selectable={nodeType === NodeType.NODE}
            label={
                <Box sx={treeItemLabelSx}>
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
                    ) : nodeType === NodeType.PIPELINE ? (
                        <PipelineIcon fontSize="small" color="primary" />
                    ) : (
                        <DatanodeIcon fontSize="small" color="primary" />
                    )}
                    {label}
                </Box>
            }
            sx={nodeType === NodeType.NODE ? undefined : ParentItemSx}
        >
            {items.map((item) => (
                <CoreItem key={item[0]} item={item} displayCycles={true} showPrimaryFlag={props.showPrimaryFlag} />
            ))}
        </TreeItem>
    );
};

const NodeSelector = (props: NodeSelectorProps) => {
    const { id = "", datanodes = [], propagate = true } = props;

    const [selected, setSelected] = useState("");
    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);

    const dispatch = useDispatch();
    const module = useModule();

    useDispatchRequestUpdateOnFirstRender(dispatch, id, module, props.updateVars);

    const displayCycles = useDynamicProperty(props.displayCycles, props.defaultDisplayCycles, true);
    const showPrimaryFlag = useDynamicProperty(props.showPrimaryFlag, props.defaultShowPrimaryFlag, true);

    const onSelect = useCallback(
        (e: SyntheticEvent, nodeId: string) => {
            const { selectable = "false" } = e.currentTarget.parentElement?.dataset || {};
            const scenariosVar = getUpdateVar(props.updateVars, "datanodes");
            dispatch(
                createSendUpdateAction(
                    props.updateVarName,
                    selectable === "true" ? nodeId : undefined,
                    module,
                    props.onChange,
                    propagate,
                    scenariosVar
                )
            );
            setSelected(nodeId);
        },
        [props.updateVarName, props.updateVars, props.onChange, propagate, dispatch, module]
    );

    const unselect = useCallback(() => {
        if (selected) {
            const scenariosVar = getUpdateVar(props.updateVars, "datanodes");
            dispatch(
                createSendUpdateAction(props.updateVarName, undefined, module, props.onChange, propagate, scenariosVar)
            );
            setSelected("");
        }
    }, [props.updateVarName, props.updateVars, props.onChange, propagate, dispatch, module, selected]);

    useEffect(() => {
        if (props.value !== undefined) {
            setSelected(props.value);
        } else if (props.defaultValue) {
            setSelected(props.defaultValue);
        }
    }, [props.defaultValue, props.value]);

    useEffect(() => {
        if (!datanodes.length) {
            unselect();
        }
    }, [datanodes, unselect]);

    // Refresh on broadcast
    useEffect(() => {
        if (props.coreChanged?.scenario) {
            const updateVar = getUpdateVar(props.updateVars, "datanodes");
            updateVar && dispatch(createRequestUpdateAction(id, module, [updateVar], true));
        }
    }, [props.coreChanged, props.updateVars, module, dispatch, id]);

    const treeViewSx = useMemo(() => ({ ...BaseTreeViewSx, maxHeight: props.height || "50vh" }), [props.height]);

    return (
        <Box sx={MainBoxSx} id={props.id} className={className}>
            <TreeView
                defaultCollapseIcon={<ExpandMore />}
                defaultExpandIcon={<ChevronRight />}
                sx={treeViewSx}
                onNodeSelect={onSelect}
                selected={selected}
            >
                {datanodes.map((item) => (
                    <CoreItem
                        key={item[0]}
                        item={item}
                        displayCycles={displayCycles}
                        showPrimaryFlag={showPrimaryFlag}
                    />
                ))}
            </TreeView>
            <Box>{props.error}</Box>
        </Box>
    );
};

export default NodeSelector;
