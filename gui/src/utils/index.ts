import { utcToZonedTime, format, getTimezoneOffset } from "date-fns-tz"
import { sprintf } from "sprintf-js";

// set global style the traditonal way
export const setStyle = (styleString: string): void => {
    const style = document.createElement("style");
    style.textContent = styleString;
    document.head.append(style);
};

export const setDarkMode = (isDarkMode: boolean): void => {
    const htmlClasses = document.querySelector("html")?.classList;
    const mode = isDarkMode ? "dark" : "light";
    htmlClasses?.add(mode);
    localStorage.setItem("theme", mode);
};

export const setTimeZone = (timeZone: string): void => {
    if(!timeZone || timeZone === "client") {
        return localStorage.setItem("timeZone", TIMEZONE_CLIENT)
    }
    localStorage.setItem("timeZone", timeZone)
}

export const setDateTimeFormat = (datetimeformat: string): void => {
    localStorage.setItem("datetimeformat", datetimeformat)
}

export const getTimeZone = (): string => localStorage.getItem("timeZone") || TIMEZONE_CLIENT;

// return client server timeZone offset in minutes
export const getClientServerTimeZoneOffset = (): number => (getTimezoneOffset(TIMEZONE_CLIENT) - getTimezoneOffset(getTimeZone())) / 60000;

export const getDateTimeFormat = (): string => localStorage.getItem("datetimeformat") || DEFAULT_DATETIME_FORMAT;

export const getDateTime = (value: string): Date => utcToZonedTime(value, getTimeZone());

export const getDateTimeString = (value: string, datetimeformat: string): string => format(getDateTime(value), datetimeformat,  { timeZone: getTimeZone()})

export const formatWSValue = (value: string | number, dataType?: string, dataFormat?: string): string => {
    dataType = dataType || typeof value;
    switch (dataType) {
        case "datetime.datetime":
            try {
                if (dataFormat) {
                    return getDateTimeString(value.toString(), dataFormat);
                }
            } catch (e) {
                console.error(`wrong dateformat "${dataFormat}"`);
            }
            return getDateTimeString(value.toString(), getDateTimeFormat());
        case "int":
        case "number":
            if (typeof value === "string") {
                value = parseInt(value, 10);
            }
            if (dataFormat) {
                return sprintf(dataFormat, value);
            }
            return value.toLocaleString();
    }
    return value.toString();
};

/* eslint @typescript-eslint/no-explicit-any: "off", curly: "error" */
export const ENDPOINT = (!process.env.NODE_ENV || process.env.NODE_ENV === "development") ? process.env.REACT_APP_BACKEND_FLASK_URL : (window as any).flask_url;

export const TIMEZONE_CLIENT = Intl.DateTimeFormat().resolvedOptions().timeZone;

export const DEFAULT_DATETIME_FORMAT = 'yyyy-MM-dd HH:mm:ss zzz';
