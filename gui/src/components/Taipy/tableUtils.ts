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

export type RowValue = string | number | null;

export type RowType = Record<string, RowValue>;

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

export const formatValue = (val: RowValue, col: ColumnDesc, formatConf: FormatConfig): string => {
    if (val === null || val === undefined) {
        return "";
    }
    switch (col.type) {
        case "datetime64[ns]":
            return getDateTimeString(val as string, col.format || defaultDateFormat, formatConf);
        case "int64":
        case "float64":
            return getNumberString(val as number, col.format, formatConf);
        default:
            return val as string;
    }
};

export const alignCell = (col: ColumnDesc): Partial<TableCellProps> => {
    switch (col.type) {
        case "int64":
        case "float64":
            return { align: "right" };
        default:
            return {};
    }
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
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
export const tableSx = { minWidth: 250 };
