import React from "react";
import { render, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom";

import { LocalizationProvider } from "@mui/lab";
import AdapterDateFns from "@mui/lab/AdapterDateFns";

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
const testDate = `${("" + (curDate.getMonth() + 1)).padStart(2, "0")}/${("" + curDate.getDate()).padStart(
    2,
    "0"
)}/${curDate.getFullYear()}`;

const testTime = testDate + " 01:01 am";

describe("DateSelector Component", () => {
    it("renders", async () => {
        const { getByDisplayValue } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} />
            </LocalizationProvider>
        );
        const elt = getByDisplayValue(testDate);
        expect(elt.tagName).toBe("INPUT");
    });
    it("displays the right info for string", async () => {
        const { getByDisplayValue } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} defaultDate="2001-01-01T00:00:01.001Z" className="taipy-date" />
            </LocalizationProvider>
        );
        const elt = getByDisplayValue(testDate);
        expect(elt.parentElement?.parentElement).toHaveClass("taipy-date");
    });
    it("displays the default value", async () => {
        const { getByDisplayValue } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector defaultDate="2001-01-01T00:00:01.001Z" date={undefined as unknown as string} />
            </LocalizationProvider>
        );
        getByDisplayValue("01/01/2001");
    });
    it("is disabled", async () => {
        const { getByDisplayValue } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} active={false} />
            </LocalizationProvider>
        );
        const elt = getByDisplayValue(testDate);
        expect(elt).toBeDisabled();
    });
    it("is enabled by default", async () => {
        const { getByDisplayValue } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} />
            </LocalizationProvider>
        );
        const elt = getByDisplayValue(testDate);
        expect(elt).not.toBeDisabled();
    });
    it("is enabled by active", async () => {
        const { getByDisplayValue } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} active={true} />
            </LocalizationProvider>
        );
        const elt = getByDisplayValue(testDate);
        expect(elt).not.toBeDisabled();
    });
    it("dispatch a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByDisplayValue } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <DateSelector date={curDateStr} />
                </LocalizationProvider>
            </TaipyContext.Provider>
        );
        const elt = getByDisplayValue(testDate);
        userEvent.clear(elt);
        await userEvent.type(elt, "01012001", { delay: 1 });
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "",
            payload: { value: "2001-01-01T00:00:00.000Z", type: "date" },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
});

describe("DateSelector with time Component", () => {
    it("renders", async () => {
        const { getByDisplayValue } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} withTime={true} />
            </LocalizationProvider>
        );
        const elt = getByDisplayValue(testTime);
        expect(elt.tagName).toBe("INPUT");
    });
    it("displays the right info for string", async () => {
        const { getByDisplayValue } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} withTime={true} className="taipy-time" />
            </LocalizationProvider>
        );
        const elt = getByDisplayValue(testTime);
        expect(elt.parentElement?.parentElement).toHaveClass("taipy-time");
    });
    it("displays the default value", async () => {
        const { getByDisplayValue } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector defaultDate={curDateStr} withTime={true} date={undefined as unknown as string} />
            </LocalizationProvider>
        );
        getByDisplayValue(testTime);
    });
    it("is disabled", async () => {
        const { getByDisplayValue } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} withTime={true} active={false} />
            </LocalizationProvider>
        );
        const elt = getByDisplayValue(testTime);
        expect(elt).toBeDisabled();
    });
    it("is enabled by default", async () => {
        const { getByDisplayValue } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} withTime={true} />
            </LocalizationProvider>
        );
        const elt = getByDisplayValue(testTime);
        expect(elt).not.toBeDisabled();
    });
    it("is enabled by active", async () => {
        const { getByDisplayValue } = render(
            <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateSelector date={curDateStr} withTime={true} active={true} />
            </LocalizationProvider>
        );
        const elt = getByDisplayValue(testTime);
        expect(elt).not.toBeDisabled();
    });
    it("dispatch a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByDisplayValue } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <DateSelector date={curDateStr} withTime={true} tp_varname="varname" />
                </LocalizationProvider>
            </TaipyContext.Provider>
        );
        const elt = getByDisplayValue(testTime);
        userEvent.clear(elt);
        await userEvent.type(elt, "01/01/2001 01:01 am", { delay: 1 });
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "varname",
            payload: { value: "2001-01-01T01:01:00.000Z", type: "date" },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
});
