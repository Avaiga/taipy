import React from "react";
import Avatar from "@mui/material/Avatar";

export interface TaipyImage {
    path: string;
    text: string;
}

export type stringImage = string | TaipyImage;

interface TaipyImageProps {
    id?: string;
    img: TaipyImage
    className?: string;
}

export const TaipyImageComp = ({id, img, className}:TaipyImageProps) => <Avatar alt={img.text || id} src={img.path} className={className} />