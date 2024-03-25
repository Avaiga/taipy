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

import DateSelector from "./DateSelector";
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

const cleanText = (val: string) => val.replace(/\u200e|\u2066|\u2067|\u2068|\u2069/g, "");

describe("DateSelector Component", () => {
    it("renders", async () => {
        const { getByTestId } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} />
            </LocalizationProvider>
        );
        const elt = getByTestId("CalendarIcon");
        expect(elt.parentElement?.tagName).toBe("BUTTON");
    });
    it("displays the right info for string", async () => {
        const { getByTestId } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} defaultDate="2001-01-01T00:00:01.001Z" className="taipy-date" />
            </LocalizationProvider>
        );
        const elt = getByTestId("CalendarIcon");
        expect(elt.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass("taipy-date-picker");
        expect(elt.parentElement?.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass("taipy-date");
    });
    it("displays the default value", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector defaultDate="2001-01-01T00:00:01.001Z" date={undefined as unknown as string} />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(cleanText(input?.value || "")).toEqual("01/01/2001");
    });
    it("shows label", async () => {
        const { getByLabelText } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector
                    defaultDate="2001-01-01T00:00:01.001Z"
                    date={undefined as unknown as string}
                    className="taipy-date"
                    label="a label"
                />
            </LocalizationProvider>
        );
        const input = getByLabelText("a label") as HTMLInputElement;
        expect(input.value).toBe("01/01/2001");
    });
    it("is disabled", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} active={false} />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(input).toBeDisabled();
    });
    it("is enabled by default", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(input).not.toBeDisabled();
    });
    it("is enabled by active", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} active={true} />
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
                    <DateSelector date={curDateStr} />
                </LocalizationProvider>
            </TaipyContext.Provider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        if (input) {
            // await userEvent.clear(input);
            await userEvent.type(input, "{ArrowLeft}{ArrowLeft}{ArrowLeft}01012001", { delay: 1 });
            expect(dispatch).toHaveBeenLastCalledWith({
                name: "",
                payload: { value: "Mon Jan 01 2001" },
                propagate: true,
                type: "SEND_UPDATE_ACTION",
            });
        }
    });
});

describe("DateSelector with time Component", () => {
    it("renders", async () => {
        const { getByTestId } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} withTime={true} />
            </LocalizationProvider>
        );
        const elt = getByTestId("CalendarIcon");
        expect(elt.parentElement?.tagName).toBe("BUTTON");
    });
    it("displays the right info for string", async () => {
        const { getByTestId } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} withTime={true} className="taipy-time" />
            </LocalizationProvider>
        );
        const elt = getByTestId("CalendarIcon");
        expect(elt.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass("taipy-time-picker");
        expect(elt.parentElement?.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass("taipy-time");
    });
    it("displays the default value", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector
                    defaultDate="2001-01-01T01:01:01.001Z"
                    withTime={true}
                    date={undefined as unknown as string}
                />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(cleanText(input?.value || "").toLocaleLowerCase()).toEqual("01/01/2001 01:01 am");
    });
    it("is disabled", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} withTime={true} active={false} />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(input).toBeDisabled();
    });
    it("is enabled by default", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} withTime={true} />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(input).not.toBeDisabled();
    });
    it("is enabled by active", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} withTime={true} active={true} />
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
                    <DateSelector date={curDateStr} withTime={true} updateVarName="varname" />
                </LocalizationProvider>
            </TaipyContext.Provider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        if (input) {
            // await userEvent.clear(input);
            await userEvent.type(
                input,
                "{ArrowLeft}{ArrowLeft}{ArrowLeft}{ArrowLeft}{ArrowLeft}{ArrowLeft}010120010101am",
                { delay: 1 }
            );
            expect(dispatch).toHaveBeenLastCalledWith({
                name: "varname",
                payload: { value: "2001-01-01T01:01:00.000Z" },
                propagate: true,
                type: "SEND_UPDATE_ACTION",
            });
        }
    });
});
