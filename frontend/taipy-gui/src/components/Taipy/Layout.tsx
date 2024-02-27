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

import React, { ReactNode, useMemo } from "react";
import Box from "@mui/material/Box";

import { useClassNames, useIsMobile } from "../../utils/hooks";
import { TaipyBaseProps } from "./utils";

interface LayoutProps extends TaipyBaseProps {
    columns?: string;
    columns_Mobile_?: string;
    children?: ReactNode;
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

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const isMobile = useIsMobile();
    const sx = useMemo(() => {
        return {
            display: "grid",
            gap: gap,
            gridTemplateColumns: expandCols(isMobile ? columns_Mobile_ : columns),
        };
    }, [columns, columns_Mobile_, gap, isMobile]);

    return (
        <Box id={props.id} className={className} sx={sx}>
            {props.children}
        </Box>
    );
};

export default Layout;
