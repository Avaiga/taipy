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

import "@testing-library/jest-dom";
import {
    addRows,
    AlertMessage,
    BlockMessage,
    createAckAction,
    createAlertAction,
    createBlockAction,
    createDownloadAction,
    createIdAction,
    createNavigateAction,
    createPartialAction,
    createRequestChartUpdateAction,
    createRequestDataUpdateAction,
    createRequestInfiniteTableUpdateAction,
    createRequestTableUpdateAction,
    createRequestUpdateAction,
    createSendActionNameAction,
    createSendUpdateAction,
    FileDownloadProps,
    getPayload,
    getWsMessageListener,
    INITIAL_STATE,
    initializeWebSocket,
    messageToAction,
    NamePayload,
    NavigateMessage,
    retreiveBlockUi,
    storeBlockUi,
    TaipyBaseAction,
    taipyReducer,
    Types,
} from "./taipyReducers";
import { WsMessage } from "./wsUtils";
import { changeFavicon, getLocalStorageValue, IdMessage } from "./utils";
import { Socket } from "socket.io-client";
import { Dispatch } from "react";
import { parseData } from "../utils/dataFormat";
import * as wsUtils from "./wsUtils";

jest.mock("./utils", () => ({
    ...jest.requireActual("./utils"),
    changeFavicon: jest.fn(),
    messageToAction: jest.fn(),
    getLocalStorageValue: jest.fn(),
}));
jest.mock("../utils/dataFormat", () => ({
    parseData: jest.fn(),
}));
const sendWsMessageSpy = jest.spyOn(wsUtils, "sendWsMessage");
describe("reducer", () => {
    it("store socket connected", async () => {
        expect(
            taipyReducer({ ...INITIAL_STATE }, { type: "SOCKET_CONNECTED" } as TaipyBaseAction).isSocketConnected,
        ).toBeDefined();
    });
    it("returns update", async () => {
        expect(
            taipyReducer({ ...INITIAL_STATE }, {
                type: "UPDATE",
                name: "name",
                payload: { value: "value" },
            } as TaipyBaseAction).data.name,
        ).toBeDefined();
    });
    it("store locations", async () => {
        expect(
            taipyReducer({ ...INITIAL_STATE }, {
                type: "SET_LOCATIONS",
                payload: { value: { loc: "loc" } },
            } as TaipyBaseAction).locations,
        ).toBeDefined();
    });
    it("set alert", async () => {
        expect(
            taipyReducer({ ...INITIAL_STATE }, {
                type: "SET_ALERT",
                atype: "i",
                message: "message",
                system: "system",
            } as TaipyBaseAction).alerts,
        ).toHaveLength(1);
    });
    it("set show block", async () => {
        expect(
            taipyReducer({ ...INITIAL_STATE }, {
                type: "SET_BLOCK",
                action: "action",
                message: "message",
            } as TaipyBaseAction).block,
        ).toBeDefined();
    });
    it("set hide block", async () => {
        expect(
            taipyReducer({ ...INITIAL_STATE }, {
                type: "SET_BLOCK",
                action: "action",
                message: "message",
                close: true,
            } as TaipyBaseAction).block,
        ).toBeUndefined();
    });
    it("set navigate", async () => {
        expect(
            taipyReducer({ ...INITIAL_STATE }, {
                type: "NAVIGATE",
                to: "navigateTo",
                tab: "_blank",
            } as TaipyBaseAction).navigateTo,
        ).toBeDefined();
    });
    it("set client id", async () => {
        expect(taipyReducer({ ...INITIAL_STATE }, { type: "CLIENT_ID", id: "id" } as TaipyBaseAction).id).toBeDefined();
    });
    it("set Acknowledgement", async () => {
        expect(
            taipyReducer({ ...INITIAL_STATE }, {
                type: "ACKNOWLEDGEMENT",
                id: "id",
            } as TaipyBaseAction),
        ).toEqual(INITIAL_STATE);
    });
    it("remove Acknowledgement", async () => {
        expect(
            taipyReducer({ ...INITIAL_STATE, ackList: ["ack"] }, {
                type: "ACKNOWLEDGEMENT",
                id: "ack",
            } as TaipyBaseAction),
        ).toEqual(INITIAL_STATE);
    });
    it("set Theme", async () => {
        expect(
            taipyReducer({ ...INITIAL_STATE }, {
                type: "SET_THEME",
                payload: { value: "dark" },
            } as TaipyBaseAction).theme,
        ).toBeDefined();
    });
    it("set TimeZone", async () => {
        expect(
            taipyReducer({ ...INITIAL_STATE }, {
                type: "SET_TIMEZONE",
                payload: { timeZone: "tz" },
            } as TaipyBaseAction).timeZone,
        ).toBeDefined();
    });
    it("set default TimeZone", async () => {
        expect(
            taipyReducer({ ...INITIAL_STATE }, {
                type: "SET_TIMEZONE",
                payload: {},
            } as TaipyBaseAction).timeZone,
        ).toBeDefined();
    });
    it("set Menu", async () => {
        expect(
            taipyReducer({ ...INITIAL_STATE }, { type: "SET_MENU", menu: {} } as TaipyBaseAction).menu,
        ).toBeDefined();
    });
    it("sets download", async () => {
        expect(
            taipyReducer({ ...INITIAL_STATE }, {
                type: "DOWNLOAD_FILE",
                content: {},
            } as TaipyBaseAction).download,
        ).toBeDefined();
    });
    it("resets download", async () => {
        expect(
            taipyReducer({ ...INITIAL_STATE }, { type: "DOWNLOAD_FILE" } as TaipyBaseAction).download,
        ).toBeUndefined();
    });
    it("sets partial", async () => {
        expect(
            taipyReducer({ ...INITIAL_STATE }, {
                type: "PARTIAL",
                name: "partial",
                create: true,
            } as TaipyBaseAction).data.partial,
        ).toBeDefined();
    });
    it("resets partial", async () => {
        expect(
            taipyReducer({ ...INITIAL_STATE, data: { partial: true } }, {
                type: "PARTIAL",
                name: "partial",
            } as TaipyBaseAction).data.partial,
        ).toBeUndefined();
    });
    it("creates an alert action", () => {
        expect(createAlertAction({ atype: "I", message: "message" } as AlertMessage).type).toBe("SET_ALERT");
        expect(createAlertAction({ atype: "err", message: "message" } as AlertMessage).atype).toBe("error");
        expect(createAlertAction({ atype: "Wa", message: "message" } as AlertMessage).atype).toBe("warning");
        expect(createAlertAction({ atype: "sUc", message: "message" } as AlertMessage).atype).toBe("success");
        expect(createAlertAction({ atype: "  ", message: "message" } as AlertMessage).atype).toBe("");
    });
});

describe("storeBlockUi function", () => {
    let setItemSpy: jest.MockedFunction<(key: string, value: string) => void>;
    beforeEach(() => {
        setItemSpy = jest.spyOn(Storage.prototype, "setItem") as jest.MockedFunction<
            (key: string, value: string) => void
        >;
        global.localStorage = {
            setItem: setItemSpy,
            removeItem: jest.fn(),
            getItem: jest.fn(),
            clear: jest.fn(),
            length: 0,
            key: jest.fn(),
        };
    });
    afterEach(() => {
        setItemSpy.mockRestore();
    });
    it("stores message block in localStorage when document not visible", () => {
        Object.defineProperty(document, "visibilityState", { value: "hidden", configurable: true });
        const block: BlockMessage = {
            action: "yourAction",
            noCancel: false,
            close: false,
            message: "yourMessage",
        };
        storeBlockUi(block)();
        expect(localStorage.setItem).toHaveBeenCalledWith("TaipyBlockUi", JSON.stringify(block));
    });
    it("does not set localStorage when message block is defined and document is 'visible", () => {
        Object.defineProperty(document, "visibilityState", { value: "visible", configurable: true });
        const block: BlockMessage = {
            action: "yourAction",
            noCancel: false,
            close: false,
            message: "yourMessage",
        };
        storeBlockUi(block)();
        expect(localStorage.setItem).not.toHaveBeenCalled();
    });
});

describe("createNavigateAction function", () => {
    it("should create a navigate action with the correct properties", () => {
        const to = "testTo";
        const params = { testParam: "testValue" };
        const tab = "testTab";
        const force = true;
        const action = createNavigateAction(to, params, tab, force);
        expect(action.type).toEqual(Types.Navigate);
        expect(action.to).toEqual(to);
        expect(action.params).toEqual(params);
        expect(action.tab).toEqual(tab);
        expect(action.force).toEqual(force);
    });
});

describe("createRequestUpdateAction function", () => {
    it("should create a request update action with the correct properties", () => {
        const id = "testId";
        const context = "testContext";
        const names = ["name1", "name2"];
        const forceRefresh = true;
        const stateContext = { key: "value" };
        const action = createRequestUpdateAction(id, context, names, forceRefresh, stateContext);
        expect(action.type).toEqual(Types.RequestUpdate);
        expect(action.context).toEqual(context);
        expect(action.payload.id).toEqual(id);
        expect(action.payload.names).toEqual(names);
        expect(action.payload.refresh).toEqual(forceRefresh);
        expect(action.payload.state_context).toEqual(stateContext);
    });
});

describe("createRequestDataUpdateAction function", () => {
    it("should create a request data update action with the correct properties", () => {
        const name = "testName";
        const id = "testId";
        const context = "testContext";
        const columns = ["column1", "column2"];
        const pageKey = "testPageKey";
        const payload = { key: "value" };
        const allData = true;
        const library = "testLibrary";
        const action = createRequestDataUpdateAction(name, id, context, columns, pageKey, payload, allData, library);
        expect(action.type).toEqual(Types.RequestDataUpdate);
        expect(action.name).toEqual(name);
        expect(action.context).toEqual(context);
        expect(action.payload.id).toEqual(id);
        expect(action.payload.columns).toEqual(columns);
        expect(action.payload.pagekey).toEqual(pageKey);
        expect(action.payload.key).toEqual(payload.key);
        expect(action.payload.alldata).toEqual(allData);
        expect(action.payload.library).toEqual(library);
    });
});

describe("createRequestInfiniteTableUpdateAction function", () => {
    it("should create a request infinite table update action with the correct properties", () => {
        const name = "testName";
        const id = "testId";
        const context = "testContext";
        const columns = ["column1", "column2"];
        const pageKey = "testPageKey";
        const start = 0;
        const end = 10;
        const orderBy = "testOrderBy";
        const sort = "testSort";
        const aggregates = ["aggregate1", "aggregate2"];
        const applies = { key: "value" };
        const styles = { styleKey: "styleValue" };
        const tooltips = { tooltipKey: "tooltipValue" };
        const handleNan = true;
        const compare = "testCompare";
        const compareDatas = "testCompareDatas";
        const stateContext = { stateKey: "stateValue" };
        const reverse = true;
        const filters = [
            {
                field: "testField",
                operator: "testOperator",
                value: "testValue",
                col: "yourColValue",
                action: "yourActionValue",
            },
        ];
        const action = createRequestInfiniteTableUpdateAction(
            name,
            id,
            context,
            columns,
            pageKey,
            start,
            end,
            orderBy,
            sort,
            aggregates,
            applies,
            styles,
            tooltips,
            handleNan,
            filters,
            compare,
            compareDatas,
            stateContext,
            reverse,
        );
        expect(action.type).toEqual(Types.RequestDataUpdate);
        expect(action.name).toEqual(name);
        expect(action.context).toEqual(context);
        expect(action.payload.id).toEqual(id);
        expect(action.payload.columns).toEqual(columns);
        expect(action.payload.pagekey).toEqual(pageKey);
        expect(action.payload.start).toEqual(start);
        expect(action.payload.end).toEqual(end);
        expect(action.payload.orderby).toEqual(orderBy);
        expect(action.payload.sort).toEqual(sort);
        expect(action.payload.aggregates).toEqual(aggregates);
        expect(action.payload.applies).toEqual(applies);
        expect(action.payload.styles).toEqual(styles);
        expect(action.payload.tooltips).toEqual(tooltips);
        expect(action.payload.handlenan).toEqual(handleNan);
        expect(action.payload.filters).toEqual(filters);
        expect(action.payload.compare).toEqual(compare);
        expect(action.payload.compare_datas).toEqual(compareDatas);
        expect(action.payload.state_context).toEqual(stateContext);
        expect(action.payload.reverse).toEqual(reverse);
    });
});

describe("createRequestTableUpdateAction function", () => {
    it("should create a request table update action with the correct properties", () => {
        const name = "testName";
        const id = "testId";
        const context = "testContext";
        const columns = ["column1", "column2"];
        const pageKey = "testPageKey";
        const start = 0;
        const end = 10;
        const orderBy = "testOrderBy";
        const sort = "testSort";
        const aggregates = ["aggregate1", "aggregate2"];
        const applies = { key: "value" };
        const styles = { styleKey: "styleValue" };
        const tooltips = { tooltipKey: "tooltipValue" };
        const handleNan = true;
        const filters = [
            { field: "testField", operator: "testOperator", value: "testValue", col: "testCol", action: "testAction" },
        ];
        const compare = "testCompare";
        const compareDatas = "testCompareDatas";
        const stateContext = { stateKey: "stateValue" };
        const action = createRequestTableUpdateAction(
            name,
            id,
            context,
            columns,
            pageKey,
            start,
            end,
            orderBy,
            sort,
            aggregates,
            applies,
            styles,
            tooltips,
            handleNan,
            filters,
            compare,
            compareDatas,
            stateContext,
        );
        expect(action.type).toEqual(Types.RequestDataUpdate);
        expect(action.name).toEqual(name);
        expect(action.context).toEqual(context);
        expect(action.payload.id).toEqual(id);
        expect(action.payload.columns).toEqual(columns);
        expect(action.payload.pagekey).toEqual(pageKey);
        expect(action.payload.start).toEqual(start);
        expect(action.payload.end).toEqual(end);
        expect(action.payload.orderby).toEqual(orderBy);
        expect(action.payload.sort).toEqual(sort);
        expect(action.payload.aggregates).toEqual(aggregates);
        expect(action.payload.applies).toEqual(applies);
        expect(action.payload.styles).toEqual(styles);
        expect(action.payload.tooltips).toEqual(tooltips);
        expect(action.payload.handlenan).toEqual(handleNan);
        expect(action.payload.filters).toEqual(filters);
        expect(action.payload.compare).toEqual(compare);
        expect(action.payload.compare_datas).toEqual(compareDatas);
        expect(action.payload.state_context).toEqual(stateContext);
    });
});

describe("createRequestChartUpdateAction function", () => {
    it("should create a request chart update action with the correct properties", () => {
        const name = "testName";
        const id = "testId";
        const context = "testContext";
        const columns = ["column1", "column2"];
        const pageKey = "testPageKey";
        const decimatorPayload = { key: "value" };
        const action = createRequestChartUpdateAction(name, id, context, columns, pageKey, decimatorPayload);
        expect(action.type).toEqual(Types.RequestDataUpdate);
        expect(action.name).toEqual(name);
        expect(action.context).toEqual(context);
        expect(action.payload.id).toEqual(id);
        expect(action.payload.columns).toEqual(columns);
        expect(action.payload.pagekey).toEqual(pageKey);
        expect(action.payload.decimatorPayload).toEqual(decimatorPayload);
    });
});

describe("createSendActionNameAction function", () => {
    it("should create a send action name action with the correct properties", () => {
        const name = "testName";
        const context = "testContext";
        const value = { key: "value" };
        const args = ["arg1", "arg2"];
        const action = createSendActionNameAction(name, context, value, ...args);
        expect(action.type).toEqual(Types.Action);
        expect(action.name).toEqual(name);
        expect(action.context).toEqual(context);
        expect(action.payload.key).toEqual(value.key);
        expect(action.payload.args).toEqual(args);
    });
    it("should create a send action name action with value as action when value is not an object", () => {
        const name = "testName";
        const context = "testContext";
        const value = "testValue";
        const args = ["arg1", "arg2"];
        const action = createSendActionNameAction(name, context, value, ...args);
        expect(action.type).toEqual(Types.Action);
        expect(action.name).toEqual(name);
        expect(action.context).toEqual(context);
        expect(action.payload.action).toEqual(value);
        expect(action.payload.args).toEqual(args);
    });
});

describe("getPayload function", () => {
    it("should create a payload with the correct properties", () => {
        const value = "testValue";
        const onChange = "testOnChange";
        const relName = "testRelName";
        const payload = getPayload(value, onChange, relName);
        expect(payload.value).toEqual(value);
        expect(payload.on_change).toEqual(onChange);
        expect(payload.relvar).toEqual(relName);
    });
    it("should create a payload with only value when other parameters are not provided", () => {
        const value = "testValue";
        const payload = getPayload(value);
        expect(payload.value).toEqual(value);
        expect(payload.on_change).toBeUndefined();
        expect(payload.relvar).toBeUndefined();
    });
});

describe("createSendUpdateAction function", () => {
    it("should create a send update action with the correct properties", () => {
        const name = "testName";
        const value = "testValue";
        const context = "testContext";
        const onChange = "testOnChange";
        const propagate = true;
        const relName = "testRelName";
        const action = createSendUpdateAction(name, value, context, onChange, propagate, relName);
        expect(action.type).toEqual(Types.SendUpdate);
        expect(action.name).toEqual(name);
        expect(action.context).toEqual(context);
        expect(action.propagate).toEqual(propagate);
        expect(action.payload.value).toEqual(value);
        expect(action.payload.on_change).toEqual(onChange);
        expect(action.payload.relvar).toEqual(relName);
    });
});

describe("taipyReducer function", () => {
    it("should not change state for SOCKET_CONNECTED action if isSocketConnected is already true", () => {
        const action = { type: Types.SocketConnected };
        const initialState = { ...INITIAL_STATE, isSocketConnected: true };
        const newState = taipyReducer(initialState, action);
        const expectedState = { ...initialState, isSocketConnected: true };
        expect(newState).toEqual(expectedState);
    });
    it("should handle UPDATE action", () => {
        const action = {
            type: Types.Update,
            payload: {
                value: { someKey: "someValue" },
                infinite: false,
                pagekey: "somePageKey",
            },
            name: "someName",
        };
        const newState = taipyReducer({ ...INITIAL_STATE }, action);
        expect(newState.data[action.name]).toEqual({ [action.payload.pagekey]: action.payload.value });
    });
    it("should handle SET_LOCATIONS action", () => {
        const action = {
            type: Types.SetLocations,
            payload: { value: { location1: "value1", location2: "value2" } },
        };
        const newState = taipyReducer({ ...INITIAL_STATE }, action);
        expect(newState.locations).toEqual(action.payload.value);
    });
    it("should handle SET_ALERT action", () => {
        const action = {
            type: Types.SetAlert,
            atype: "error",
            message: "some error message",
            system: true,
            duration: 3000,
        };
        const newState = taipyReducer({ ...INITIAL_STATE }, action);
        expect(newState.alerts).toContainEqual({
            atype: action.atype,
            message: action.message,
            system: action.system,
            duration: action.duration,
        });
    });
    it("should handle DELETE_ALERT action", () => {
        const initialState = {
            ...INITIAL_STATE,
            alerts: [
                { atype: "error", message: "First Alert", system: true, duration: 5000 },
                { atype: "warning", message: "Second Alert", system: false, duration: 3000 },
            ],
        };
        const action = { type: Types.DeleteAlert };
        const newState = taipyReducer(initialState, action);
        expect(newState.alerts).toEqual([{ atype: "warning", message: "Second Alert", system: false, duration: 3000 }]);
    });
    it("should not modify state if no alerts are present", () => {
        const initialState = { ...INITIAL_STATE, alerts: [] };
        const action = { type: Types.DeleteAlert };
        const newState = taipyReducer(initialState, action);
        expect(newState).toEqual(initialState);
    });
    it("should handle DELETE_ALERT action", () => {
        const initialState = {
            ...INITIAL_STATE,
            alerts: [
                {
                    message: "alert1",
                    atype: "type1",
                    system: true,
                    duration: 5000,
                },
                {
                    message: "alert2",
                    atype: "type2",
                    system: false,
                    duration: 3000,
                },
            ],
        };
        const action = { type: Types.DeleteAlert };
        const newState = taipyReducer(initialState, action);
        expect(newState.alerts).toEqual([
            {
                message: "alert2",
                atype: "type2",
                system: false,
                duration: 3000,
            },
        ]);
    });
    it("should handle SET_BLOCK action", () => {
        const initialState = { ...INITIAL_STATE, block: undefined };
        const action = {
            type: Types.SetBlock,
            noCancel: false,
            action: "blockAction",
            close: false,
            message: "blockMessage",
        };
        const newState = taipyReducer(initialState, action);
        expect(newState.block).toEqual({
            noCancel: false,
            action: "blockAction",
            close: false,
            message: "blockMessage",
        });
    });
    it("should handle NAVIGATE action", () => {
        const initialState = {
            ...INITIAL_STATE,
            navigateTo: undefined,
            navigateParams: undefined,
            navigateTab: undefined,
            navigateForce: undefined,
        };
        const action = {
            type: Types.Navigate,
            to: "newLocation",
            params: { key: "value" },
            tab: "newTab",
            force: true,
        };
        const newState = taipyReducer(initialState, action);
        expect(newState.navigateTo).toEqual("newLocation");
        expect(newState.navigateParams).toEqual({ key: "value" });
        expect(newState.navigateTab).toEqual("newTab");
        expect(newState.navigateForce).toEqual(true);
    });
    it("should handle CLIENT_ID action", () => {
        const initialState = { ...INITIAL_STATE, id: "oldId" };
        const action = { type: Types.ClientId, id: "newId" };
        const newState = taipyReducer(initialState, action);
        expect(newState.id).toEqual("newId");
    });
    it("should handle ACKNOWLEDGEMENT action", () => {
        const initialState = { ...INITIAL_STATE, ackList: ["ack1", "ack2"] };
        const action = { type: Types.Acknowledgement, id: "ack1" };
        const newState = taipyReducer(initialState, action);
        expect(newState.ackList).toEqual(["ack2"]);
    });
    it("should handle SET_MENU action", () => {
        const initialState = { ...INITIAL_STATE, menu: {} };
        const action = { type: Types.SetMenu, menu: { menu1: "item1", menu2: "item2" } };
        const newState = taipyReducer(initialState, action);
        expect(newState.menu).toEqual({ menu1: "item1", menu2: "item2" });
    });
    it("should handle DOWNLOAD_FILE action", () => {
        const initialState = { ...INITIAL_STATE, download: undefined };
        const action = { type: Types.DownloadFile, content: "fileContent", name: "fileName", onAction: "fileAction" };
        const newState = taipyReducer(initialState, action);
        expect(newState.download).toEqual({ content: "fileContent", name: "fileName", onAction: "fileAction" });
    });
    it("should handle PARTIAL action", () => {
        const initialState = { ...INITIAL_STATE, data: { test: false } };
        const actionCreate = {
            type: Types.Partial,
            name: "test",
            create: true,
        };
        let newState = taipyReducer(initialState, actionCreate);
        expect(newState.data.test).toEqual(true);

        const actionDelete = {
            type: Types.Partial,
            name: "test",
            create: false,
        };
        newState = taipyReducer(newState, actionDelete);
        expect(newState.data.test).toBeUndefined();
    });
    it("should handle MULTIPLE_UPDATE action", () => {
        const initialState = { ...INITIAL_STATE, data: { test1: false, test2: false } };
        const action = {
            type: Types.MultipleUpdate,
            payload: [
                {
                    name: "test1",
                    payload: { value: true },
                },
                {
                    name: "test2",
                    payload: { value: true },
                },
            ],
        };
        const newState = taipyReducer(initialState, action);
        expect(newState.data.test1).toEqual(true);
        expect(newState.data.test2).toEqual(true);
    });
    it("should handle SetTimeZone action with fromBackend true", () => {
        const initialState = { ...INITIAL_STATE, timeZone: "oldTimeZone" };
        const action = { type: Types.SetTimeZone, payload: { timeZone: "newTimeZone", fromBackend: true } };
        const newState = taipyReducer(initialState, action);
        expect(newState.timeZone).toEqual("newTimeZone");
    });
    it("should handle SetTimeZone action with fromBackend false and localStorage value", () => {
        const initialState = { ...INITIAL_STATE, timeZone: "oldTimeZone" };
        const localStorageTimeZone = "localStorageTimeZone";
        localStorage.setItem("timeZone", localStorageTimeZone);
        const action = { type: Types.SetTimeZone, payload: { timeZone: "newTimeZone", fromBackend: false } };
        const newState = taipyReducer(initialState, action);
        expect(newState.timeZone).toEqual("UTC");
        localStorage.removeItem("timeZone");
    });
    it("should handle SetTimeZone action with fromBackend false and no localStorage value", () => {
        const initialState = { ...INITIAL_STATE, timeZone: "oldTimeZone" };
        const action = { type: Types.SetTimeZone, payload: { timeZone: "newTimeZone", fromBackend: false } };
        const newState = taipyReducer(initialState, action);
        expect(newState.timeZone).toEqual("UTC");
    });
    it("should handle SetTimeZone action with no change in timeZone", () => {
        const initialState = { ...INITIAL_STATE, timeZone: "oldTimeZone" };
        const action = { type: Types.SetTimeZone, payload: { timeZone: "oldTimeZone", fromBackend: true } };
        const newState = taipyReducer(initialState, action);
        expect(newState).toEqual(initialState);
    });
});

describe("addRows function", () => {
    it("should replace existing rows with new rows at the specified start index", () => {
        const previousRows = [
            { id: 1, value: "row1" },
            { id: 2, value: "row2" },
        ];
        const newRows = [
            { id: 3, value: "row3" },
            { id: 4, value: "row4" },
        ];
        const start = 1;
        const result = addRows(previousRows, newRows, start);
        const expected = [
            { id: 1, value: "row1" },
            { id: 3, value: "row3" },
            { id: 4, value: "row4" },
        ];
        expect(result).toEqual(expected);
    });
});

describe("retreiveBlockUi function", () => {
    it("should retrieve block message from localStorage", () => {
        const mockBlockMessage = { action: "testAction", noCancel: false, close: false, message: "testMessage" };
        Storage.prototype.getItem = jest.fn(() => JSON.stringify(mockBlockMessage));
        const result = retreiveBlockUi();
        expect(result).toEqual(mockBlockMessage);
    });

    it("should return an empty object if localStorage is empty", () => {
        Storage.prototype.getItem = jest.fn(() => null);
        const result = retreiveBlockUi();
        expect(result).toEqual({});
    });

    it("should return an empty object if localStorage contains invalid JSON", () => {
        Storage.prototype.getItem = jest.fn(() => "{ invalid json");
        const result = retreiveBlockUi();
        expect(result).toEqual({});
    });
});

describe("messageToAction function", () => {
    it("should handle 'MU' type with payload as an array", () => {
        const message: WsMessage = {
            type: "MU",
            payload: [
                {
                    name: "test1",
                    payload: {
                        value: true,
                    },
                },
                {
                    name: "test2",
                    payload: {
                        value: true,
                    },
                },
            ],
            name: "someName",
            propagate: true,
            client_id: "someClientId",
            module_context: "someModuleContext",
        };
        const result = messageToAction(message);
        const expected = {
            type: Types.MultipleUpdate,
            payload: [
                { name: "test1", payload: { value: true } },
                { name: "test2", payload: { value: true } },
            ],
        };
        expect(result).toEqual(expected);
    });
    it("should handle 'U' type", () => {
        const message: WsMessage = {
            type: "U",
            payload: [
                {
                    name: "test",
                    payload: {
                        value: true,
                    },
                },
            ],
            name: "test",
            propagate: true,
            client_id: "someClientId",
            module_context: "someModuleContext",
        };
        const result = messageToAction(message);
        const expected = {
            type: "UPDATE",
            name: "test",
            payload: [{ name: "test", payload: { value: true } }],
            propagate: true,
            client_id: "someClientId",
            module_context: "someModuleContext",
        };
        expect(result).toEqual(expected);
    });
    it('should call createAlertAction if message type is "AL"', () => {
        const message: WsMessage & Partial<AlertMessage> = {
            type: "AL",
            atype: "I",
            name: "someName",
            payload: {},
            propagate: true,
            client_id: "someClientId",
            module_context: "someModuleContext",
            ack_id: "someAckId",
        };
        const result = messageToAction(message);
        const expectedResult = createAlertAction(message as unknown as AlertMessage);
        expect(result).toEqual(expectedResult);
    });
    it('should call createBlockAction if message type is "BL"', () => {
        const message: WsMessage & Partial<BlockMessage> = {
            type: "BL",
            name: "someName",
            payload: {},
            propagate: true,
            client_id: "someClientId",
            module_context: "someModuleContext",
            ack_id: "someAckId",
        };
        const result = messageToAction(message);
        const expectedResult = createBlockAction(message as unknown as BlockMessage);
        expect(result).toEqual(expectedResult);
    });
    it('should call createNavigateAction if message type is "NA"', () => {
        const message: WsMessage & Partial<NavigateMessage> = {
            type: "NA",
            name: "someName",
            payload: {},
            propagate: true,
            client_id: "someClientId",
            module_context: "someModuleContext",
            ack_id: "someAckId",
            to: "someDestination",
            params: { key: "value" },
            tab: "someTab",
            force: true,
        };
        const result = messageToAction(message);
        const expectedResult = createNavigateAction(message.to, message.params, message.tab, message.force);
        expect(result).toEqual(expectedResult);
    });
    it('should call createIdAction if message type is "ID"', () => {
        const message: WsMessage & Partial<IdMessage> = {
            type: "ID",
            name: "someName",
            payload: {},
            propagate: true,
            client_id: "someClientId",
            module_context: "someModuleContext",
            ack_id: "someAckId",
            id: "someId",
        };
        const result = messageToAction(message);
        if (message.id) {
            const expectedResult = createIdAction(message.id);
            expect(result).toEqual(expectedResult);
        }
    });
    it('should call createDownloadAction if message type is "DF"', () => {
        const message: WsMessage & Partial<FileDownloadProps> = {
            type: "DF",
            name: "someName",
            payload: {},
            propagate: true,
            client_id: "someClientId",
            module_context: "someModuleContext",
            ack_id: "someAckId",
            content: "someContent",
            onAction: "someOnAction",
        };
        const result = messageToAction(message);
        const expectedResult = createDownloadAction(message as unknown as FileDownloadProps);
        expect(result).toEqual(expectedResult);
    });
    it('should call createPartialAction if message type is "PR"', () => {
        const message: WsMessage = {
            type: "PR",
            name: "someName",
            payload: "key",
            propagate: true,
            client_id: "someClientId",
            module_context: "someModuleContext",
            ack_id: "someAckId",
        };
        const result = messageToAction(message);
        const expectedResult = createPartialAction(message.name, true);
        expect(result).toEqual(expectedResult);
    });
    it('should call createAckAction if message type is "ACK"', () => {
        const message: WsMessage & Partial<IdMessage> = {
            type: "ACK",
            name: "someName",
            payload: {},
            propagate: true,
            client_id: "someClientId",
            module_context: "someModuleContext",
            ack_id: "someAckId",
            id: "someId",
        };
        const result = messageToAction(message);
        if (message.id) {
            const expectedResult = createAckAction(message.id);
            expect(result).toEqual(expectedResult);
        }
    });
    it('should call changeFavicon if message type is "FV"', () => {
        const message: WsMessage = {
            type: "FV",
            name: "someName",
            payload: {
                key1: "value1",
            },
            propagate: true,
            client_id: "someClientId",
            module_context: "someModuleContext",
            ack_id: "someAckId",
        };
        messageToAction(message);
        expect(changeFavicon).toHaveBeenCalled();
    });
});

describe("getWsMessageListener function", () => {
    it("should handle 'MS' type with payload as an array", () => {
        const mockDispatchWsMessage = jest.fn();
        const mockPayloads = [
            { type: "MU", name: "test1", payload: {} },
            { type: "MU", name: "test2", payload: {} },
            { type: "MU", name: "test3", payload: {} },
        ];
        const mockMessage: WsMessage = {
            type: "MS",
            name: "testName",
            payload: mockPayloads,
            propagate: true,
            client_id: "testClientId",
            module_context: "testModuleContext",
        };
        const dispatchWsMessage = getWsMessageListener(mockDispatchWsMessage);
        dispatchWsMessage(mockMessage);
        expect(mockDispatchWsMessage).toHaveBeenCalledTimes(mockPayloads.length);
    });
    it("should handle message with payload as NamePayload array", async () => {
        const mockDispatch = jest.fn();
        const mockPayloads: NamePayload[] = [
            { name: "test1", payload: { value: "value1" } },
            { name: "test2", payload: { value: "value2" } },
            { name: "test3", payload: { value: "value3" } },
        ];
        const mockMessage: WsMessage = {
            type: "MU",
            name: "testName",
            payload: mockPayloads,
            propagate: true,
            client_id: "testClientId",
            module_context: "testModuleContext",
        };
        (parseData as jest.Mock).mockImplementation((value) => Promise.resolve(value));

        const dispatchWsMessage = getWsMessageListener(mockDispatch);
        dispatchWsMessage(mockMessage);
        expect(parseData).toHaveBeenCalledTimes(mockPayloads.length);
    });
});

describe("initializeWebSocket function", () => {
    let mockSocket: jest.Mocked<Socket>;
    const mockDispatch: Dispatch<TaipyBaseAction> = jest.fn();
    beforeEach(() => {
        mockSocket = {
            on: jest.fn(),
            connect: jest.fn(),
        } as unknown as jest.Mocked<Socket>;
        (getLocalStorageValue as jest.Mock).mockReturnValue("mockId");
    });
    afterEach(() => {
        jest.resetAllMocks();
    });
    it("should set up event listeners and connect the socket if socket is provided", () => {
        initializeWebSocket(mockSocket, mockDispatch);
        expect(mockSocket.on).toHaveBeenCalledWith("connect", expect.any(Function));
        expect(mockSocket.on).toHaveBeenCalledWith("connect_error", expect.any(Function));
        expect(mockSocket.on).toHaveBeenCalledWith("disconnect", expect.any(Function));
        expect(mockSocket.on).toHaveBeenCalledWith("message", expect.any(Function));
        expect(mockSocket.connect).toHaveBeenCalled();
        expect(changeFavicon).toHaveBeenCalled();
    });
    it("should dispatch SocketConnected action on connect", () => {
        initializeWebSocket(mockSocket, mockDispatch);

        const connectCallback = mockSocket.on.mock.calls.find((call) => call[0] === "connect")?.[1];
        expect(connectCallback).toBeDefined();

        if (connectCallback) {
            connectCallback();
            expect(sendWsMessageSpy).toHaveBeenCalledWith(
                mockSocket,
                "ID",
                "TaipyClientId",
                "mockId",
                "mockId",
                undefined,
                false,
                expect.any(Function),
            );
        }
    });
    it("should not throw if socket is undefined", () => {
        expect(() => initializeWebSocket(undefined, mockDispatch)).not.toThrow();
    });
    it("should attempt to reconnect on server disconnection", () => {
        initializeWebSocket(mockSocket, mockDispatch);
        const disconnectCallback = mockSocket.on.mock.calls.find((call) => call[0] === "disconnect")?.[1];
        expect(disconnectCallback).toBeDefined();
        if (disconnectCallback) {
            disconnectCallback("io server disconnect");
            expect(mockSocket.connect).toHaveBeenCalled();
        }
    });
    it("should attempt to reconnect on connect_error", () => {
        jest.useFakeTimers();
        initializeWebSocket(mockSocket, mockDispatch);
        const connectErrorCallback = mockSocket.on.mock.calls.find((call) => call[0] === "connect_error")?.[1];
        expect(connectErrorCallback).toBeDefined();
        if (connectErrorCallback) {
            connectErrorCallback();
            jest.advanceTimersByTime(500);
            expect(mockSocket.connect).toHaveBeenCalled();
        }
        jest.useRealTimers();
    });
});
