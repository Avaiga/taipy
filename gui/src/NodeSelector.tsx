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

import React, { useEffect, useCallback } from "react";
import Box from "@mui/material/Box";
import { ChevronRight, ExpandMore } from "@mui/icons-material";
import TreeItem from "@mui/lab/TreeItem";
import TreeView from "@mui/lab/TreeView";
import { useDispatch, useModule, createSendActionNameAction } from "taipy-gui";
import { Cycles, Cycle, DataNodes, NodeType, Scenarios, Scenario, DataNode, Pipeline } from "./utils/types";
import {
    Cycle as CycleIcon,
    Datanode as DatanodeIcon,
    Pipeline as PipelineIcon,
    Scenario as ScenarioIcon,
} from "./icons";

interface NodeSelectorProps {
    id?: string;
    updateVarName?: string;
    datanodes?: Cycles | Scenarios | DataNodes;
    coreChanged?: Record<string, unknown>;
    updateVars?: string;
    onDataNodeSelect?: string;
    error?: string;
}

const MainBoxSx = {
    maxWidth: 300,
    overflowY: "auto",
};

const TreeViewSx = {
    mb: 2,
    "& .MuiTreeItem-root .MuiTreeItem-content": {
        mb: 0.5,
        py: 1,
        px: 2,
        borderRadius: 0.5,
        backgroundColor: "background.paper",
    },
    "& .MuiTreeItem-iconContainer:empty": {
        display: "none",
    },
};
const treeItemLabelSx = {
    display: "flex",
    alignItems: "center",
    gap: 1,
};
const ParentTreeItemSx = {
    "& > .MuiTreeItem-content": {
        ".MuiTreeItem-label": {
            fontWeight: "fontWeightBold",
        },
    },
};

const NodeItem = (props: { item: DataNode }) => {
    const [id, label, items = [], nodeType, _] = props.item;
    return (
        <TreeItem
            key={id}
            nodeId={id}
            data-nodetype={NodeType.NODE.toString()}
            label={
                <Box sx={treeItemLabelSx}>
                    <DatanodeIcon fontSize="small" color="primary" />
                    {label}
                </Box>
            }
        />
    );
};

const PipelineItem = (props: { item: Pipeline }) => {
    const [id, label, items = [], nodeType, _] = props.item;

    return (
        <TreeItem
            key={id}
            nodeId={id}
            data-nodetype={NodeType.PIPELINE.toString()}
            label={
                <Box sx={treeItemLabelSx}>
                    <PipelineIcon fontSize="small" color="primary" />
                    {label}
                </Box>
            }
            sx={ParentTreeItemSx}
        >
            {items
                ? items.map((item) => {
                      return <NodeItem item={item} />;
                  })
                : null}
        </TreeItem>
    );
};

const ScenarioItem = (props: { item: Scenario }) => {
    const [id, label, items = [], nodeType, _] = props.item;
    return (
        <TreeItem
            key={id}
            nodeId={id}
            data-nodetype={NodeType.SCENARIO.toString()}
            label={
                <Box sx={treeItemLabelSx}>
                    <ScenarioIcon fontSize="small" color="primary" />
                    {label}
                </Box>
            }
            sx={ParentTreeItemSx}
        >
            {items
                ? items.map((item: any) => {
                      const [id, label, items = [], nodeType, _] = item;
                      return nodeType === NodeType.PIPELINE ? <PipelineItem item={item} /> : <NodeItem item={item} />;
                  })
                : null}
        </TreeItem>
    );
};

const CycleItem = (props: { item: Cycle }) => {
    const [id, label, items = [], nodeType, _] = props.item;
    return (
        <TreeItem
            key={id}
            nodeId={id}
            data-nodetype={NodeType.CYCLE.toString()}
            label={
                <Box sx={treeItemLabelSx}>
                    <CycleIcon fontSize="small" color="primary" />
                    {label}
                </Box>
            }
            sx={ParentTreeItemSx}
        >
            {items
                ? items.map((item: any) => {
                      const [id, label, items = [], nodeType, _] = item;
                      return nodeType === NodeType.SCENARIO ? <ScenarioItem item={item} /> : <NodeItem item={item} />;
                  })
                : null}
        </TreeItem>
    );
};

const NodeSelector = (props: NodeSelectorProps) => {
    const { id = "", datanodes } = props;

    const dispatch = useDispatch();
    const module = useModule();

    const onSelect = useCallback((e: React.SyntheticEvent | undefined, nodeId: string) => {
        const keyId = nodeId || "";
        const { nodetype = "" } = e.currentTarget.dataset || {};
        if (nodetype === NodeType.NODE.toString()) {
            //TODO: handle on select node
            dispatch(createSendActionNameAction(id, module, props.onDataNodeSelect, keyId));
        }
    }, []);

    return (
        <>
            <Box sx={MainBoxSx}>
                <TreeView
                    defaultCollapseIcon={<ExpandMore />}
                    defaultExpandIcon={<ChevronRight />}
                    sx={TreeViewSx}
                    onNodeSelect={onSelect}
                >
                    {datanodes
                        ? datanodes.map((item) => {
                              const [id, label, items = [], nodeType, _] = item;
                              return nodeType === NodeType.CYCLE ? (
                                  <CycleItem item={item as Cycle} />
                              ) : nodeType === NodeType.SCENARIO ? (
                                  <ScenarioItem item={item as Scenario} />
                              ) : (
                                  <NodeItem item={item as DataNode} />
                              );
                          })
                        : null}
                </TreeView>
                <Box>{props.error}</Box>
            </Box>
        </>
    );
};

export default NodeSelector;
