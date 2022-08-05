import { utcToZonedTime, getTimezoneOffset, formatInTimeZone } from "date-fns-tz";
import { sprintf } from "sprintf-js";
import { FormatConfig } from "../context/taipyReducers";

declare global {
    interface Window {
        taipyConfig: {
            darkMode: boolean;
            themes: Record<string, Record<string, unknown>>;
            timeZone: string;
            extensions: Record<string, string>;
        };
        taipyVersion: string;
        [key: string]: unknown;
    }
}

// return client server timeZone offset in minutes
export const getClientServerTimeZoneOffset = (tz: string): number =>
    (getTimezoneOffset(TIMEZONE_CLIENT) - getTimezoneOffset(tz)) / 60000;

export const getDateTime = (value: string | null | undefined, tz?: string): Date | null => {
    if (value === null || value === undefined) {
        return null;
    }
    try {
        return tz ? utcToZonedTime(value, tz) : new Date(value);
    } catch (e) {
        return null;
    }
};

export const getDateTimeString = (
    value: string,
    datetimeformat: string | undefined,
    formatConf: FormatConfig,
    tz?: string
): string =>
    formatInTimeZone(getDateTime(value) || "", formatConf.forceTZ || !tz ? formatConf.timeZone : tz, datetimeformat || formatConf.dateTime);

export const getNumberString = (value: number, numberformat: string | undefined, formatConf: FormatConfig): string => {
    try {
        return numberformat || formatConf.number
            ? sprintf(numberformat || formatConf.number, value)
            : value.toLocaleString();
    } catch (e) {
        console.info("getNumberString: " + (e as Error).message || e);
        return (
            (typeof value === "number" && value.toLocaleString()) ||
            (typeof value === "string" && (value as string)) ||
            ""
        );
    }
};

export const getTypeFromDf = (dataType?: string) => {
    switch (dataType) {
        case "datetime.datetime":
        case "datetime.date":
        case "datetime.time":
        case "datetime":
            return "date";
        case "int":
        case "float":
            return "number";
        case "bool":
            return "boolean";
    }
    return dataType;
}

export const formatWSValue = (
    value: string | number,
    dataType: string | undefined,
    dataFormat: string | undefined,
    formatConf: FormatConfig
): string => {
    dataType = dataType || typeof value;
    switch (dataType) {
        case "datetime.datetime":
        case "datetime.date":
        case "datetime.time":
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

export const TIMEZONE_CLIENT = Intl.DateTimeFormat().resolvedOptions().timeZone;
