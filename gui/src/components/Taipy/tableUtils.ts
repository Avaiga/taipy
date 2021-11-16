import { TableCellProps } from "@mui/material/TableCell";
import { FormatConfig } from "../../context/taipyReducers";

import { getDateTimeString, getNumberString } from "../../utils/index";
import { TaipyBaseProps, TaipyMultiSelectProps } from "./utils";

export interface ColumnDesc {
    dfid: string;
    type: string;
    format: string;
    title?: string;
    index: number;
    width?: number;
}

export type Order = "asc" | "desc";

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

export const formatValue = (val: any, col: any, formatConf: FormatConfig) => {
    if (val === null || val === undefined) {
        return "";
    }
    switch (col.type) {
        case "datetime64[ns]":
            return getDateTimeString(val, col.format || defaultDateFormat, formatConf);
        case "int64":
        case "float64":
            return getNumberString(val, col.format, formatConf);
        default:
            return val;
    }
};

export const alignCell = (col: any): Partial<TableCellProps> => {
    switch (col.type) {
        case "int64":
        case "float64":
            return { align: "right" };
        default:
            return {};
    }
};

/* eslint "@typescript-eslint/no-explicit-any": "off", curly: "error" */
export type TableValueType = Record<string, Record<string, any>>;

export interface TaipyTableProps extends TaipyBaseProps, TaipyMultiSelectProps {
    value?: TableValueType;
    columns: string;
    refresh?: boolean;
    height?: string;
    pageSize?: number;
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

export const boxSx = { width: "100%" };
export const paperSx = { width: "100%", mb: 2 };
export const tableSx = { minWidth: 750 };
