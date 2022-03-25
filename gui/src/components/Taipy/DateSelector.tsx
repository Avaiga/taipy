import React, { useState, useEffect, useCallback, useContext } from "react";
import DatePicker from "@mui/lab/DatePicker";
import DateTimePicker from "@mui/lab/DateTimePicker";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";
import Tooltip from "@mui/material/Tooltip";
import { isValid } from "date-fns";

import { TaipyContext } from "../../context/taipyContext";
import { createSendUpdateAction } from "../../context/taipyReducers";
import { getSuffixedClassNames, TaipyActiveProps, TaipyChangeProps } from "./utils";
import { getDateTime, getClientServerTimeZoneOffset } from "../../utils";
import { useDynamicProperty, useFormatConfig } from "../../utils/hooks";
import Field from "./Field";

interface DateSelectorProps extends TaipyActiveProps, TaipyChangeProps {
    withTime?: boolean;
    format?: string;
    date: string;
    defaultDate?: string;
    defaultEditable?: boolean;
    editable?: boolean;
}

const boxSx = { display: "inline-block" };

const DateSelector = (props: DateSelectorProps) => {
    const { className, updateVarName, withTime = false, id, propagate = true } = props;
    const { dispatch } = useContext(TaipyContext);
    const formatConfig = useFormatConfig();
    const tz = formatConfig.timeZone;
    const [value, setValue] = useState(() => getDateTime(props.defaultDate, tz));

    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const editable = useDynamicProperty(props.editable, props.defaultEditable, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    const handleChange = useCallback(
        (v) => {
            setValue(v);
            const newDate = new Date(v);
            if (isValid(newDate)) {
                // dispatch new date which offset by the timeZone differences between client and server
                const hours = getClientServerTimeZoneOffset(tz) / 60;
                const minutes = getClientServerTimeZoneOffset(tz) % 60;
                newDate.setSeconds(0);
                newDate.setMilliseconds(0);
                if (withTime) {
                    // Parse data with selected time if it is a datetime selector
                    newDate.setHours(newDate.getHours() + hours);
                    newDate.setMinutes(newDate.getMinutes() + minutes);
                } else {
                    // Parse data with 00:00 UTC time if it is a date selector
                    newDate.setHours(hours);
                    newDate.setMinutes(minutes);
                }
                dispatch(createSendUpdateAction(updateVarName, newDate.toISOString(), props.tp_onChange, propagate));
            }
        },
        [updateVarName, dispatch, withTime, propagate, tz, props.tp_onChange]
    );

    const renderInput = useCallback(
        (params) => <TextField id={id} {...params} className={className} />,
        [id, className]
    );

    // Run every time props.value get updated
    useEffect(() => {
        if (props.date !== undefined) {
            setValue(getDateTime(props.date, tz));
        }
    }, [props.date, tz]);

    return (
        <Tooltip title={hover || ""}>
            <Box id={id} className={className} sx={boxSx}>
                {editable ? (
                    withTime ? (
                        <DateTimePicker
                            value={value}
                            onChange={handleChange}
                            renderInput={renderInput}
                            className={getSuffixedClassNames(className, "-picker")}
                            disabled={!active}
                        />
                    ) : (
                        <DatePicker
                            value={value}
                            onChange={handleChange}
                            renderInput={renderInput}
                            className={getSuffixedClassNames(className, "-picker")}
                            disabled={!active}
                        />
                    )
                ) : (
                    <Field
                        dataType="datetime.datetime"
                        defaultValue={props.defaultDate}
                        value={props.date}
                        format={props.format}
                        id={id + "-field"}
                        className={getSuffixedClassNames(className, "-text")}
                    />
                )}
            </Box>
        </Tooltip>
    );
};

export default DateSelector;
