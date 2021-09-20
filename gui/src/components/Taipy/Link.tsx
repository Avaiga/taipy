import React, { ReactNode } from "react";
import { Link as RouterLink } from "react-router-dom";
import MuiLink from "@mui/material/Link";

interface LinkProps {
    to: string;
    children?: ReactNode;
}

const Link = (props: LinkProps) => <MuiLink to={props.to} component={RouterLink}>{props.children}</MuiLink>

export default Link