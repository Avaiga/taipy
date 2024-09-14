/*
 * Copyright 2021-2024 Avaiga Private Limited
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

import React, {
    useState,
    useCallback,
    useEffect,
    useMemo,
    CSSProperties,
    MouseEvent,
    ChangeEvent,
    SyntheticEvent,
} from "react";
import { FilterOptionsState } from "@mui/material";
import Autocomplete, { createFilterOptions } from "@mui/material/Autocomplete";
import Badge from "@mui/material/Badge";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import Input from "@mui/material/Input";
import Switch from "@mui/material/Switch";
import TableCell, { TableCellProps } from "@mui/material/TableCell";
import TextField from "@mui/material/TextField";
import CheckIcon from "@mui/icons-material/Check";
import ClearIcon from "@mui/icons-material/Clear";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { DateTimePicker } from "@mui/x-date-pickers/DateTimePicker";
import { BaseDateTimePickerSlotProps } from "@mui/x-date-pickers/DateTimePicker/shared";
import { isValid } from "date-fns";

import { FormatConfig } from "../../context/taipyReducers";
import { dateToString, getDateTime, getDateTimeString, getNumberString, getTimeZonedDate } from "../../utils/index";
import { TaipyActiveProps, TaipyMultiSelectProps, getSuffixedClassNames } from "./utils";

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
    /** The name of the column that holds the tooltip to
     *  show on the cells. */
    tooltip?: string;
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
    /** The list of values that can be used on edit. */
    lov?: string[];
    /** If true the user can enter any value besides the lov values. */
    freeLov?: boolean;
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

export const defaultDateFormat = "yyyy/MM/dd";

const imgButtonRe = /^(!)?\[([^\]]*)]\(([^)]*)\)$/;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type TableValueType = Record<string, Record<string, any>>;

export interface TaipyTableProps extends TaipyActiveProps, TaipyMultiSelectProps {
    data?: TableValueType;
    columns?: string;
    defaultColumns: string;
    height?: string;
    width?: string;
    pageSize?: number;
    onEdit?: string;
    onDelete?: string;
    onAdd?: string;
    onAction?: string;
    editable?: boolean;
    defaultEditable?: boolean;
    lineStyle?: string;
    tooltip?: string;
    cellTooltip?: string;
    nanValue?: string;
    filter?: boolean;
    size?: "small" | "medium";
    defaultKey?: string; // for testing purposes only
    userData?: unknown;
    downloadable?: boolean;
    onCompare?: string;
    compare?: boolean;
}

export const DownloadAction = "__Taipy__download_csv";

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
export const iconInRowSx = { fontSize: "body2.fontSize" };
export const iconsWrapperSx = { gridColumnStart: 2, display: "flex", alignItems: "center" } as CSSProperties;
const cellBoxSx = { display: "grid", gridTemplateColumns: "1fr auto", alignItems: "center" } as CSSProperties;
const tableFontSx = { fontSize: "body2.fontSize" };
const ButtonSx = { minHeight: "unset", mb: "unset", padding: "unset", lineHeight: "unset" };
export interface OnCellValidation {
    (value: RowValue, rowIndex: number, colName: string, userValue: string, tz?: string): void;
}

export interface OnRowDeletion {
    (rowIndex: number): void;
}

export interface OnRowSelection {
    (rowIndex: number, colName?: string, value?: string): void;
}

export interface OnRowClick {
    (e: MouseEvent<HTMLTableRowElement>): void;
}

interface EditableCellProps {
    rowIndex: number;
    value: RowValue;
    colDesc: ColumnDesc;
    formatConfig: FormatConfig;
    onValidation?: OnCellValidation;
    onDeletion?: OnRowDeletion;
    onSelection?: OnRowSelection;
    nanValue?: string;
    className?: string;
    tableClassName?: string;
    tooltip?: string;
    tableCellProps?: Partial<TableCellProps>;
    comp?: RowValue;
}

export const defaultColumns = {} as Record<string, ColumnDesc>;

export const getsortByIndex = (cols: Record<string, ColumnDesc>) => (key1: string, key2: string) =>
    cols[key1].index < cols[key2].index ? -1 : cols[key1].index > cols[key2].index ? 1 : 0;

const formatValue = (val: RowValue, col: ColumnDesc, formatConf: FormatConfig, nanValue?: string): string => {
    if (val === undefined) {
        return "";
    }
    switch (col.type) {
        case "datetime":
            if (val === "NaT") {
                return nanValue || "";
            }
            return val ? getDateTimeString(val as string, col.format || defaultDateFormat, formatConf, col.tz) : "";
        case "int":
        case "float":
            if (val === null) {
                return nanValue || "";
            }
            return getNumberString(val as number, col.format, formatConf);
        default:
            return val ? (val as string) : "";
    }
};

const VALID_BOOLEAN_STRINGS = ["true", "1", "t", "y", "yes", "yeah", "sure"];

const isBooleanTrue = (val: RowValue) =>
    typeof val == "string" ? VALID_BOOLEAN_STRINGS.some((s) => s == val.trim().toLowerCase()) : !!val;

const defaultCursor = { cursor: "default" };
const defaultCursorIcon = { ...iconInRowSx, "& .MuiSwitch-input": defaultCursor };

const getCellProps = (col: ColumnDesc, base: Partial<TableCellProps> = {}): Partial<TableCellProps> => {
    switch (col.type) {
        case "bool":
            base.align = "center";
            break;
    }
    if (col.width) {
        base.width = col.width;
    }
    return base;
};

export const getRowIndex = (row: Record<string, RowValue>, rowIndex: number, startIndex = 0) =>
    typeof row["_tp_index"] === "number" ? row["_tp_index"] : rowIndex + startIndex;

export const addDeleteColumn = (nbToRender: number, columns: Record<string, ColumnDesc>) => {
    if (nbToRender) {
        Object.keys(columns).forEach((key) => columns[key].index++);
        columns[EDIT_COL] = {
            dfid: EDIT_COL,
            type: "",
            format: "",
            title: "",
            index: 0,
            width: nbToRender * 4 + "em",
            filter: false,
        };
    }
    return columns;
};

export const getClassName = (row: Record<string, unknown>, style?: string, col?: string) =>
    style ? (((col && row[`tps__${col}__${style}`]) || row[style]) as string) : undefined;

export const getTooltip = (row: Record<string, unknown>, tooltip?: string, col?: string) =>
    tooltip ? (((col && row[`tpt__${col}__${tooltip}`]) || row[tooltip]) as string) : undefined;

const setInputFocus = (input: HTMLInputElement) => input && input.focus();

const textFieldProps = { textField: { margin: "dense" } } as BaseDateTimePickerSlotProps<Date>;

const filter = createFilterOptions<string>();
const getOptionKey = (option: string) => (Array.isArray(option) ? option[0] : option);
const getOptionLabel = (option: string) => (Array.isArray(option) ? option[1] : option);

const onCompleteClose = (evt: SyntheticEvent) => evt.stopPropagation();

const emptyObject = {};

export const EditableCell = (props: EditableCellProps) => {
    const {
        onValidation,
        value,
        colDesc,
        formatConfig,
        rowIndex,
        onDeletion,
        onSelection,
        nanValue,
        className,
        tableClassName,
        tooltip,
        tableCellProps = emptyObject,
        comp,
    } = props;
    const [val, setVal] = useState<RowValue | Date>(value);
    const [edit, setEdit] = useState(false);
    const [deletion, setDeletion] = useState(false);

    const onChange = useCallback((e: ChangeEvent<HTMLInputElement>) => setVal(e.target.value), []);
    const onCompleteChange = useCallback((e: SyntheticEvent, value: string | null) => {
        e.stopPropagation();
        setVal(value);
    }, []);
    const onBoolChange = useCallback((e: ChangeEvent<HTMLInputElement>) => setVal(e.target.checked), []);
    const onDateChange = useCallback((date: Date | null) => setVal(date), []);

    const withTime = useMemo(() => !!colDesc.format && colDesc.format.toLowerCase().includes("h"), [colDesc.format]);

    const buttonImg = useMemo(() => {
        let m;
        if (typeof value == "string" && (m = imgButtonRe.exec(value)) !== null) {
            return {
                text: !!m[1] ? m[3]: m[2],
                value: !!m[1] ? m[2]: m[3],
                img: !!m[1],
                action: !!onSelection,
            };
        }
        return undefined;
    }, [value, onSelection]);

    const onCheckClick = useCallback(
        (evt?: MouseEvent<HTMLElement>) => {
            evt && evt.stopPropagation();
            let castVal = val;
            switch (colDesc.type) {
                case "bool":
                    castVal = isBooleanTrue(val as RowValue);
                    break;
                case "int":
                    try {
                        castVal = parseInt(val as string, 10);
                    } catch {
                        // ignore
                    }
                    break;
                case "float":
                    try {
                        castVal = parseFloat(val as string);
                    } catch {
                        // ignore
                    }
                    break;
                case "datetime":
                    if (val === null) {
                        castVal = val;
                    } else if (isValid(val)) {
                        castVal = dateToString(
                            getTimeZonedDate(val as Date, formatConfig.timeZone, withTime),
                            withTime
                        );
                    } else {
                        return;
                    }
                    break;
            }
            onValidation &&
                onValidation(
                    castVal as RowValue,
                    rowIndex,
                    colDesc.dfid,
                    val as string,
                    colDesc.type == "datetime" ? formatConfig.timeZone : undefined
                );
            setEdit((e) => !e);
        },
        [onValidation, val, rowIndex, colDesc.dfid, colDesc.type, formatConfig.timeZone, withTime]
    );

    const onEditClick = useCallback(
        (evt?: MouseEvent<HTMLElement>) => {
            evt && evt.stopPropagation();
            colDesc.type?.startsWith("date")
                ? setVal(getDateTime(value as string, formatConfig.timeZone, withTime))
                : setVal(value);
            onValidation && setEdit((e) => !e);
        },
        [onValidation, value, formatConfig.timeZone, colDesc.type, withTime]
    );

    const onKeyDown = useCallback(
        (e: React.KeyboardEvent<HTMLElement>) => {
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

    const onDeleteCheckClick = useCallback(
        (evt?: MouseEvent<HTMLElement>) => {
            evt && evt.stopPropagation();
            onDeletion && onDeletion(rowIndex);
            setDeletion((d) => !d);
        },
        [onDeletion, rowIndex]
    );

    const onDeleteClick = useCallback(
        (evt?: MouseEvent) => {
            evt && evt.stopPropagation();
            onDeletion && setDeletion((d) => !d);
        },
        [onDeletion]
    );

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

    const onSelect = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            onSelection && onSelection(rowIndex, colDesc.dfid, buttonImg && buttonImg.value);
        },
        [onSelection, rowIndex, colDesc.dfid, buttonImg]
    );

    const filterOptions = useCallback(
        (options: string[], params: FilterOptionsState<string>) => {
            const filtered = filter(options, params);
            if (colDesc.freeLov) {
                const { inputValue } = params;
                if (
                    inputValue &&
                    !options.some((option) => inputValue == (Array.isArray(option) ? option[1] : option))
                ) {
                    filtered.push(inputValue);
                }
            }
            return filtered;
        },
        [colDesc.freeLov]
    );

    useEffect(() => {
        !onValidation && setEdit(false);
    }, [onValidation]);

    return (
        <TableCell
            {...getCellProps(colDesc, tableCellProps)}
            className={
                onValidation ? getSuffixedClassNames(className || "tpc", edit ? "-editing" : "-editable") : className
            }
            title={
                tooltip || comp
                    ? `${tooltip ? tooltip : ""}${
                          comp ? " " + formatValue(comp as RowValue, colDesc, formatConfig, nanValue) : ""
                      }`
                    : undefined
            }
        >
            <Badge color="primary" variant="dot" invisible={comp === undefined || comp === null}>
                {edit ? (
                    colDesc.type?.startsWith("bool") ? (
                        <Box sx={cellBoxSx}>
                            <Switch
                                checked={val as boolean}
                                size="small"
                                title={val ? "True" : "False"}
                                sx={iconInRowSx}
                                onChange={onBoolChange}
                                inputRef={setInputFocus}
                            />
                            <Box sx={iconsWrapperSx}>
                                <IconButton onClick={onCheckClick} size="small" sx={iconInRowSx}>
                                    <CheckIcon fontSize="inherit" />
                                </IconButton>
                                <IconButton onClick={onEditClick} size="small" sx={iconInRowSx}>
                                    <ClearIcon fontSize="inherit" />
                                </IconButton>
                            </Box>
                        </Box>
                    ) : colDesc.type?.startsWith("date") ? (
                        <Box sx={cellBoxSx}>
                            {withTime ? (
                                <DateTimePicker
                                    value={val as Date}
                                    onChange={onDateChange}
                                    slotProps={textFieldProps}
                                    inputRef={setInputFocus}
                                    sx={tableFontSx}
                                />
                            ) : (
                                <DatePicker
                                    value={val as Date}
                                    onChange={onDateChange}
                                    slotProps={textFieldProps}
                                    inputRef={setInputFocus}
                                    sx={tableFontSx}
                                />
                            )}
                            <Box sx={iconsWrapperSx}>
                                <IconButton onClick={onCheckClick} size="small" sx={iconInRowSx}>
                                    <CheckIcon fontSize="inherit" />
                                </IconButton>
                                <IconButton onClick={onEditClick} size="small" sx={iconInRowSx}>
                                    <ClearIcon fontSize="inherit" />
                                </IconButton>
                            </Box>
                        </Box>
                    ) : colDesc.lov ? (
                        <Box sx={cellBoxSx}>
                            <Autocomplete
                                autoComplete={true}
                                fullWidth
                                selectOnFocus={!!colDesc.freeLov}
                                clearOnBlur={!!colDesc.freeLov}
                                handleHomeEndKeys={!!colDesc.freeLov}
                                options={colDesc.lov}
                                getOptionKey={getOptionKey}
                                getOptionLabel={getOptionLabel}
                                filterOptions={filterOptions}
                                freeSolo={!!colDesc.freeLov}
                                value={val as string}
                                onChange={onCompleteChange}
                                onOpen={onCompleteClose}
                                renderInput={(params) => (
                                    <TextField
                                        {...params}
                                        fullWidth
                                        inputRef={setInputFocus}
                                        onChange={colDesc.freeLov ? onChange : undefined}
                                        margin="dense"
                                        variant="standard"
                                        sx={tableFontSx}
                                    />
                                )}
                                disableClearable={!colDesc.freeLov}
                            />
                            <Box sx={iconsWrapperSx}>
                                <IconButton onClick={onCheckClick} size="small" sx={iconInRowSx}>
                                    <CheckIcon fontSize="inherit" />
                                </IconButton>
                                <IconButton onClick={onEditClick} size="small" sx={iconInRowSx}>
                                    <ClearIcon fontSize="inherit" />
                                </IconButton>
                            </Box>
                        </Box>
                    ) : (
                        <Input
                            value={val}
                            onChange={onChange}
                            onKeyDown={onKeyDown}
                            inputRef={setInputFocus}
                            margin="dense"
                            sx={tableFontSx}
                            endAdornment={
                                <Box sx={iconsWrapperSx}>
                                    <IconButton onClick={onCheckClick} size="small" sx={iconInRowSx}>
                                        <CheckIcon fontSize="inherit" />
                                    </IconButton>
                                    <IconButton onClick={onEditClick} size="small" sx={iconInRowSx}>
                                        <ClearIcon fontSize="inherit" />
                                    </IconButton>
                                </Box>
                            }
                        />
                    )
                ) : EDIT_COL === colDesc.dfid ? (
                    deletion ? (
                        <Input
                            value="Confirm"
                            onKeyDown={onDeleteKeyDown}
                            inputRef={setInputFocus}
                            sx={tableFontSx}
                            endAdornment={
                                <Box sx={iconsWrapperSx}>
                                    <IconButton onClick={onDeleteCheckClick} size="small" sx={iconInRowSx}>
                                        <CheckIcon fontSize="inherit" />
                                    </IconButton>
                                    <IconButton onClick={onDeleteClick} size="small" sx={iconInRowSx}>
                                        <ClearIcon fontSize="inherit" />
                                    </IconButton>
                                </Box>
                            }
                        />
                    ) : onDeletion ? (
                        <Box sx={iconsWrapperSx}>
                            <IconButton onClick={onDeleteClick} size="small" sx={iconInRowSx}>
                                <DeleteIcon fontSize="inherit" />
                            </IconButton>
                        </Box>
                    ) : null
                ) : (
                    <Box sx={cellBoxSx} onClick={onSelect}>
                        {buttonImg ? (
                            buttonImg.img ? (
                                <img
                                    src={buttonImg.text}
                                    className={getSuffixedClassNames(tableClassName, "-img")}
                                    alt={buttonImg.value}
                                    onClick={onSelect}
                                    title={buttonImg.value}
                                />
                            ) : (
                                <Button
                                    size="small"
                                    onClick={onSelect}
                                    sx={ButtonSx}
                                    className={getSuffixedClassNames(tableClassName, "-btn")}
                                    disabled={!buttonImg.action}
                                    title={buttonImg.value}
                                >
                                    {formatValue(buttonImg.text, colDesc, formatConfig, nanValue)}
                                </Button>
                            )
                        ) : value !== null && value !== undefined && colDesc.type && colDesc.type.startsWith("bool") ? (
                            <Switch
                                checked={value as boolean}
                                size="small"
                                title={value ? "True" : "False"}
                                sx={defaultCursorIcon}
                                className={getSuffixedClassNames(tableClassName, "-bool")}
                            />
                        ) : (
                            <span style={defaultCursor}>
                                {formatValue(value as RowValue, colDesc, formatConfig, nanValue)}
                            </span>
                        )}
                        {onValidation && !buttonImg ? (
                            <Box sx={iconsWrapperSx}>
                                <IconButton onClick={onEditClick} size="small" sx={iconInRowSx}>
                                    <EditIcon fontSize="inherit" />
                                </IconButton>
                            </Box>
                        ) : null}
                    </Box>
                )}
            </Badge>
        </TableCell>
    );
};
