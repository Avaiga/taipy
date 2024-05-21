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

import React, { useEffect, useMemo, useRef } from "react";
import axios from "axios";
import Avatar from "@mui/material/Avatar";
import { SxProps, useTheme, Theme } from "@mui/material/styles";

/**
 * An Icon representation.
 */
export interface Icon {
    /** The URL to the image. */
    path: string;
    /** The text. */
    text: string;
    /** light theme path */
    lightPath?: string;
    /** dark theme path */
    darkPath?: string;
}

/**
 * A string or an icon.
 */
export type stringIcon = string | Icon;

interface IconProps {
    id?: string;
    img: Icon;
    className?: string;
    sx?: SxProps<Theme>;
}

export const avatarSx = { bgcolor: (theme: Theme) => theme.palette.text.primary };

export const IconAvatar = ({ id, img, className, sx }: IconProps) => {
    const avtRef = useRef<HTMLDivElement>(null);
    const theme = useTheme();
    const path = useMemo(
        () => (theme.palette.mode === "dark" ? img.darkPath : img.lightPath) || img.path || "",
        [img.path, img.lightPath, img.darkPath, theme.palette.mode]
    );
    const [svg, svgContent, inlineSvg] = useMemo(() => {
        const p = path.trim();
        if (p.length > 3) {
            const svgFile = p.substring(p.length - 4).toLowerCase() === ".svg";
            const svgXml = p.substring(0, 4).toLowerCase() === "<svg";
            return [
                svgFile && path,
                svgXml && path,
                svgFile || svgXml
            ];
        }
        return [undefined, undefined, false];
    }, [path]);
    const avtSx = useMemo(() => (sx ? { ...avatarSx, ...sx } : avatarSx), [sx]);

    useEffect(() => {
        if (svg) {
            axios.get<string>(svg).then((response) => avtRef.current && (avtRef.current.innerHTML = response.data));
        } else if (svgContent && avtRef.current) {
            avtRef.current.innerHTML = svgContent;
        }
    }, [svg, svgContent]);

    return inlineSvg ? (
        <Avatar alt={img.text || id} className={className} ref={avtRef} sx={avtSx} />
    ) : (
        <Avatar alt={img.text || id} src={path} className={className} sx={avtSx} />
    );
};
