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
import { render, fireEvent, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom";

import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFnsV3";

import TimeSelector from "./TimeSelector";
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

describe("TimeSelector component with digital time picker", () => {
    it("renders", async () => {
        const { getByTestId } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <TimeSelector time={curDateStr} />
            </LocalizationProvider>
        );
        const elt = getByTestId("ClockIcon");
        expect(elt.parentElement?.tagName).toBe("BUTTON");
    });

    it("displays the right info for string", async () => {
        const { getByTestId } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <TimeSelector time={curDateStr} className="taipy-time" />
            </LocalizationProvider>
        );
        const elt = getByTestId("ClockIcon");
        expect(elt.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass("taipy-time-picker");
        expect(elt.parentElement?.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass("taipy-time");
    });

    it("displays the right value after supplied by picker ", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <TimeSelector
                    time={undefined as unknown as string}
                />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        fireEvent.change(screen.getByRole("textbox"), {target: {value: '10:20 AM'}});
        expect(screen.getByRole('textbox')).toHaveValue('10:20 AM');
    });

    it("displays the default value", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <TimeSelector
                    defaultTime="2001-01-01T01:01:01"
                    time={undefined as unknown as string}
                />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(cleanText(input?.value || "").toLocaleLowerCase()).toEqual("01:01 am");
    });
    it("displays the default value with format", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <TimeSelector
                    defaultTime="2001-01-01T14:20:01"
                    time={undefined as unknown as string}
                    format="hh aa"
                />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(cleanText(input?.value || "")).toEqual("02 PM");
    });
    it("is disabled", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <TimeSelector time={curDateStr} active={false} />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(input).toBeDisabled();
    });
    it("is enabled by default", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <TimeSelector time={curDateStr} />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(input).not.toBeDisabled();
    });
    it("is enabled by active", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <TimeSelector time={curDateStr} active={true} />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(input).not.toBeDisabled();
    });
});

describe("TimeSelector component with analogue time picker", () => {
    it("renders", async () => {
        const { getByTestId } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <TimeSelector time={curDateStr} analogic={true} />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
    });
    it("displays the default value", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <TimeSelector
                    defaultTime="2001-01-01T01:01:01"
                    time={undefined as unknown as string}
                    analogic={true}
                />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(cleanText(input?.value || "").toLocaleLowerCase()).toEqual("01:01 am");
    });
    it("displays the default value with format", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <TimeSelector
                    defaultTime="2001-01-01T14:20:01"
                    time={undefined as unknown as string}
                    analogic={true}
                    format="hh aa"
                />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(cleanText(input?.value || "")).toEqual("02 PM");
    });

    it("is disabled", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <TimeSelector time={curDateStr} active={false} analogic={true} />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(input).toBeDisabled();
    });
    it("is enabled by default", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <TimeSelector time={curDateStr} analogic={true} />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(input).not.toBeDisabled();
    });
    it("is enabled by active", async () => {
        render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <TimeSelector time={curDateStr} active={true} analogic={true} />
            </LocalizationProvider>
        );
        const input = document.querySelector("input");
        expect(input).toBeInTheDocument();
        expect(input).not.toBeDisabled();
    });
});