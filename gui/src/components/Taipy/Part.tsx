import React, { ReactNode } from "react";
import Box from "@mui/material/Box";

import { useDynamicProperty } from "../../utils/hooks";
import TaipyRendered from "../pages/TaipyRendered";

interface PartProps {
    id?: string;
    className?: string;
    render?: boolean;
    defaultRender?: boolean;
    page?: string;
    children?: ReactNode;
    partial?: boolean;
}

const Part = (props: PartProps) => {
    const {id, className, children, page, partial} = props;
    const render = useDynamicProperty(props.render, props.defaultRender, true);
    return render ? (
        <Box id={id} className={className}>
            {page ? <TaipyRendered path={"/" + page} partial={partial} /> : null}
            {children}
        </Box>
    ) : null;
};

export default Part;
