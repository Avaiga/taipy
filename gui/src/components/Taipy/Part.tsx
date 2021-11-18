import React, { ReactNode } from "react";
import Box from "@mui/material/Box";

interface PartProps {
    id?: string;
    className?: string;
    children?: ReactNode;
}

const Part = (props: PartProps) => {
    return (
        <Box id={props.id} className={props.className}>
            {props.children}
        </Box>
    );
};

export default Part;
