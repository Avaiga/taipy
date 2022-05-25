import React, { ReactNode, useMemo } from "react";
import Box from "@mui/material/Box";

import { useIsMobile } from "../../utils/hooks";

interface LayoutProps {
    id?: string;
    columns?: string;
    columns_Mobile_?: string;
    children?: ReactNode;
    className?: string;
    gap?: string;
}

const EXPR_COLS = /(\d+)\s*\*\s*(\d+)([^\s]*)/;
const NON_UNIT_COLS = /(\d+)\s+/g;

const expandCols = (cols: string) => {
    let m = cols.match(EXPR_COLS);
    while (m && m.length > 3) {
        const n1 = parseInt(m[1], 10);
        cols = cols.replace(m[0],  Array.from(Array(n1), () => m && (m[2] + m[3])).join(" "));
        m = cols.match(EXPR_COLS);
    }
    return (cols + " ").replaceAll(NON_UNIT_COLS, (v, g) => g + "fr ").trim();
}

const Layout = (props: LayoutProps) => {
    const { columns = "1 1", gap = "0.5rem", columns_Mobile_ = "1" } = props;
    const isMobile = useIsMobile();
    const sx = useMemo(() => {
        return {
            display: "grid",
            gap: gap,
            gridTemplateColumns: expandCols(isMobile ? columns_Mobile_ : columns),
        };
    }, [columns, columns_Mobile_, gap, isMobile]);

    return (
        <Box id={props.id} className={props.className} sx={sx}>
            {props.children}
        </Box>
    );
};

export default Layout;
