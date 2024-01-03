/*
 * Copyright 2021-2024 Avaiga Private Limited
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
import { getClientServerTimeZoneOffset } from "../../utils";

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
    // @ts-ignore
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
        const elts = getAllByTestId("CalendarIcon");
        expect(elts).toHaveLength(2);
        expect(elts[0].parentElement?.tagName).toBe("BUTTON");
    });
    it("displays the right info for string", async () => {
        const { getAllByTestId } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange dates={curDates} defaultDates={defaultDates} className="taipy-date-2" />
            </LocalizationProvider>
        );
        const elts = getAllByTestId("CalendarIcon");
        expect(elts).toHaveLength(2);
        expect(elts[0].parentElement?.parentElement?.parentElement?.parentElement).toHaveClass(
            "taipy-date-2-picker",
            "taipy-date-2-picker-start"
        );
        expect(elts[0].parentElement?.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass(
            "taipy-date-2"
        );
        expect(elts[1].parentElement?.parentElement?.parentElement?.parentElement).toHaveClass(
            "taipy-date-2-picker",
            "taipy-date-2-picker-end"
        );
        expect(elts[1].parentElement?.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass(
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
    it("shows labels", async () => {
        const { getByLabelText } = render(
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
        const startInput = getByLabelText("start") as HTMLInputElement;
        expect(startInput.value).toBe("01/01/2001");
        const endInput = getByLabelText("end") as HTMLInputElement;
        expect(endInput.value).toBe("01/31/2001");
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
        render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <DateRange dates={curDates} className="taipy-date-range" />
                </LocalizationProvider>
            </TaipyContext.Provider>
        );
        const input = document.querySelector(".taipy-date-range-picker-start input");
        expect(input).toBeInTheDocument();
        const input2 = document.querySelector(".taipy-date-range-picker-end input");
        expect(input2).toBeInTheDocument();
        if (input && input2) {
            await userEvent.clear(input);
            await userEvent.type(input, "{ArrowLeft}{ArrowLeft}{ArrowLeft}01012001", { delay: 1 });
            await userEvent.clear(input2);
            await userEvent.type(input2, "{ArrowLeft}{ArrowLeft}{ArrowLeft}01312001", { delay: 1 });
            expect(dispatch).toHaveBeenLastCalledWith({
                name: "",
                payload: { value: ["Mon Jan 01 2001", "Wed Jan 31 2001"] },
                propagate: true,
                type: "SEND_UPDATE_ACTION",
            });
        }
    });
});

describe("DateRange with time Component", () => {
    it("renders", async () => {
        const { getAllByTestId } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange dates={curDates} withTime={true} />
            </LocalizationProvider>
        );
        const elts = getAllByTestId("CalendarIcon");
        expect(elts).toHaveLength(2);
        expect(elts[0].parentElement?.tagName).toBe("BUTTON");
    });
    it("displays the right info for string", async () => {
        const { getAllByTestId } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange dates={curDates} withTime={true} className="taipy-time" />
            </LocalizationProvider>
        );
        const elts = getAllByTestId("CalendarIcon");
        expect(elts).toHaveLength(2);
        expect(elts[0].parentElement?.parentElement?.parentElement?.parentElement).toHaveClass(
            "taipy-time-picker",
            "taipy-time-picker-start"
        );
        expect(elts[0].parentElement?.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass(
            "taipy-time"
        );
        expect(elts[1].parentElement?.parentElement?.parentElement?.parentElement).toHaveClass(
            "taipy-time-picker",
            "taipy-time-picker-end"
        );
        expect(elts[1].parentElement?.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass(
            "taipy-time"
        );
    });
    it("displays the default value", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange
                    defaultDates="[&quot;2001-01-01T00:00:01.001Z&quot;,&quot;2001-01-31T00:00:01.001Z&quot;]"
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
    it("shows labels", async () => {
        const { getByLabelText } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateRange
                    defaultDates="[&quot;2001-01-01T00:00:01.001Z&quot;,&quot;2001-01-31T00:00:01.001Z&quot;]"
                    dates={undefined as unknown as string[]}
                    withTime={true}
                    className="taipy-date-range"
                    labelStart="start"
                    labelEnd="end"
                />
            </LocalizationProvider>
        );
        const startInput = getByLabelText("start") as HTMLInputElement;
        expect(startInput.value.toLocaleLowerCase()).toBe("01/01/2001 12:00 am");
        const endInput = getByLabelText("end") as HTMLInputElement;
        expect(endInput.value.toLocaleLowerCase()).toBe("01/31/2001 12:00 am");
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
        render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <DateRange dates={curDates} withTime={true} updateVarName="varname" className="tp-dt" />
                </LocalizationProvider>
            </TaipyContext.Provider>
        );
        const input = document.querySelector(".tp-dt-picker-start input");
        expect(input).toBeInTheDocument();
        const input2 = document.querySelector(".tp-dt-picker-end input");
        expect(input2).toBeInTheDocument();
        if (input && input2) {
            await userEvent.clear(input);
            await userEvent.type(
                input,
                "{ArrowLeft}{ArrowLeft}{ArrowLeft}{ArrowLeft}{ArrowLeft}{ArrowLeft}010120010101am",
                { delay: 1 }
            );
            await userEvent.clear(input2);
            await userEvent.type(
                input2,
                "{ArrowLeft}{ArrowLeft}{ArrowLeft}{ArrowLeft}{ArrowLeft}{ArrowLeft}123120010101am",
                { delay: 1 }
            );
            expect(dispatch).toHaveBeenLastCalledWith({
                name: "varname",
                payload: { value: ["2001-01-01T01:01:00.000Z", "2001-12-31T01:01:00.000Z"] },
                propagate: true,
                type: "SEND_UPDATE_ACTION",
            });
        }
    });
});
