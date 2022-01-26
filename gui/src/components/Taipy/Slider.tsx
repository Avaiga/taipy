import React, { useState, useEffect, useCallback, useContext, useMemo } from "react";
import { SxProps } from "@mui/material";
import MuiSlider from "@mui/material/Slider";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";

import { TaipyContext } from "../../context/taipyContext";
import { createSendUpdateAction } from "../../context/taipyReducers";
import { useDynamicProperty } from "../../utils/hooks";
import { LovImage, LovProps, useLovListMemo } from "./lovUtils";
import { TaipyImage } from "./utils";

interface SliderProps extends LovProps<number | string, number | string> {
    width?: number | string;
    min?: number;
    max?: number;
    textAnchor?: string;
    alwaysUpdate?: boolean;
    labels?: string | boolean;
}

const Slider = (props: SliderProps) => {
    const {
        className,
        id,
        tp_varname,
        propagate = true,
        defaultValue,
        lov,
        defaultLov = "",
        textAnchor = "bottom",
        width = 300,
    } = props;
    const [value, setValue] = useState(0);
    const { dispatch } = useContext(TaipyContext);

    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const lovList = useLovListMemo(lov, defaultLov);

    const update = useMemo(
        () => (props.alwaysUpdate === undefined ? lovList.length === 0 : props.alwaysUpdate),
        [lovList, props.alwaysUpdate]
    );

    const min = lovList.length ? 0 : props.min;
    const max = lovList.length ? lovList.length - 1 : props.max;

    const handleRange = useCallback(
        (e, val: number | number[]) => {
            setValue(val as number);
            if (update) {
                const value = lovList.length ? lovList[val as number].id : val;
                dispatch(createSendUpdateAction(tp_varname, value, propagate));
            }
        },
        [lovList, update, tp_varname, dispatch, propagate]
    );

    const handleRangeCommitted = useCallback(
        (e, val: number | number[]) => {
            setValue(val as number);
            if (!update) {
                const value = lovList.length ? lovList[val as number].id : val;
                dispatch(createSendUpdateAction(tp_varname, value, propagate));
            }
        },
        [lovList, update, tp_varname, dispatch, propagate]
    );

    const getLabel = useCallback(
        (value) =>
            lovList.length > value ? (
                typeof lovList[value].item === "string" ? (
                    <Typography>{lovList[value].item}</Typography>
                ) : (
                    <LovImage item={lovList[value].item as TaipyImage} />
                )
            ) : (
                <>{value}</>
            ),
        [lovList]
    );

    const getText = useCallback(
        (value, before) => {
            if (lovList.length) {
                if (before && (textAnchor === "top" || textAnchor === "left")) {
                    return getLabel(value);
                }
                if (!before && (textAnchor === "bottom" || textAnchor === "right")) {
                    return getLabel(value);
                }
            }
            return null;
        },
        [lovList, textAnchor, getLabel]
    );

    const marks = useMemo(() => {
        if (props.labels) {
            if (typeof props.labels === "boolean") {
                if (lovList.length) {
                    return lovList.map((it, idx) => ({ value: idx, label: getLabel(idx) }));
                }
            } else {
                try {
                    const labels = JSON.parse(props.labels);
                    const marks: Array<{ value: number; label: string }> = [];
                    Object.keys(labels).forEach((key) => {
                        if (labels[key]) {
                            let idx = lovList.findIndex((it) => it.id === key);
                            if (idx == -1) {
                                try {
                                    idx = parseInt(key, 10);
                                } catch (e) {
                                    // too bad
                                }
                            }
                            if (idx != -1) {
                                marks.push({ value: idx, label: labels[key] });
                            }
                        }
                    });
                    if (marks.length) {
                        return marks;
                    }
                } catch (e) {
                    // won't happen
                }
            }
        }
        if (lovList.length > 0) {
            return true;
        }
        return false;
    }, [props.labels, lovList, getLabel]);

    const textAnchorSx = useMemo(() => {
        if (lovList.length) {
            if (textAnchor === "top" || textAnchor === "bottom") {
                return { width: width, display: "inline-grid", gap: "0.5em", textAlign: "center" } as SxProps;
            }
            if (textAnchor === "left" || textAnchor === "right") {
                return {
                    width: width,
                    display: "inline-grid",
                    gap: "1em",
                    gridTemplateColumns: textAnchor === "left" ? "auto 1fr" : "1fr auto",
                    alignItems: "center",
                } as SxProps;
            }
        }
        return { width: width, display: "inline-block" };
    }, [lovList, textAnchor, width]);

    useEffect(() => {
        if (props.value === undefined) {
            let val = 0;
            if (defaultValue !== undefined) {
                if (typeof defaultValue === "string") {
                    if (lovList.length) {
                        try {
                            const arrVal = JSON.parse(defaultValue) as string[];
                            val = lovList.findIndex((item) => item.id === arrVal[0]);
                            val = val === -1 ? 0 : val;
                        } catch (e) {
                            // Too bad also
                        }
                    } else {
                        try {
                            val = parseInt(defaultValue, 10);
                        } catch (e) {
                            // too bad
                        }
                    }
                } else {
                    val = defaultValue as number;
                }
            }
            setValue(val);
        } else {
            if (lovList.length) {
                const val = lovList.findIndex((item) => item.id === props.value);
                setValue(val === -1 ? 0 : val);
            } else {
                setValue(props.value as number);
            }
        }
    }, [props.value, lovList, defaultValue]);

    return (
        <Box sx={textAnchorSx} className={className}>
            {getText(value, true)}
            <MuiSlider
                id={id}
                value={value as number}
                onChange={handleRange}
                onChangeCommitted={handleRangeCommitted}
                disabled={!active}
                valueLabelDisplay="auto"
                min={min}
                max={max}
                step={1}
                marks={marks}
                valueLabelFormat={getLabel}
            />
            {getText(value, false)}
        </Box>
    );
};

export default Slider;
