import { TableCellProps } from "@mui/material/TableCell";

import { getDateTimeString } from "../../utils/index";
import { TaipyBaseProps } from "./utils";

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

export const formatValue = (val: any, col: any) => {
    switch (col.type) {
        case "datetime64[ns]":
            return getDateTimeString(val, col.format || defaultDateFormat);
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

export interface TaipyTableProps extends TaipyBaseProps {
    /* eslint "@typescript-eslint/no-explicit-any": "off", curly: "error" */
    value: Record<string, Record<string, any>>;
    columns: string;
}

export interface TaipyPaginatedTableProps extends TaipyTableProps {
    pageSize?: number;
    pageSizeOptions: (
        | number
        | {
              value: number;
              label: string;
          }
    )[];
    allowAllRows: boolean;
    showAll: boolean;
}



export const boxSx = { width: "100%" };
export const paperSx = { width: "100%", mb: 2 };
export const tableSx = { minWidth: 750 };
export const tcSx = { maxHeight: "80vh" };

