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

import React, { ChangeEvent, useCallback, useEffect, useRef, useState } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Popover, { PopoverOrigin } from "@mui/material/Popover";
import IconButton from "@mui/material/IconButton";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import Tooltip from "@mui/material/Tooltip";
import FormControl from "@mui/material/FormControl";
import OutlinedInput from "@mui/material/OutlinedInput";
import TextField from "@mui/material/TextField";
import CheckIcon from "@mui/icons-material/Check";
import ClearIcon from "@mui/icons-material/Clear";
import DeleteIcon from "@mui/icons-material/Delete";
import FilterListIcon from "@mui/icons-material/FilterList";
import SendIcon from "@mui/icons-material/Send";
import { DateField, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";

import { ColumnDesc, defaultDateFormat, iconInRowSx, iconsWrapperSx } from "./tableUtils";
import { getDateTime, getTypeFromDf } from "../../utils";
import { getSuffixedClassNames } from "./utils";

export interface FilterDesc {
    col: string;
    action: string;
    value: string | number | boolean | Date;
}

interface TableFilterProps {
    columns: Record<string, ColumnDesc>;
    colsOrder: Array<string>;
    onValidate: (data: Array<FilterDesc>) => void;
    appliedFilters?: Array<FilterDesc>;
    className?: string;
}

interface FilterRowProps {
    idx: number;
    filter?: FilterDesc;
    columns: Record<string, ColumnDesc>;
    colsOrder: Array<string>;
    setFilter: (idx: number, fd: FilterDesc, remove?: boolean) => void;
}

const anchorOrigin = {
    vertical: "bottom",
    horizontal: "right",
} as PopoverOrigin;

const actionsByType = {
    string: { "==": "equals", contains: "contains", "!=": "not equals" },
    number: {
        "<": "less",
        "<=": "less equals",
        "==": "equals",
        "!=": "not equals",
        ">=": "greater equals",
        ">": "greater",
    },
    boolean: { "==": "equals", "!=": "not equals" },
    date: {
        "<": "before",
        "<=": "before equal",
        "==": "equals",
        "!=": "not equals",
        ">=": "after equal",
        ">": "after",
    },
} as Record<string, Record<string, string>>;

const getActionsByType = (colType?: string) =>
    (colType && colType in actionsByType && actionsByType[colType]) || actionsByType["string"];

const filtersSx = {
    display: "flex",
    flexDirection: "column",
    alignItems: "stretch",
    p: 4,
};

const filterBoxSx = {
    display: "flex",
    flexDirection: "row",
    gap: 2,
};

const buttonBoxSx = {
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-between",
    mt: 2,
    gap: 2,
};

const colSx = { width: "15em" };
const actSx = { width: "10em" };
const valSx = { width: "15em" };

const getFilterDesc = (columns: Record<string, ColumnDesc>, colId?: string, act?: string, val?: string) => {
    if (colId && act && val !== undefined) {
        const colType = getTypeFromDf(columns[colId].type);
        if (!val && (colType == "date" || colType == "number" || colType == "boolean")) {
            return;
        }
        try {
            const typedVal =
                colType == "number"
                    ? parseFloat(val)
                    : colType == "boolean"
                    ? val == "1"
                    : colType == "date"
                    ? getDateTime(val)
                    : val;
            return {
                col: columns[colId].dfid,
                action: act,
                value: typedVal,
            } as FilterDesc;
        } catch (e) {
            console.info("could not parse value ", val, e);
        }
    }
};

const FilterRow = (props: FilterRowProps) => {
    const { idx, setFilter, columns, colsOrder, filter } = props;

    const [colId, setColId] = useState<string>("");
    const [action, setAction] = useState<string>("");
    const [val, setVal] = useState<string>("");
    const [enableCheck, setEnableCheck] = useState(false);
    const [enableDel, setEnableDel] = useState(false);

    const onColSelect = useCallback(
        (e: SelectChangeEvent<string>) => {
            setColId(e.target.value);
            setEnableCheck(!!getFilterDesc(columns, e.target.value, action, val));
        },
        [columns, action, val]
    );
    const onActSelect = useCallback(
        (e: SelectChangeEvent<string>) => {
            setAction(e.target.value);
            setEnableCheck(!!getFilterDesc(columns, colId, e.target.value, val));
        },
        [columns, colId, val]
    );
    const onValueChange = useCallback(
        (e: ChangeEvent<HTMLInputElement>) => {
            setVal(e.target.value);
            setEnableCheck(!!getFilterDesc(columns, colId, action, e.target.value));
        },
        [columns, colId, action]
    );
    const onValueSelect = useCallback(
        (e: SelectChangeEvent<string>) => {
            setVal(e.target.value);
            setEnableCheck(!!getFilterDesc(columns, colId, action, e.target.value));
        },
        [columns, colId, action]
    );
    const onDateChange = useCallback(
        (v: Date | null) => {
            let dv;
            try {
                dv = v?.toISOString() || "";
            } catch (e) {
                dv = "";
                console.info("TableFilter.onDateChange", v);
            }
            setVal(dv);
            setEnableCheck(!!getFilterDesc(columns, colId, action, dv));
        },
        [columns, colId, action]
    );

    const onDeleteClick = useCallback(() => setFilter(idx, undefined as unknown as FilterDesc, true), [idx, setFilter]);
    const onCheckClick = useCallback(() => {
        const fd = getFilterDesc(columns, colId, action, val);
        fd && setFilter(idx, fd);
    }, [idx, setFilter, columns, colId, action, val]);

    useEffect(() => {
        if (filter && idx > -1) {
            const col = Object.keys(columns).find((col) => columns[col].dfid === filter.col) || "";
            setColId(col);
            setAction(filter.action);
            setVal(filter.value as string);
            setEnableCheck(false);
            setEnableDel(!!getFilterDesc(columns, col, filter.action, filter.value as string));
        } else {
            setColId("");
            setAction("");
            setVal("");
            setEnableCheck(false);
            setEnableDel(false);
        }
    }, [columns, filter, idx]);

    const colType = getTypeFromDf(colId in columns ? columns[colId].type : "");
    const colFormat = colId in columns && columns[colId].format ? columns[colId].format : defaultDateFormat;

    return (
        <Box sx={filterBoxSx}>
            <FormControl margin="dense">
                <InputLabel>Column</InputLabel>
                <Select value={colId || ""} onChange={onColSelect} sx={colSx} input={<OutlinedInput label="Column" />}>
                    {colsOrder.map((col) =>
                        columns[col].filter ? (
                            <MenuItem key={col} value={col}>
                                {columns[col].title || columns[col].dfid}
                            </MenuItem>
                        ) : null
                    )}
                </Select>
            </FormControl>
            <FormControl margin="dense">
                <InputLabel>Action</InputLabel>
                <Select value={action || ""} onChange={onActSelect} sx={actSx} input={<OutlinedInput label="Action" />}>
                    {Object.keys(getActionsByType(colType)).map((a) => (
                        <MenuItem key={a} value={a}>
                            {getActionsByType(colType)[a]}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>
            {colType == "number" ? (
                <TextField
                    type="number"
                    value={typeof val == "number" ? val : val || ""}
                    onChange={onValueChange}
                    label="Number"
                    sx={valSx}
                    margin="dense"
                />
            ) : colType == "boolean" ? (
                <FormControl margin="dense">
                    <InputLabel>Boolean</InputLabel>
                    <Select
                        value={typeof val === "boolean" ? (val ? "1" : "0") : val || ""}
                        onChange={onValueSelect}
                        sx={valSx}
                        input={<OutlinedInput label="Boolean" />}
                    >
                        <MenuItem value={"1"}>True</MenuItem>
                        <MenuItem value={"0"}>False</MenuItem>
                    </Select>
                </FormControl>
            ) : colType == "date" ? (
                <DateField
                    value={(val && new Date(val)) || null}
                    onChange={onDateChange}
                    format={colFormat}
                    sx={valSx}
                    margin="dense"
                />
            ) : (
                <TextField
                    value={val || ""}
                    onChange={onValueChange}
                    label={`${val ? "" : "Empty "}String`}
                    sx={valSx}
                    margin="dense"
                />
            )}
            <Tooltip title="Validate">
                <Box component="span" sx={iconsWrapperSx}>
                    <IconButton onClick={onCheckClick} disabled={!enableCheck} sx={iconInRowSx}>
                        <CheckIcon />
                    </IconButton>
                </Box>
            </Tooltip>
            <Tooltip title="Delete">
                <Box component="span" sx={iconsWrapperSx}>
                    <IconButton onClick={onDeleteClick} disabled={!enableDel} sx={iconInRowSx}>
                        <DeleteIcon />
                    </IconButton>
                </Box>
            </Tooltip>
        </Box>
    );
};

const TableFilter = (props: TableFilterProps) => {
    const { onValidate, appliedFilters, columns, colsOrder, className = "" } = props;

    const [showFilter, setShowFilter] = useState(false);
    const filterRef = useRef<HTMLButtonElement | null>(null);
    const [filters, setFilters] = useState<Array<FilterDesc>>([]);

    const onShowFilterClick = useCallback(() => setShowFilter((f) => !f), []);

    const updateFilter = useCallback((idx: number, nfd: FilterDesc, remove?: boolean) => {
        setFilters((fds) => {
            if (idx > -1) {
                if (remove) {
                    fds.splice(idx, 1);
                    return [...fds];
                }
                return fds.map((fd, index) => (index == idx ? nfd : fd));
            }
            if (remove) {
                return fds;
            }
            return [...fds, nfd];
        });
    }, []);

    const onApply = useCallback(() => {
        onValidate([...filters]);
        onShowFilterClick();
    }, [onValidate, filters, onShowFilterClick]);
    const onRemove = useCallback(() => {
        onValidate([]);
        onShowFilterClick();
    }, [onValidate, onShowFilterClick]);

    useEffect(() => {
        columns && appliedFilters && setFilters(appliedFilters.filter((fd) => Object.values(columns).some((cd) => cd.dfid === fd.col)));
    }, [columns, appliedFilters]);

    return (
        <>
            <Tooltip title="Filter list">
                <IconButton
                    onClick={onShowFilterClick}
                    size="small"
                    ref={filterRef}
                    sx={iconInRowSx}
                    className={getSuffixedClassNames(className, "-filter-icon")}
                >
                    <FilterListIcon fontSize="inherit" />
                </IconButton>
            </Tooltip>
            <Popover
                anchorEl={filterRef.current}
                anchorOrigin={anchorOrigin}
                open={showFilter}
                onClose={onShowFilterClick}
                className={getSuffixedClassNames(className, "-filter")}
            >
                <Box sx={filtersSx}>
                    <LocalizationProvider dateAdapter={AdapterDateFns}>
                        {filters.map((fd, idx) => (
                            <FilterRow
                                key={"fd" + idx}
                                idx={idx}
                                filter={fd}
                                columns={columns}
                                colsOrder={colsOrder}
                                setFilter={updateFilter}
                            />
                        ))}
                        <FilterRow
                            idx={-(filters.length + 1)}
                            columns={columns}
                            colsOrder={colsOrder}
                            setFilter={updateFilter}
                        />
                    </LocalizationProvider>
                    <Box sx={buttonBoxSx}>
                        <Button
                            endIcon={<ClearIcon />}
                            onClick={onRemove}
                            disabled={filters.length == 0}
                            variant="outlined"
                            color="inherit"
                        >
                            {`Reset list (remove applied filter${filters.length > 1 ? "s" : ""})`}
                        </Button>
                        <Button
                            endIcon={<SendIcon />}
                            onClick={onApply}
                            disabled={filters.length == 0}
                            variant="outlined"
                        >
                            {`Apply ${filters.length} filter${filters.length > 1 ? "s" : ""}`}
                        </Button>
                    </Box>
                </Box>
            </Popover>
        </>
    );
};

export default TableFilter;
