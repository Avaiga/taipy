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

import React, { useCallback } from "react";
import Box from "@mui/material/Box";
import { ChevronRight, ExpandMore } from "@mui/icons-material";
import TreeItem from "@mui/lab/TreeItem";
import TreeView from "@mui/lab/TreeView";
import { useDispatch, useModule, createSendActionNameAction } from "taipy-gui";
import { Cycles, NodeType, Scenarios } from "./utils/types";
import { Cycle, Datanode, Pipeline, Scenario as ScenarioIcon } from "./icons";

interface DataNodeExplorerProps {
    id?: string;
    updateVarName?: string;
    scenarios?: Cycles | Scenarios;
    coreChanged?: Record<string, unknown>;
    updateVars?: string;
    configs?: Array<[string, string]>;
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

const buildId = (id: string, type: NodeType) => {
    return JSON.stringify({ id: id, type: type });
};

const NodeItem = ({ item = [] }: { item: any[] }) => {
    const [id, label, items = [], nodeType, _] = item;
    return (
        <TreeItem
            key={id}
            nodeId={buildId(id, nodeType)}
            label={
                <Box sx={treeItemLabelSx}>
                    <Datanode fontSize="small" color="primary" />
                    {label}
                </Box>
            }
        />
    );
};

const PipelineItem = ({ item = [] }) => {
    const [id, label, items = [], nodeType, _] = item;

    return (
        <TreeItem
            key={id}
            nodeId={buildId(id, nodeType)}
            label={
                <Box sx={treeItemLabelSx}>
                    <Pipeline fontSize="small" color="primary" />
                    {label}
                </Box>
            }
            sx={ParentTreeItemSx}
        >
            {items &&
                items.map((item: any) => {
                    return <NodeItem item={item} />;
                })}
        </TreeItem>
    );
};

const ScenarioItem = ({ item = [] }: { item: any[] }) => {
    const [id, label, items = [], nodeType, _] = item;
    return (
        <TreeItem
            key={id}
            nodeId={buildId(id, nodeType)}
            label={
                <Box sx={treeItemLabelSx}>
                    <ScenarioIcon fontSize="small" color="primary" />
                    {label}
                </Box>
            }
            sx={ParentTreeItemSx}
        >
            {items &&
                items.map((item: any) => {
                    const [id, label, items = [], nodeType, _] = item;
                    return nodeType === NodeType.PIPELINE ? <PipelineItem item={item} /> : <NodeItem item={item} />;
                })}
        </TreeItem>
    );
};

const CycleItem = ({ item }: { item: any[] }) => {
    const [id, label, items = [], nodeType, _] = item;
    return (
        <TreeItem
            key={id}
            nodeId={buildId(id, nodeType)}
            label={
                <Box sx={treeItemLabelSx}>
                    <Cycle fontSize="small" color="primary" />
                    {label}
                </Box>
            }
            sx={ParentTreeItemSx}
        >
            {items &&
                items.map((item: any) => {
                    const [id, label, items = [], nodeType, _] = item;
                    return nodeType === NodeType.SCENARIO ? <ScenarioItem item={item} /> : <NodeItem item={item} />;
                })}
        </TreeItem>
    );
};

const DataNodeExplorer = (props: DataNodeExplorerProps) => {
    const { id = "", scenarios = [] } = props;

    const dispatch = useDispatch();
    const module = useModule();

    const onSelect = useCallback((e: React.SyntheticEvent | undefined, nodeIds: string) => {
        const selected = (nodeIds && JSON.parse(nodeIds)) || "";
        if (selected && selected.type == NodeType.NODE) {
            //TODO: handle on select node
            dispatch(createSendActionNameAction(id, module, props.onDataNodeSelect, selected.id));
        }
    }, []);

    return (
        <div>
            <Box sx={MainBoxSx}>
                <TreeView
                    defaultCollapseIcon={<ExpandMore />}
                    defaultExpandIcon={<ChevronRight />}
                    sx={TreeViewSx}
                    onNodeSelect={onSelect}
                >
                    {scenarios
                        ? scenarios.map((item) => {
                              const [id, label, items = [], nodeType, _] = item;
                              return nodeType === NodeType.CYCLE ? (
                                  <CycleItem item={item} />
                              ) : nodeType === NodeType.SCENARIO ? (
                                  <ScenarioItem item={item} />
                              ) : (
                                  <NodeItem item={item} />
                              );
                          })
                        : null}
                </TreeView>
                <Box>{props.error}</Box>
            </Box>
        </div>
    );
};

export default DataNodeExplorer;
