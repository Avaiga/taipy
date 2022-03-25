import React, { useState, useContext, useCallback, useEffect, useMemo, SyntheticEvent } from "react";
import Box from "@mui/material/Box";
import MuiTreeView from "@mui/lab/TreeView";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import TreeItem from "@mui/lab/TreeItem";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";

import { TaipyContext } from "../../context/taipyContext";
import { createSendUpdateAction } from "../../context/taipyReducers";
import {
    boxSx,
    isLovParent,
    LovImage,
    paperBaseSx,
    SelTreeProps,
    showItem,
    treeSelBaseSx,
    useLovListMemo,
} from "./lovUtils";
import { useDispatchRequestUpdateOnFirstRender, useDynamicProperty } from "../../utils/hooks";
import { LovItem } from "../../utils/lov";
import { getUpdateVar } from "./utils";

const renderTree = (lov: LovItem[], active: boolean, searchValue: string) => {
    return lov.map((li) => {
        const children = li.children ? renderTree(li.children, active, searchValue) : [];
        if (!children.filter((c) => c).length && !showItem(li, searchValue)) {
            return null;
        }
        return (
            <TreeItem
                key={li.id}
                nodeId={li.id}
                label={typeof li.item === "string" ? li.item : li.item ? <LovImage item={li.item} /> : "undefined item"}
                disabled={!active}
            >
                {children}
            </TreeItem>
        );
    });
};

interface TreeViewProps extends SelTreeProps {
    defaultExpanded?: string | boolean;
    expanded?: string[] | boolean;
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
        className,
        propagate = true,
        lov,
        updateVars = "",
        width = 360,
        height,
        valueById,
    } = props;
    const [searchValue, setSearchValue] = useState("");
    const [selectedValue, setSelectedValue] = useState<string[] | string>(multiple ? [] : "");
    const [oneExpanded, setOneExpanded] = useState(false);
    const [refreshExpanded, setRefreshExpanded] = useState(false);
    const [expandedNodes, setExpandedNodes] = useState<string[]>([]);
    const { dispatch } = useContext(TaipyContext);

    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    useDispatchRequestUpdateOnFirstRender(dispatch, id, updateVars, updateVarName);

    const lovList = useLovListMemo(lov, defaultLov, true);
    const treeSx = useMemo(() => ({ ...treeSelBaseSx, maxWidth: width }), [width]);
    const paperSx = useMemo(
        () => (height === undefined ? paperBaseSx : { ...paperBaseSx, maxHeight: height }),
        [height]
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
            setSelectedValue(
                multiple ? (Array.isArray(value) ? value : [value]) : Array.isArray(value) ? value[0] : value
            );
        } else if (defaultValue) {
            let parsedValue;
            try {
                parsedValue = JSON.parse(defaultValue);
            } catch (e) {
                parsedValue = defaultValue;
            }
            setSelectedValue(
                multiple
                    ? Array.isArray(parsedValue)
                        ? parsedValue
                        : [parsedValue]
                    : Array.isArray(parsedValue)
                    ? parsedValue[0]
                    : parsedValue
            );
        }
    }, [defaultValue, value, multiple]);

    const clickHandler = useCallback(
        (event: SyntheticEvent, nodeIds: string[] | string) => {
            setSelectedValue(nodeIds);
            updateVarName &&
                dispatch(
                    createSendUpdateAction(
                        updateVarName,
                        Array.isArray(nodeIds) ? nodeIds : [nodeIds], 
                        props.tp_onChange,
                        propagate,
                        valueById ? undefined : getUpdateVar(updateVars, "lov")
                    )
                );
        },
        [updateVarName, dispatch, propagate, updateVars, valueById, props.tp_onChange]
    );

    const handleInput = useCallback((e) => setSearchValue(e.target.value), []);

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
                        dispatch(createSendUpdateAction(expVar, nodeIds, props.tp_onChange, propagate));
                    }
                    return nodeIds;
                });
            } else {
                setExpandedNodes(nodeIds);
                if (refreshExpanded) {
                    dispatch(createSendUpdateAction(expVar, nodeIds, props.tp_onChange, propagate));
                }
            }
        },
        [oneExpanded, refreshExpanded, lovList, propagate, updateVars, dispatch, props.tp_onChange]
    );

    const treeProps = useMemo(
        () =>
            multiple
                ? { multiSelect: true as true | undefined, selected: selectedValue as string[] }
                : { selected: selectedValue as string },
        [multiple, selectedValue]
    );

    return (
        <Box id={id} sx={boxSx} className={className}>
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
                            />
                        )}
                    </Box>
                    <MuiTreeView
                        aria-label="tree"
                        defaultCollapseIcon={<ExpandMoreIcon />}
                        defaultExpandIcon={<ChevronRightIcon />}
                        sx={treeSx}
                        onNodeSelect={clickHandler}
                        expanded={expandedNodes}
                        onNodeToggle={handleNodeToggle}
                        {...treeProps}
                    >
                        {renderTree(lovList, !!active, searchValue)}
                    </MuiTreeView>
                </Paper>
            </Tooltip>
        </Box>
    );
};

export default TreeView;
