import { format } from "date-fns";
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

export const formatWSValue = (value: string | number, dataType?: string, dataFormat?: string): string => {
    dataType = dataType || typeof value;
    switch (dataType) {
        case "datetime.datetime":
            try {
                if (dataFormat) {
                    return format(new Date(value), dataFormat);
                } 
            } catch (e) {
                console.error(`wrong dateformat "${dataFormat}"`);
            }
            return new Date(value).toISOString();
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
