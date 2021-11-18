import React, { ReactNode, useMemo } from "react";
import Box from "@mui/material/Box";

interface LayoutProps {
    id?: string;
    type?: string;
    children?: ReactNode;
    className?: string;
    gap?: string;
}

const baseSx = { display: "grid" };

const SPLIT_COLS = /\D+/

const Layout = (props: LayoutProps) => {
    const { type = "1 1", gap = "0.5rem" } = props;
    const sx = useMemo(() => {
        const vals = type.split(SPLIT_COLS).filter(t => t).map((t) => {
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
    }, [type, gap]);
    return (
        <Box id={props.id} className={props.className} sx={sx}>
            {props.children}
        </Box>
    );
};

export default Layout;
