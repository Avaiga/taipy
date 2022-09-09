/*
 * Copyright 2022 Avaiga Private Limited
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

import React, { useCallback, useContext, useEffect, useMemo, useState } from "react";
import { styled, SxProps, Theme } from "@mui/material/styles";
import ButtonBase from "@mui/material/ButtonBase";
import Typography from "@mui/material/Typography";
import Tooltip from "@mui/material/Tooltip";

import { TaipyContext } from "../../context/taipyContext";
import { createSendActionNameAction } from "../../context/taipyReducers";
import { useDynamicProperty } from "../../utils/hooks";
import { TaipyActiveProps } from "./utils";

interface ImageProps extends TaipyActiveProps {
    onAction?: string;
    label?: string;
    defaultLabel?: string;
    width?: string | number;
    height?: string | number;
    content?: string;
    defaultContent: string;
}

const ImageButton = styled(ButtonBase)(({ theme }) => ({
    position: "relative",
    height: 200,
    [theme.breakpoints.down("sm")]: {
        width: "100% !important", // Overrides inline-style
        height: 100,
    },
    "&:hover, &.Mui-focusVisible": {
        zIndex: 1,
        "& .MuiImageBackdrop-root": {
            opacity: 0.15,
        },
        "& .MuiImageMarked-root": {
            opacity: 0,
        },
        "& .MuiTypography-root": {
            border: "4px solid currentColor",
        },
    },
}));

const ImageSrc = styled("span")({
    position: "absolute",
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    backgroundSize: "cover",
    backgroundPosition: "center 40%",
});

const ImageSpan = styled("span")(({ theme }) => ({
    position: "absolute",
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: theme.palette.common.white,
}));

const ImageBackdrop = styled("span")(({ theme }) => ({
    position: "absolute",
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    backgroundColor: theme.palette.common.black,
    opacity: 0.4,
    transition: theme.transitions.create("opacity"),
}));

const ImageMarked = styled("span")(({ theme }) => ({
    height: 3,
    width: 18,
    backgroundColor: theme.palette.common.white,
    position: "absolute",
    bottom: -2,
    left: "calc(50% - 9px)",
    transition: theme.transitions.create("opacity"),
}));

const Image = (props: ImageProps) => {
    const { className, id, onAction, width = 300, height } = props;
    const [label, setLabel] = useState(props.defaultLabel);
    const [content, setContent] = useState(props.defaultContent);
    const { dispatch } = useContext(TaipyContext);

    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    const handleClick = useCallback(() => {
        if (onAction) {
            dispatch(createSendActionNameAction(id, onAction));
        }
    }, [id, onAction, dispatch]);

    useEffect(() => {
        setLabel((val) => {
            if (props.label !== undefined && val !== props.label) {
                return props.label;
            }
            return val;
        });
    }, [props.label]);

    useEffect(() => {
        setContent((val) => {
            if (props.content !== undefined && val !== props.content) {
                return props.content;
            }
            return val;
        });
    }, [props.content]);

    const style = useMemo(() => ({ width: width, height: height }), [width, height]);

    const imgStyle = useMemo(() => ({ backgroundImage: `url("${content}")` }), [content]);

    const imgSx = useMemo(
        () =>
            ({
                position: "relative",
                p: 4,
                pt: 2,
                pb: (theme: Theme) => `calc(${theme.spacing(1)} + 6px)`,
            } as SxProps<Theme>),
        []
    );

    return (
        <Tooltip title={hover || ""}>
            <ImageButton
                focusRipple
                style={style}
                onClick={handleClick}
                disabled={!active}
                className={className}
                id={id}
            >
                <ImageSrc style={imgStyle} />
                <ImageBackdrop className="MuiImageBackdrop-root" />
                {label === undefined ? null : (
                    <ImageSpan>
                        <Typography component="span" variant="subtitle1" color="inherit" sx={imgSx}>
                            {label}
                            <ImageMarked className="MuiImageMarked-root" />
                        </Typography>
                    </ImageSpan>
                )}
            </ImageButton>
        </Tooltip>
    );
};

export default Image;
