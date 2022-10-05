/*
 * Copyright 2022 Avaiga Private Limited
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

import React, { useState, useCallback, CSSProperties } from "react";
import TableCell, { TableCellProps } from "@mui/material/TableCell";
import Box from "@mui/material/Box";
import Input from "@mui/material/Input";
import IconButton from "@mui/material/IconButton";
import CheckIcon from "@mui/icons-material/Check";
import ClearIcon from "@mui/icons-material/Clear";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import Switch from "@mui/material/Switch";

import { FormatConfig } from "../../context/taipyReducers";
import { getDateTimeString, getNumberString } from "../../utils/index";
import { TaipyActiveProps, TaipyMultiSelectProps } from "./utils";

/**
 * A column description as received by the backend.
 */
export interface ColumnDesc {
    /** The unique column identifier. */
    dfid: string;
    /** The column type. */
    type: string;
    /** The value format. */
    format?: string;
    /** The column title. */
    title?: string;
    /** The order of the column. */
    index: number;
    /** The column width. */
    width?: number | string;
    /** If true, the column cannot be edited. */
    notEditable?: boolean;
    /** The name of the column that holds the CSS classname to
     *  apply to the cells. */
    style?: string;
    /** The value that would replace a NaN value. */
    nanValue?: string;
    /** The TimeZone identifier used if the type is `date`. */
    tz?: string;
    /** The flag that allows filtering. */
    filter?: boolean;
    /** The name of the aggregation function. */
    apply?: string;
    /** The flag that allows the user to aggregate the column. */
    groupBy?: boolean;
    widthHint?: number;
}

export const DEFAULT_SIZE = "small";

export type Order = "asc" | "desc";

/**
 * A cell value type.
 */
export type RowValue = string | number | boolean | null;

/**
 * The definition of a table row.
 *
 * A row definition associates a name (a string) to a type (a {@link RowValue}).
 */
export type RowType = Record<string, RowValue>;

export const EDIT_COL = "taipy_edit";

export const LINE_STYLE = "__taipy_line_style__";

export const getsortByIndex = (cols: Record<string, ColumnDesc>) => (key1: string, key2: string) => {
    if (cols[key1].index < cols[key2].index) {
        return -1;
    }
    if (cols[key1].index > cols[key2].index) {
        return 1;
    }
    return 0;
};

export const defaultDateFormat = "yyyy/MM/dd";

const formatValue = (val: RowValue, col: ColumnDesc, formatConf: FormatConfig, nanValue?: string): string => {
    if (val === null || val === undefined) {
        return "";
    }
    switch (col.type) {
        case "datetime":
            return getDateTimeString(val as string, col.format || defaultDateFormat, formatConf, col.tz);
        case "int":
        case "float":
            if (val === "NaN") {
                return nanValue || "";
            }
            return getNumberString(val as number, col.format, formatConf);
        default:
            return val as string;
    }
};
const VALID_BOOLEAN_STRINGS = ["true", "1", "t", "y", "yes", "yeah", "sure"];

const isBooleanTrue = (val: RowValue) => typeof val == "string" ? VALID_BOOLEAN_STRINGS.some(s => s == val.trim().toLowerCase()) : !!val;

const renderCellValue = (val: RowValue | boolean, col: ColumnDesc, formatConf: FormatConfig, nanValue?: string) => {
    if (val !== null && val !== undefined && col.type && col.type.startsWith("bool")) {
        return <Switch checked={val as boolean} size="small" title={val ? "True" : "False"} sx={iconInRowSx} />;
    }
    return <>{formatValue(val as RowValue, col, formatConf, nanValue)}</>;
};

const getCellProps = (col: ColumnDesc, base: Partial<TableCellProps> = {}): Partial<TableCellProps> => {
    switch (col.type) {
        case "int":
        case "float":
            base.align = "right";
            break;
        case "bool":
            base.align = "center";
            break;
    }
    if (col.width) {
        base.width = col.width;
    }
    return base;
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type TableValueType = Record<string, Record<string, any>>;

export interface TaipyTableProps extends TaipyActiveProps, TaipyMultiSelectProps {
    data?: TableValueType;
    columns: string;
    height?: string;
    width?: string;
    pageSize?: number;
    onEdit?: string;
    onDelete?: string;
    onAdd?: string;
    editable?: boolean;
    defaultEditable?: boolean;
    lineStyle?: string;
    nanValue?: string;
    filter?: boolean;
    size?: "small" | "medium";
    defaultKey?: string; // for testing purposes only
}

export type PageSizeOptionsType = (
    | number
    | {
          value: number;
          label: string;
      }
)[];

export interface TaipyPaginatedTableProps extends TaipyTableProps {
    pageSizeOptions?: string;
    allowAllRows?: boolean;
    showAll?: boolean;
}

export const baseBoxSx = { width: "100%" };
export const paperSx = { width: "100%", mb: 2 };
export const tableSx = { minWidth: 250 };
export const headBoxSx = { display: "flex", alignItems: "flex-start" };

export interface OnCellValidation {
    (value: RowValue, rowIndex: number, colName: string, userValue: string): void;
}

export interface OnRowDeletion {
    (rowIndex: number): void;
}

interface EditableCellProps {
    rowIndex: number;
    value: RowValue;
    colDesc: ColumnDesc;
    formatConfig: FormatConfig;
    onValidation?: OnCellValidation;
    onDeletion?: OnRowDeletion;
    nanValue?: string;
    className?: string;
    tableCellProps?: Partial<TableCellProps>;
}

export const addDeleteColumn = (render: number, columns: Record<string, ColumnDesc>) => {
    if (render) {
        Object.keys(columns).forEach((key) => columns[key].index++);
        columns[EDIT_COL] = {
            dfid: EDIT_COL,
            type: "",
            format: "",
            title: "",
            index: 0,
            width: render * 4 + "em",
            filter: false,
        };
    }
    return columns;
};

export const getClassName = (row: Record<string, unknown>, style?: string) =>
    style ? (row[style] as string) : undefined;

const setInputFocus = (input: HTMLInputElement) => input && input.focus();

const cellBoxSx = { display: "grid", gridTemplateColumns: "1fr auto", alignItems: "center" } as CSSProperties;
export const iconInRowSx = { fontSize: "body2.fontSize" };
const tableFontSx = { fontSize: "body2.fontSize" };

export const EditableCell = (props: EditableCellProps) => {
    const {
        onValidation,
        value,
        colDesc,
        formatConfig,
        rowIndex,
        onDeletion,
        nanValue,
        className,
        tableCellProps = {},
    } = props;
    const [val, setVal] = useState(value);
    const [edit, setEdit] = useState(false);
    const [deletion, setDeletion] = useState(false);

    const onChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => setVal(e.target.value), []);

    const onCheckClick = useCallback(() => {
        let castedVal = val;
        switch (colDesc.type) {
            case "bool":
                castedVal = isBooleanTrue(val);
                break;
            case "int":
                try {
                    castedVal = parseInt(val as string, 10);
                } catch (e) {
                    // ignore
                }
                break;
            case "float":
                try {
                    castedVal = parseFloat(val as string);
                } catch (e) {
                    // ignore
                }
                break;
            }
        onValidation && onValidation(castedVal, rowIndex, colDesc.dfid, val as string);
        setEdit((e) => !e);
    }, [onValidation, val, rowIndex, colDesc.dfid, colDesc.type]);

    const onEditClick = useCallback(() => {
        onValidation && setEdit((e) => !e);
        setVal(value);
    }, [onValidation, value]);

    const onKeyDown = useCallback(
        (e: React.KeyboardEvent<HTMLInputElement>) => {
            switch (e.key) {
                case "Enter":
                    onCheckClick();
                    break;
                case "Escape":
                    onEditClick();
                    break;
            }
        },
        [onCheckClick, onEditClick]
    );

    const onDeleteCheckClick = useCallback(() => {
        onDeletion && onDeletion(rowIndex);
        setDeletion((d) => !d);
    }, [onDeletion, rowIndex]);

    const onDeleteClick = useCallback(() => onDeletion && setDeletion((d) => !d), [onDeletion]);
    const onDeleteKeyDown = useCallback(
        (e: React.KeyboardEvent<HTMLInputElement>) => {
            switch (e.key) {
                case "Enter":
                    onDeleteCheckClick();
                    break;
                case "Escape":
                    onDeleteClick();
                    break;
            }
        },
        [onDeleteCheckClick, onDeleteClick]
    );

    return (
        <TableCell {...getCellProps(colDesc, tableCellProps)} className={className}>
            {edit ? (
                <Input
                    value={val}
                    onChange={onChange}
                    onKeyDown={onKeyDown}
                    inputRef={setInputFocus}
                    margin="dense"
                    sx={tableFontSx}
                    endAdornment={
                        <>
                            <IconButton onClick={onCheckClick} size="small" sx={iconInRowSx}>
                                <CheckIcon fontSize="inherit" />
                            </IconButton>
                            <IconButton onClick={onEditClick} size="small" sx={iconInRowSx}>
                                <ClearIcon fontSize="inherit" />
                            </IconButton>
                        </>
                    }
                />
            ) : EDIT_COL === colDesc.dfid ? (
                deletion ? (
                    <Input
                        value="Confirm"
                        onKeyDown={onDeleteKeyDown}
                        inputRef={setInputFocus}
                        sx={tableFontSx}
                        endAdornment={
                            <>
                                <IconButton onClick={onDeleteCheckClick} size="small" sx={iconInRowSx}>
                                    <CheckIcon fontSize="inherit" />
                                </IconButton>
                                <IconButton onClick={onDeleteClick} size="small" sx={iconInRowSx}>
                                    <ClearIcon fontSize="inherit" />
                                </IconButton>
                            </>
                        }
                    />
                ) : onDeletion ? (
                    <IconButton onClick={onDeleteClick} size="small" sx={iconInRowSx}>
                        <DeleteIcon fontSize="inherit" />
                    </IconButton>
                ) : null
            ) : (
                <Box sx={cellBoxSx}>
                    {renderCellValue(value, colDesc, formatConfig, nanValue)}
                    {onValidation && !colDesc.notEditable ? (
                        <IconButton onClick={onEditClick} size="small" sx={iconInRowSx}>
                            <EditIcon fontSize="inherit" />
                        </IconButton>
                    ) : null}
                </Box>
            )}
        </TableCell>
    );
};
