import React from "react";
import AutoLoadingTable from "./AutoLoadingTable";
import PaginatedTable from "./PaginatedTable";
import { TaipyPaginatedTableProps } from "./TableUtils";

interface TableProps extends TaipyPaginatedTableProps {
    autoLoading: boolean;
}

const Table = ({ autoLoading = false, ...rest }: TableProps) =>
    autoLoading ? <AutoLoadingTable {...rest} /> : <PaginatedTable {...rest} />;

export default Table;
