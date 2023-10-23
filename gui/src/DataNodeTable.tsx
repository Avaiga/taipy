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

import React, { useEffect, useState, useCallback, useMemo, MouseEvent, ChangeEvent, MutableRefObject } from "react";

import { TableChartOutlined, BarChartOutlined, RefreshOutlined } from "@mui/icons-material";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import Grid from "@mui/material/Grid";
import InputLabel from "@mui/material/InputLabel";
import OutlinedInput from "@mui/material/OutlinedInput";
import ListItemText from "@mui/material/ListItemText";
import MenuItem from "@mui/material/MenuItem";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import Switch from "@mui/material/Switch";
import TextField from "@mui/material/TextField";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";

import { ColumnDesc, Table, TraceValueType, createSendActionNameAction, useDispatch, useModule } from "taipy-gui";

import { ChartViewType, MenuProps, TableViewType, selectSx, tabularHeaderSx } from "./utils";

interface DataNodeTableProps {
    active: boolean;
    nodeId?: string;
    configId?: string;
    data?: Record<string, TraceValueType>;
    columns?: Record<string, ColumnDesc>;
    updateVarName?: string;
    uniqid: string;
    onEdit?: string;
    onViewTypeChange: (e: MouseEvent, value?: string) => void;
    onLock?: string;
    editInProgress?: boolean;
    editLock: MutableRefObject<boolean>;
    editable: boolean;
}

const pushRightSx = { ml: "auto" };

const DataNodeTable = (props: DataNodeTableProps) => {
    const { uniqid, configId, nodeId, columns = "", onViewTypeChange, editable } = props;

    const dispatch = useDispatch();
    const module = useModule();

    // tabular selected columns
    const [selectedCols, setSelectedCols] = useState<string[]>([]);
    const onColsChange = useCallback(
        (e: SelectChangeEvent<typeof selectedCols>) => {
            const sc = typeof e.target.value == "string" ? e.target.value.split(",") : e.target.value;
            localStorage && localStorage.setItem(`${configId}-selected-cols`, JSON.stringify(sc));
            setSelectedCols(sc);
        },
        [configId]
    );
    const resetCols = useCallback(() => {
        localStorage && localStorage.removeItem(`${configId}-selected-cols`);
        columns && setSelectedCols(Object.entries(columns).map((e) => e[1].dfid));
    }, [configId, columns]);

    useEffect(() => {
        if (columns) {
            let tc = Object.entries(columns).map((e) => e[1].dfid);
            const storedSel = localStorage && localStorage.getItem(`${configId}-selected-cols`);
            if (storedSel) {
                try {
                    const storedCols = JSON.parse(storedSel);
                    if (Array.isArray(storedCols)) {
                        tc = tc.filter((c) => storedCols.includes(c));
                    }
                } catch {
                    // do nothing
                }
            }
            setSelectedCols(tc);
        }
    }, [columns, configId]);

    // tabular columns
    const [tabCols, setTabCols] = useState<Record<string, ColumnDesc>>({});
    useEffect(() => {
        if (columns) {
            const res = {} as Record<string, ColumnDesc>;
            const dfids = {} as Record<string, string>;
            Object.entries(columns).forEach(([k, v]) => (dfids[v.dfid] = k));
            selectedCols.forEach((c) => dfids[c] && (res[dfids[c]] = columns[dfids[c]]));
            setTabCols(res);
        }
    }, [columns, selectedCols]);

    const [tableEdit, setTableEdit] = useState(false);
    const toggleTableEdit = useCallback(
        () =>
            setTableEdit((e) => {
                props.editLock.current = !e;
                dispatch(createSendActionNameAction("", module, props.onLock, { id: nodeId, lock: !e }));
                return !e;
            }),
        [nodeId, dispatch, module, props.onLock, props.editLock]
    );

    const userData = useMemo(() => ({ dn_id: nodeId, comment: "" }), [nodeId]);
    const [comment, setComment] = useState("");
    const changeComment = useCallback(
        (e: ChangeEvent<HTMLInputElement>) => {
            setComment(e.currentTarget.value);
            userData.comment = e.currentTarget.value;
        },
        [userData]
    );

    return (
        <>
            <Grid container sx={tabularHeaderSx}>
                <Grid item>
                    <Box className="taipy-toggle">
                        <ToggleButtonGroup onChange={onViewTypeChange} exclusive value={TableViewType} color="primary">
                            <ToggleButton value={TableViewType}>
                                <TableChartOutlined />
                            </ToggleButton>
                            <ToggleButton value={ChartViewType}>
                                <BarChartOutlined />
                            </ToggleButton>
                        </ToggleButtonGroup>
                    </Box>
                </Grid>
                <Grid item>
                    <FormControl sx={selectSx} fullWidth className="taipy-selector">
                        <InputLabel id={uniqid + "-cols-label"}>Columns</InputLabel>
                        <Select
                            labelId={uniqid + "-cols-label"}
                            multiple
                            value={selectedCols}
                            onChange={onColsChange}
                            input={<OutlinedInput label="Columns" fullWidth />}
                            renderValue={(selected) => selected.join(", ")}
                            MenuProps={MenuProps}
                            fullWidth
                        >
                            {Object.values(columns || {}).map((colDesc) => (
                                <MenuItem key={colDesc.dfid} value={colDesc.dfid}>
                                    <Checkbox checked={selectedCols.includes(colDesc.dfid)} />
                                    <ListItemText primary={colDesc.dfid} />
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>
                <Grid item>
                    <Button onClick={resetCols} variant="text" color="primary" className="taipy-button">
                        <RefreshOutlined /> Reset View
                    </Button>
                </Grid>
                {tableEdit ? (
                    <Grid item sx={pushRightSx}>
                        <TextField value={comment} onChange={changeComment} label="Comment"></TextField>
                    </Grid>
                ) : null}
                <Grid item sx={tableEdit ? undefined : pushRightSx}>
                    <FormControlLabel
                        disabled={!props.active || !editable || !!props.editInProgress}
                        control={<Switch color="primary" checked={tableEdit} onChange={toggleTableEdit} />}
                        label="Edit data"
                        labelPlacement="start"
                    />
                </Grid>
            </Grid>
            <Table
                active={props.active}
                defaultColumns={JSON.stringify(tabCols)}
                updateVarName={props.updateVarName}
                data={props.data}
                userData={userData}
                onEdit={tableEdit ? props.onEdit : undefined}
                filter={true}
                libClassName="taipy-table"
            />
        </>
    );
};

export default DataNodeTable;
