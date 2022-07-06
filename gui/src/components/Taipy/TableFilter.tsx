import React, { ChangeEvent, useCallback, useEffect, useRef, useState } from "react";
import Box from "@mui/material/Box";
import Popover, { PopoverOrigin } from "@mui/material/Popover";
import IconButton from "@mui/material/IconButton";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import Tooltip from "@mui/material/Tooltip";
import FormControl from "@mui/material/FormControl";
import OutlinedInput from "@mui/material/OutlinedInput";
import TextField, { TextFieldProps } from "@mui/material/TextField";
import { DatePicker } from "@mui/x-date-pickers";
import CheckIcon from "@mui/icons-material/Check";
import ClearIcon from "@mui/icons-material/Clear";
import DeleteIcon from "@mui/icons-material/Delete";
import FilterListIcon from "@mui/icons-material/FilterList";
import SendIcon from "@mui/icons-material/Send";

import { ColumnDesc, iconInRowSx, EDIT_COL } from "./tableUtils";
import { getTypeFromDf } from "../../utils";
import { Button } from "@mui/material";

export interface FilterDesc {
    col: string;
    action: string;
    value: string | number | boolean | Date;
}

interface TableFilterProps {
    columns: Record<string, ColumnDesc>;
    onValidate: (data: Array<FilterDesc>) => void;
    filters?: Array<FilterDesc>;
}

interface FilterRowProps {
    idx: number;
    filter?: FilterDesc;
    columns: Record<string, ColumnDesc>;
    setFilter: (idx: number, fd: FilterDesc, remove?: boolean) => void;
}

const anchorOrigin = {
    vertical: "bottom",
    horizontal: "right",
} as PopoverOrigin;

const actionsByType = {
    string: ["==", "like", "!="],
    number: ["<", "<=", "==", "!=", ">=", ">"],
    boolean: ["==", "!="],
    date: ["<", "<=", "==", "!=", ">=", ">"],
} as Record<string, Array<string>>;

const getActionsByType = (colType?: string) =>
    (colType && colType in actionsByType && actionsByType[colType]) || actionsByType["string"];

const filtersSx = {
    display: "flex",
    alignItems: "flex-start",
    flexDirection: "column",
    p: 1,
    m: 1,
    bgcolor: "background.paper",
    borderRadius: 1,
};

const filterBoxSx = {
    display: "flex",
    flexDirection: "row",
    p: 1,
    m: 1,
    bgcolor: "background.paper",
    borderRadius: 1,
    gap: "1em",
};

const getFilterDesc = (columns: Record<string, ColumnDesc>, colId?: string, act?: string, val?: string) => {
    if (colId && act && val !== undefined) {
        const colType = getTypeFromDf(columns[colId].type);
        if (colType == "date" && !val) {
            return;
        }
        const typedVal = colType == "number" ? parseFloat(val) : colType == "boolean" ? val == "1" : val;
        return {
            col: colId,
            action: act,
            value: typedVal,
        } as FilterDesc;
    }
};

const renderInput = (params: TextFieldProps) => <TextField {...params} />;

const FilterRow = (props: FilterRowProps) => {
    const { idx, setFilter, columns, filter } = props;

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
            setVal(v?.toISOString() || "");
            setEnableCheck(!!getFilterDesc(columns, colId, action, v?.toISOString()));
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
            setColId(filter.col);
            setAction(filter.action);
            setVal(filter.value as string);
            setEnableCheck(false);
            setEnableDel(!!getFilterDesc(columns, filter.col, filter.action, filter.value as string));
        } else {
            setColId("");
            setAction("");
            setVal("");
            setEnableCheck(false);
            setEnableDel(false);
        }
    }, [columns, filter, idx]);

    const colType = getTypeFromDf(colId in columns ? columns[colId].type : "");
    const colFormat = colId in columns ? columns[colId].format : undefined;

    return (
        <Box sx={filterBoxSx}>
            <FormControl>
                <InputLabel>Column</InputLabel>
                <Select
                    value={colId || ""}
                    onChange={onColSelect}
                    sx={{ width: "15em" }}
                    input={<OutlinedInput label="Column" />}
                >
                    {Object.keys(columns).map((col, idx) =>
                        col == EDIT_COL ? null : (
                            <MenuItem key={"col" + idx} value={col}>
                                {columns[col].title || columns[col].dfid}
                            </MenuItem>
                        )
                    )}
                </Select>
            </FormControl>
            <FormControl>
                <InputLabel>Action</InputLabel>
                <Select
                    value={action || ""}
                    onChange={onActSelect}
                    sx={{ width: "6em" }}
                    input={<OutlinedInput label="Action" />}
                >
                    {getActionsByType(colType).map((a, idx) => (
                        <MenuItem key={"act" + idx} value={a}>
                            {a}
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
                />
            ) : colType == "boolean" ? (
                <FormControl>
                    <InputLabel>Boolean</InputLabel>
                    <Select
                        value={typeof val === "boolean" ? (val ? "1" : "0") : val || ""}
                        onChange={onValueSelect}
                        sx={{ width: "7em" }}
                        input={<OutlinedInput label="Boolean" />}
                    >
                        <MenuItem value={"1"}>True</MenuItem>
                        <MenuItem value={"0"}>False</MenuItem>
                    </Select>
                </FormControl>
            ) : colType == "date" ? (
                <DatePicker value={val || null} onChange={onDateChange} renderInput={renderInput} inputFormat={colFormat} />
            ) : (
                <TextField value={val || ""} onChange={onValueChange} label="Empty String" />
            )}
            <Tooltip title="Validate">
                <span>
                    <IconButton onClick={onCheckClick} disabled={!enableCheck}>
                        <CheckIcon />
                    </IconButton>
                </span>
            </Tooltip>
            <Tooltip title="Delete">
                <span>
                    <IconButton onClick={onDeleteClick} disabled={!enableDel}>
                        <DeleteIcon />
                    </IconButton>
                </span>
            </Tooltip>
        </Box>
    );
};

export const TableFilter = (props: TableFilterProps) => {
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

    return (
        <>
            <Tooltip title="Filter list">
                <IconButton onClick={onShowFilterClick} size="small" sx={iconInRowSx} ref={filterRef}>
                    <FilterListIcon />
                </IconButton>
            </Tooltip>
            <Popover
                anchorEl={filterRef.current}
                anchorOrigin={anchorOrigin}
                open={showFilter}
                onClose={onShowFilterClick}
            >
                <Box sx={filtersSx}>
                    {filters.map((fd, idx) => (
                        <FilterRow
                            key={"fd" + idx}
                            idx={idx}
                            filter={fd}
                            columns={props.columns}
                            setFilter={updateFilter}
                        />
                    ))}
                    <FilterRow idx={-(filters.length + 1)} columns={props.columns} setFilter={updateFilter} />
                    <Box sx={filterBoxSx}>
                        <Button endIcon={<SendIcon />}>{"Apply filter" + (filters.length > 1 ? "s" : "")}</Button>
                        <Button endIcon={<ClearIcon />}>{"Remove filter" + (filters.length > 1 ? "s" : "")}</Button>
                    </Box>
                </Box>
            </Popover>
        </>
    );
};
