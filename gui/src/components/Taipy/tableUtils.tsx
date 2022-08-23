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
    tz?: string;
    filter?: boolean;
    apply?: string;
    groupBy?: boolean;
    widthHint?: number;
}

export const DEFAULT_SIZE = "small";

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
    tp_onEdit?: string;
    tp_onDelete?: string;
    tp_onAdd?: string;
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
        onValidation && onValidation(val, rowIndex, colDesc.dfid);
        setEdit((e) => !e);
    }, [onValidation, val, rowIndex, colDesc.dfid]);

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
                    <IconButton onClick={onDeleteClick} size="small">
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
