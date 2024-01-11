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
