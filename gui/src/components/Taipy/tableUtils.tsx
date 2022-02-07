import React, { useState, useCallback, CSSProperties } from "react";
import { TableCellProps } from "@mui/material/TableCell";
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

export interface ColumnDesc {
    dfid: string;
    type: string;
    format: string;
    title?: string;
    index: number;
    width?: number | string;
    notEditable?: boolean;
    style?: string;
    nanValue?: string;
}

export type Order = "asc" | "desc";

export type RowValue = string | number | null;

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
        case "datetime64[ns]":
            return getDateTimeString(val as string, col.format || defaultDateFormat, formatConf);
        case "int64":
        case "float64":
            if (val === "NaN") {
                return nanValue || "";
            }
            return getNumberString(val as number, col.format, formatConf);
        default:
            return val as string;
    }
};

const renderCellValue = (val: RowValue | boolean, col: ColumnDesc, formatConf: FormatConfig, nanValue?: string) => {
    if (val !== null && val !== undefined && col.type && col.type.startsWith("bool")) {
        return <Switch checked={val as boolean} title={"" + val} />;
    }
    return <>{formatValue(val as RowValue, col, formatConf, nanValue)}</>;
};

export const getCellProps = (col: ColumnDesc): Partial<TableCellProps> => {
    const ret: Partial<TableCellProps> = {};
    switch (col.type) {
        case "int64":
        case "float64":
            ret.align = "right";
    }
    if (col.width) {
        ret.width = col.width;
    }
    return ret;
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type TableValueType = Record<string, Record<string, any>>;

export interface TaipyTableProps extends TaipyActiveProps, TaipyMultiSelectProps {
    data?: TableValueType;
    columns: string;
    refresh?: boolean;
    height?: string;
    width?: string;
    pageSize?: number;
    editAction?: string;
    deleteAction?: string;
    addAction?: string;
    editable?: boolean;
    defaultEditable?: boolean;
    lineStyle?: string;
    nanValue?: string;
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
    (value: RowValue, rowIndex: number, colName: string): void;
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
}

export const addDeleteColumn = (render: boolean, columns: Record<string, ColumnDesc>) => {
    if (render) {
        Object.keys(columns).forEach((key) => columns[key].index++);
        columns[EDIT_COL] = { dfid: EDIT_COL, type: "", format: "", title: "", index: 0, width: "2em" };
    }
    return columns;
};

export const getClassName = (row: Record<string, unknown>, style?: string) =>
    style ? (row[style] as string) : undefined;

const setInputFocus = (input: HTMLInputElement) => input && input.focus();

const cellBoxSx = { display: "grid", gridTemplateColumns: "1fr auto", alignItems: "center" } as CSSProperties;
export const iconInRowSx = { height: "1em" } as CSSProperties;

export const EditableCell = (props: EditableCellProps) => {
    const { onValidation, value, colDesc, formatConfig, rowIndex, onDeletion, nanValue } = props;
    const [val, setVal] = useState(value);
    const [edit, setEdit] = useState(false);
    const [deletion, setDeletion] = useState(false);

    const onChange = useCallback((e) => setVal(e.target.value), []);
    const onCheckClick = useCallback(() => {
        onValidation && onValidation(val, rowIndex, colDesc.dfid);
        setEdit((e) => !e);
    }, [onValidation, val, rowIndex, colDesc.dfid]);

    const onEditClick = useCallback(() => {
        onValidation && setEdit((e) => !e);
        setVal(value);
    }, [onValidation, value]);

    const onKeyDown = useCallback(
        (e) => {
            switch (e.keyCode) {
                case 13:
                    onCheckClick();
                    break;
                case 27:
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
        (e) => {
            switch (e.keyCode) {
                case 13:
                    onDeleteCheckClick();
                    break;
                case 27:
                    onDeleteClick();
                    break;
            }
        },
        [onDeleteCheckClick, onDeleteClick]
    );

    return edit ? (
        <Input
            value={val}
            onChange={onChange}
            onKeyDown={onKeyDown}
            inputRef={setInputFocus}
            endAdornment={
                <>
                    <IconButton onClick={onCheckClick} size="small" sx={iconInRowSx}>
                        <CheckIcon />
                    </IconButton>
                    <IconButton onClick={onEditClick} size="small" sx={iconInRowSx}>
                        <ClearIcon />
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
                endAdornment={
                    <>
                        <IconButton onClick={onDeleteCheckClick} size="small" sx={iconInRowSx}>
                            <CheckIcon />
                        </IconButton>
                        <IconButton onClick={onDeleteClick} size="small" sx={iconInRowSx}>
                            <ClearIcon />
                        </IconButton>
                    </>
                }
            />
        ) : (
            <IconButton onClick={onDeleteClick} size="small" sx={iconInRowSx}>
                <DeleteIcon />
            </IconButton>
        )
    ) : onValidation ? (
        <Box sx={cellBoxSx}>
            {formatValue(value, colDesc, formatConfig)}
            {!colDesc.notEditable ? (
                <IconButton onClick={onEditClick} size="small" sx={iconInRowSx}>
                    <EditIcon />
                </IconButton>
            ) : null}
        </Box>
    ) : (
        renderCellValue(value, colDesc, formatConfig, nanValue)
    );
};
