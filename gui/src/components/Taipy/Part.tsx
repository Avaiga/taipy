import React, { ReactNode } from "react";
import Box from "@mui/material/Box";

import { useDynamicProperty } from "../../utils/hooks";

interface PartProps {
    id?: string;
    className?: string;
    render?: boolean;
    defaultRender?: boolean;
    children?: ReactNode;
}

const Part = (props: PartProps) => {
    const {id, className, children} = props;
    const render = useDynamicProperty(props.render, props.defaultRender, true);
    return render ? (
        <Box id={id} className={className}>
            {children}
        </Box>
    ) : null;
};

export default Part;
