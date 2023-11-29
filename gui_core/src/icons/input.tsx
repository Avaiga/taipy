import React from "react";
import { SvgIcon, SvgIconProps } from "@mui/material";

export const Input = (props: SvgIconProps) => (
    <SvgIcon {...props} viewBox="0 0 16 16">
        <g stroke="currentColor">
            <path d="m8.8 8.02h-5.6" fill="none" />
            <circle cx="11.71" cy="8" r="1.09" fill="currentColor" />
            <path d="m7.12 5.85 2.15 2.15-2.15 2.15" fill="none" />
        </g>
    </SvgIcon>
);
