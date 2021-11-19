import React, { ReactNode, useContext, useMemo } from "react";
import { Link as RouterLink, useMatch, useResolvedPath } from "react-router-dom";
import MuiLink from "@mui/material/Link";
import { TaipyContext } from "../../context/taipyContext";

interface LinkProps {
    href: string;
    children?: ReactNode;
    noStyle?: boolean;
}

const Link = (props: LinkProps) => {
    const { state } = useContext(TaipyContext);
    const resolved = useResolvedPath(props.href);
    const match = useMatch({ path: resolved.pathname, end: true });

    const linkStyle = useMemo(
        () =>
            !props.noStyle && match
                ? { textDecoration: "underline", backgroundColor: "rgba(144, 202, 249, 0.16)" }
                : {},
        [props.noStyle, match]
    );

    if (Object.keys(state.locations).some((route) => props.href === route)) {
        return (
            <MuiLink to={props.href} component={RouterLink} sx={linkStyle}>
                {props.children}
            </MuiLink>
        );
    }
    return <MuiLink {...props} />;
};

export default Link;
