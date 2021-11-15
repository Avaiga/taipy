import { utcToZonedTime, format, getTimezoneOffset } from "date-fns-tz";
import { sprintf } from "sprintf-js";
import { FormatConfig } from "../context/taipyReducers";

// set global style the traditonal way
export const setStyle = (styleString: string): void => {
    const style = document.createElement("style");
    style.textContent = styleString;
    document.head.append(style);
};

// return client server timeZone offset in minutes
export const getClientServerTimeZoneOffset = (tz: string): number =>
    (getTimezoneOffset(TIMEZONE_CLIENT) - getTimezoneOffset(tz)) / 60000;

export const getDateTime = (value: string | undefined, tz: string): Date => utcToZonedTime(value || new Date(), tz);

export const getDateTimeString = (
    value: string,
    datetimeformat: string | undefined,
    formatConf: FormatConfig
): string =>
    format(getDateTime(value, formatConf.timeZone), datetimeformat || formatConf.dateTime, {
        timeZone: formatConf.timeZone,
    });

export const getNumberString = (value: number, numberformat: string | undefined, formatConf: FormatConfig): string =>
    numberformat || formatConf.number ? sprintf(numberformat || formatConf.number, value) : value.toLocaleString();

export const formatWSValue = (
    value: string | number,
    dataType: string | undefined,
    dataFormat: string | undefined,
    formatConf: FormatConfig
): string => {
    dataType = dataType || typeof value;
    switch (dataType) {
        case "datetime.datetime":
            try {
                return getDateTimeString(value.toString(), dataFormat, formatConf);
            } catch (e) {
                console.error(`wrong dateformat "${dataFormat || formatConf.dateTime}"`, e);
            }
            return getDateTimeString(value.toString(), undefined, formatConf);
        case "int":
        case "float":
        case "number":
            if (typeof value === "string") {
                try {
                    if (dataType === "float") {
                        value = parseFloat(value);
                    } else {
                        value = parseInt(value, 10);
                    }
                } catch (e) {
                    console.error("number parse exception", e);
                    value = NaN;
                }
            }
            return getNumberString(value, dataFormat, formatConf);
    }
    return value ? value.toString() : "";
};

export const getInitials = (value: string, max = 2): string =>
    (value || "")
        .split(" ", max)
        .map((word) => (word.length ? word.charAt(0) : ""))
        .join("")
        .toUpperCase();

/* eslint @typescript-eslint/no-explicit-any: "off", curly: "error" */
export const ENDPOINT =
    !process.env.NODE_ENV || process.env.NODE_ENV === "development" || process.env.NODE_ENV === "test"
        ? process.env.REACT_APP_BACKEND_FLASK_URL
        : (window as any).flask_url;

export const TIMEZONE_CLIENT = Intl.DateTimeFormat().resolvedOptions().timeZone;
