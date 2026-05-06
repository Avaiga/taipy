/*
 * Copyright 2021-2025 Avaiga Private Limited
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

import React from "react";
import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom";

import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";

import DateRange from "./DateRange";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";

jest.mock("../../utils", () => {
    const originalModule = jest.requireActual("../../utils");

    //Mock getClientServerTimeZoneOffset
    return {
        __esModule: true,
        ...originalModule,
        getClientServerTimeZoneOffset: () => 0,
    };
});

beforeEach(() => {
    // add window.matchMedia
    // this is necessary for the date picker to be rendered in desktop mode.
    // if this is not provided, the mobile mode is rendered, which might lead to unexpected behavior
    Object.defineProperty(window, "matchMedia", {
        writable: true,
        value: (query: string): MediaQueryList => ({
            media: query,
            // this is the media query that @material-ui/pickers uses to determine if a device is a desktop device
            matches: query === "(pointer: fine)",
            onchange: () => {},
            addEventListener: () => {},
            removeEventListener: () => {},
            addListener: () => {},
            removeListener: () => {},
            dispatchEvent: () => false,
        }),
    });
});

afterEach(() => {
    // @ts-expect-error
    delete window.matchMedia;
});

const curDate = new Date();
curDate.setHours(1, 1, 1, 1);
const curDateStr = curDate.toISOString();
const nextDate = new Date(curDate);
nextDate.setDate(nextDate.getDate() + 1);
const nextDateStr = nextDate.toISOString();
const curDates = [curDateStr, nextDateStr];
const cleanText = (val: string) => val.replace(/\u200e|\u2066|\u2067|\u2068|\u2069/g, "");
const defaultDates = '["2001-01-01T00:00:01.001Z","2001-01-31T00:00:01.001Z"]';

describe("DateRange Component", () => {
    it("renders", async () => {
        const { getAllByTestId } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange dates={curDates} />
            </LocalizationProvider>
        );
        const elements = getAllByTestId("CalendarIcon");
        expect(elements).toHaveLength(2);
        expect(elements[0].parentElement?.tagName).toBe("BUTTON");
    });
    it("renders with analog time picker", async () => {
        const { getAllByTestId } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange dates={curDates} withTime={true} analogic={true} />
            </LocalizationProvider>
        );
        const elements = getAllByTestId("CalendarIcon");
        expect(elements).toHaveLength(2);
        expect(elements[0].parentElement?.tagName).toBe("BUTTON");
    });
    it("displays the right info for string", async () => {
        const { getAllByTestId } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange dates={curDates} defaultDates={defaultDates} className="taipy-date-2" />
            </LocalizationProvider>
        );
        const elements = getAllByTestId("CalendarIcon");
        expect(elements).toHaveLength(2);
        expect(elements[0].parentElement?.parentElement?.parentElement?.parentElement).toHaveClass(
            "taipy-date-2-picker",
            "taipy-date-2-picker-start"
        );
        expect(elements[0].parentElement?.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass(
            "taipy-date-2"
        );
        expect(elements[1].parentElement?.parentElement?.parentElement?.parentElement).toHaveClass(
            "taipy-date-2-picker",
            "taipy-date-2-picker-end"
        );
        expect(elements[1].parentElement?.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass(
            "taipy-date-2"
        );
    });
    it("displays the default value", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange
                    defaultDates={defaultDates}
                    dates={undefined as unknown as string[]}
                    className="taipy-date-range"
                />
            </LocalizationProvider>
        );
        const input = document.querySelector(".taipy-date-range-picker-start input") as HTMLInputElement;
        expect(input).toBeInTheDocument();
        expect(cleanText(input?.value || "")).toEqual("01/01/2001");
        const input2 = document.querySelector(".taipy-date-range-picker-end input") as HTMLInputElement;
        expect(input2).toBeInTheDocument();
        expect(cleanText(input2?.value || "")).toEqual("01/31/2001");
    });
    it("displays the default value with format", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange
                    defaultDates={defaultDates}
                    dates={undefined as unknown as string[]}
                    className="taipy-date-range"
                    format="dd-MM-yyyy"
                />
            </LocalizationProvider>
        );
        const input = document.querySelector(".taipy-date-range-picker-start input") as HTMLInputElement;
        expect(input).toBeInTheDocument();
        expect(cleanText(input?.value || "")).toEqual("01-01-2001");
        const input2 = document.querySelector(".taipy-date-range-picker-end input") as HTMLInputElement;
        expect(input2).toBeInTheDocument();
        expect(cleanText(input2?.value || "")).toEqual("31-01-2001");
    });
    it("shows labels", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange
                    defaultDates={defaultDates}
                    dates={undefined as unknown as string[]}
                    className="taipy-date-range"
                    labelStart="start"
                    labelEnd="end"
                />
            </LocalizationProvider>
        );
        const labels = document.querySelectorAll("label");
        expect(labels).toHaveLength(2);
        const first = labels[0].textContent === "start";
        const startLabel = first ? labels[0] : labels[1];
        expect(startLabel.parentElement?.querySelector("input")?.value).toBe("01/01/2001");
        const endLabel = first ? labels[1] : labels[0];
        expect(endLabel.parentElement?.querySelector("input")?.value).toBe("01/31/2001");
    });
    it("displays with width=70%", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange dates={curDates} width="70%" />
            </LocalizationProvider>
        );
        const elt = document.querySelector(".MuiStack-root");
        expect(elt).toHaveStyle("width: 70%");
    });
    it("displays with width=500", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange dates={curDates} width={500} />
            </LocalizationProvider>
        );
        const elt = document.querySelector(".MuiStack-root");
        expect(elt).toHaveStyle("width: 500px");
    });
    it("is disabled", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange dates={curDates} active={false} className="taipy-date-range" />
            </LocalizationProvider>
        );
        const input = document.querySelector(".taipy-date-range-picker-start input");
        expect(input).toBeInTheDocument();
        expect(input).toBeDisabled();
        const input2 = document.querySelector(".taipy-date-range-picker-end input");
        expect(input2).toBeInTheDocument();
        expect(input2).toBeDisabled();
    });
    it("is enabled by default", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange dates={curDates} />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(input).not.toBeDisabled();
    });
    it("is enabled by active", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange dates={curDates} active={true} />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(input).not.toBeDisabled();
    });
    it("dispatch a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getAllByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <DateRange dates={undefined as unknown as string[]} className="taipy-date-range" />
                </LocalizationProvider>
            </TaipyContext.Provider>
        );
        const years = getAllByText("YYYY");
        expect(years).toHaveLength(2);
        expect(years[0]).toBeInTheDocument();
        expect(years[1]).toBeInTheDocument();
        await userEvent.type(years[0], "2001", { delay: 1 });
        await userEvent.type(years[1], "2001", { delay: 1 });

        const months = getAllByText("MM");
        expect(months).toHaveLength(2);
        expect(months[0]).toBeInTheDocument();
        expect(months[1]).toBeInTheDocument();
        if (months[0].closest(".taipy-date-range-picker-start")) {
            await userEvent.type(months[0], "01", { delay: 1 });
            await userEvent.type(months[1], "03", { delay: 1 });
        } else {
            await userEvent.type(months[1], "01", { delay: 1 });
            await userEvent.type(months[0], "03", { delay: 1 });
        }
        const days = getAllByText("DD");
        expect(days).toHaveLength(2);
        expect(days[0]).toBeInTheDocument();
        expect(days[1]).toBeInTheDocument();
        await userEvent.type(days[0], "01", { delay: 1 });
        await userEvent.type(days[1], "01", { delay: 1 });

        expect(dispatch).toHaveBeenLastCalledWith({
            name: "",
            payload: { value: ["Mon Jan 01 2001", "Thu Mar 01 2001"] },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
});

describe("DateRange with time Component", () => {
    it("renders", async () => {
        const { getAllByTestId } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange dates={curDates} withTime={true} />
            </LocalizationProvider>
        );
        const elements = getAllByTestId("CalendarIcon");
        expect(elements).toHaveLength(2);
        expect(elements[0].parentElement?.tagName).toBe("BUTTON");
    });
    it("displays the right info for string", async () => {
        const { getAllByTestId } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange dates={curDates} withTime={true} className="taipy-time" />
            </LocalizationProvider>
        );
        const elements = getAllByTestId("CalendarIcon");
        expect(elements).toHaveLength(2);
        expect(elements[0].parentElement?.parentElement?.parentElement?.parentElement).toHaveClass(
            "taipy-time-picker",
            "taipy-time-picker-start"
        );
        expect(elements[0].parentElement?.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass(
            "taipy-time"
        );
        expect(elements[1].parentElement?.parentElement?.parentElement?.parentElement).toHaveClass(
            "taipy-time-picker",
            "taipy-time-picker-end"
        );
        expect(elements[1].parentElement?.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass(
            "taipy-time"
        );
    });
    it("displays the default value", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange
                    defaultDates='["2001-01-01T00:00:01.001Z","2001-01-31T00:00:01.001Z"]'
                    withTime={true}
                    dates={undefined as unknown as string[]}
                    className="tp-dt"
                />
            </LocalizationProvider>
        );
        const input = document.querySelector(".tp-dt-picker-start input") as HTMLInputElement;
        expect(input).toBeInTheDocument();
        expect(cleanText(input?.value || "").toLocaleLowerCase()).toEqual("01/01/2001 12:00 am");
        const input2 = document.querySelector(".tp-dt-picker-end input") as HTMLInputElement;
        expect(input2).toBeInTheDocument();
        expect(cleanText(input2?.value || "").toLocaleLowerCase()).toEqual("01/31/2001 12:00 am");
    });
    it("displays the default value with format", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange
                    defaultDates='["2001-01-01T00:10:01.001Z","2001-01-31T00:11:01.001Z"]'
                    withTime={true}
                    dates={undefined as unknown as string[]}
                    className="tp-dt"
                    format="dd-MM-yyyy mm"
                />
            </LocalizationProvider>
        );
        const input = document.querySelector(".tp-dt-picker-start input") as HTMLInputElement;
        expect(input).toBeInTheDocument();
        expect(cleanText(input?.value || "").toLocaleLowerCase()).toEqual("01-01-2001 10");
        const input2 = document.querySelector(".tp-dt-picker-end input") as HTMLInputElement;
        expect(input2).toBeInTheDocument();
        expect(cleanText(input2?.value || "").toLocaleLowerCase()).toEqual("31-01-2001 11");
    });
    it("shows labels", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange
                    defaultDates='["2001-01-01T00:00:01.001Z","2001-01-31T00:00:01.001Z"]'
                    dates={undefined as unknown as string[]}
                    withTime={true}
                    className="taipy-date-range"
                    labelStart="start"
                    labelEnd="end"
                />
            </LocalizationProvider>
        );
        const labels = document.querySelectorAll("label");
        expect(labels).toHaveLength(2);
        const first = labels[0].textContent === "start";
        const startLabel = first ? labels[0] : labels[1];
        expect(startLabel.parentElement?.querySelector("input")?.value).toBe("01/01/2001 12:00 AM");
        const endLabel = first ? labels[1] : labels[0];
        expect(endLabel.parentElement?.querySelector("input")?.value).toBe("01/31/2001 12:00 AM");
    });
    it("is disabled", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange dates={curDates} withTime={true} active={false} className="tp-dt" />
            </LocalizationProvider>
        );
        const input = document.querySelector(".tp-dt-picker-start input");
        expect(input).toBeInTheDocument();
        expect(input).toBeDisabled();
        const input2 = document.querySelector(".tp-dt-picker-end input");
        expect(input2).toBeInTheDocument();
        expect(input2).toBeDisabled();
    });
    it("is enabled by default", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange dates={curDates} withTime={true} />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(input).not.toBeDisabled();
    });
    it("is enabled by active", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange dates={curDates} withTime={true} active={true} />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(input).not.toBeDisabled();
    });
    it("dispatch a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getAllByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <DateRange dates={[]} withTime={true} updateVarName="varname" className="tp-dt" />
                </LocalizationProvider>
            </TaipyContext.Provider>
        );

        const years = getAllByText("YYYY");
        expect(years).toHaveLength(2);
        expect(years[0]).toBeInTheDocument();
        expect(years[1]).toBeInTheDocument();
        await userEvent.type(years[0], "2001", { delay: 1 });
        await userEvent.type(years[1], "2001", { delay: 1 });

        const months = getAllByText("MM");
        expect(months).toHaveLength(2);
        expect(months[0]).toBeInTheDocument();
        expect(months[1]).toBeInTheDocument();
        if (months[0].closest(".taipy-date-range-picker-start")) {
            await userEvent.type(months[0], "12", { delay: 1 });
            await userEvent.type(months[1], "01", { delay: 1 });
        } else {
            await userEvent.type(months[1], "12", { delay: 1 });
            await userEvent.type(months[0], "01", { delay: 1 });
        }
        const days = getAllByText("DD");
        expect(days).toHaveLength(2);
        expect(days[0]).toBeInTheDocument();
        expect(days[1]).toBeInTheDocument();
        await userEvent.type(days[0], "01", { delay: 1 });
        await userEvent.type(days[1], "01", { delay: 1 });
        const hours = getAllByText("hh");
        expect(hours).toHaveLength(2);
        expect(hours[0]).toBeInTheDocument();
        expect(hours[1]).toBeInTheDocument();
        await userEvent.type(hours[0], "01", { delay: 1 });
        await userEvent.type(hours[1], "01", { delay: 1 });
        const minutes = getAllByText("mm");
        expect(minutes).toHaveLength(2);
        expect(minutes[0]).toBeInTheDocument();
        expect(minutes[1]).toBeInTheDocument();
        await userEvent.type(minutes[0], "01", { delay: 1 });
        await userEvent.type(minutes[1], "01", { delay: 1 });
        const ams = getAllByText("aa");
        expect(ams).toHaveLength(2);
        expect(ams[0]).toBeInTheDocument();
        expect(ams[1]).toBeInTheDocument();
        await userEvent.type(ams[0], "am", { delay: 1 });
        await userEvent.type(ams[1], "am", { delay: 1 });

        expect(dispatch).toHaveBeenLastCalledWith({
            name: "varname",
            payload: { value: ["2001-01-01T01:01:00.000Z", "2001-12-01T01:01:00.000Z"] },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
});
