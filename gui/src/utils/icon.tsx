import React from "react";
import Avatar from "@mui/material/Avatar";

export interface Icon {
    path: string;
    text: string;
}

export type stringIcon = string | Icon;

interface IconProps {
    id?: string;
    img: Icon
    className?: string;
}

export const IconAvatar = ({id, img, className}:IconProps) => <Avatar alt={img.text || id} src={img.path} className={className} />