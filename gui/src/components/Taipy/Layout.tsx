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

const baseSx = { display: "grid" };

const SPLIT_COLS = /\D+/

const Layout = (props: LayoutProps) => {
    const { columns = "1 1", gap = "0.5rem", columns_Mobile_ = "1" } = props;
    const isMobile = useIsMobile();
    const sx = useMemo(() => {
        const cols = isMobile ? columns_Mobile_ : columns;
        const vals = cols.split(SPLIT_COLS).filter(t => t).map((t) => {
            try {
                return parseFloat(t);
            } catch (e) {
                return 1;
            }
        });
        const total = vals.reduce((pv, cv) => pv + cv, 0);
        return {
            ...baseSx,
            gap: gap,
            gridTemplateColumns: vals
                .map((val, idx) => {
                    const base = (100 * val) / total + "%";
                    return idx == 0 ? base : "calc(" + base + " - " + gap + ")";
                })
                .join(" "),
        };
    }, [columns, columns_Mobile_, gap, isMobile]);

    return (
        <Box id={props.id} className={props.className} sx={sx}>
            {props.children}
        </Box>
    );
};

export default Layout;
