import React, { useState, useContext, useCallback, useEffect, useMemo, SyntheticEvent } from "react";
import Box from "@mui/material/Box";
import MuiTreeView from "@mui/lab/TreeView";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import TreeItem from "@mui/lab/TreeItem";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";

import { TaipyContext } from "../../context/taipyContext";
import { createSendUpdateAction } from "../../context/taipyReducers";
import { boxSx, LovImage, LovItem, paperBaseSx, SelTreeProps, showItem, treeSelBaseSx, useLovListMemo } from "./lovUtils";
import { useDispatchRequestUpdateOnFirstRender, useDynamicProperty } from "../../utils/hooks";

const renderTree = (lov: LovItem[], active: boolean, searchValue: string) => {
    return lov.map((li) => {
        const children = li.children ? renderTree(li.children, active, searchValue) : [];
        if (!children.filter(c => c).length && !showItem(li, searchValue)) {
            return null;
        }
        return <TreeItem
                key={li.id}
                nodeId={li.id}
                label={typeof li.item === "string" ? li.item : li.item ? <LovImage item={li.item} />: "undefined item"}
                disabled={!active}
            >
                {children}
            </TreeItem>
    });
}

const TreeView = (props: SelTreeProps) => {
    const {
        id,
        defaultValue = "",
        value,
        tp_varname = "",
        defaultLov = "",
        filter = false,
        multiple = false,
        className,
        propagate = true,
        lov,
        tp_updatevars = "",
        width = 360,
        height,
    } = props;
    const [searchValue, setSearchValue] = useState("");
    const [selectedValue, setSelectedValue] = useState<string[] | string>(multiple ? []: "");
    const { dispatch } = useContext(TaipyContext);

    const active = useDynamicProperty(props.active, props.defaultActive, true);

    useDispatchRequestUpdateOnFirstRender(dispatch, id, tp_updatevars, tp_varname);

    const lovList = useLovListMemo(lov, defaultLov, true);
    const treeSx = useMemo(() => ({...treeSelBaseSx, maxWidth: width}), [width]);
    const paperSx = useMemo(() => height === undefined ? paperBaseSx : {...paperBaseSx, maxHeight: height}, [height]);

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
            dispatch(createSendUpdateAction(tp_varname, Array.isArray(nodeIds) ? nodeIds : [nodeIds], propagate));
        },
        [tp_varname, dispatch, propagate]
    );

    const handleInput = useCallback((e) => setSearchValue(e.target.value), []);

    const treeProps = useMemo(
        () =>
            multiple ? { multiSelect: true as true | undefined, selected: selectedValue as string[] } : { selected: selectedValue as string },
        [multiple, selectedValue]
    );

    return (
        <Box id={id} sx={boxSx} className={className}>
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
                    {...treeProps}
                >
                    {renderTree(lovList, !!active, searchValue)}
                </MuiTreeView>
            </Paper>
        </Box>
    );
};

export default TreeView;
