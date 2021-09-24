import React, { ReactNode, useContext } from "react";
import { Link as RouterLink } from "react-router-dom";
import MuiLink from "@mui/material/Link";
import { TaipyContext } from "../../context/taipyContext";

interface LinkProps {
    href: string;
    children?: ReactNode;
}

const Link = (props: LinkProps) => {
    const {state} = useContext(TaipyContext);
    if (Object.keys(state.locations).some(route => props.href === route)) {
        return <MuiLink to={props.href} component={RouterLink}>{props.children}</MuiLink>
    }
    return <MuiLink {...props} />
}

export default Link