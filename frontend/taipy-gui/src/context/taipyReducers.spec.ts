/*
 * Copyright 2023 Avaiga Private Limited
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

import { taipyReducer, INITIAL_STATE, TaipyBaseAction, createAlertAction, AlertMessage } from "./taipyReducers";

describe("reducer", () => {
    it("store socket connected", async () => {
        expect(taipyReducer({...INITIAL_STATE}, {type: "SOCKET_CONNECTED"} as TaipyBaseAction).isSocketConnected).toBeDefined();
    });
    it("returns update", async () => {
        expect(taipyReducer({...INITIAL_STATE}, {type: "UPDATE", name: "name", payload: {value: "value"}} as TaipyBaseAction).data.name).toBeDefined();
    });
    it("store locations", async () => {
        expect(taipyReducer({...INITIAL_STATE}, {type: "SET_LOCATIONS", payload: {value: {loc: "loc"}}} as TaipyBaseAction).locations).toBeDefined();
    });
    it("set alert", async () => {
        expect(taipyReducer({...INITIAL_STATE}, {type: "SET_ALERT", atype: "i", message: "message", system: "system"} as TaipyBaseAction).alerts).toHaveLength(1);
    });
    it("set show block", async () => {
        expect(taipyReducer({...INITIAL_STATE}, {type: "SET_BLOCK", action: "action", message: "message"} as TaipyBaseAction).block).toBeDefined();
    });
    it("set hide block", async () => {
        expect(taipyReducer({...INITIAL_STATE}, {type: "SET_BLOCK", action: "action", message: "message", close: true} as TaipyBaseAction).block).toBeUndefined();
    });
    it("set navigate", async () => {
        expect(taipyReducer({...INITIAL_STATE}, {type: "NAVIGATE", to: "navigateTo", tab: "_blank"} as TaipyBaseAction).navigateTo).toBeDefined();
    });
    it("set client id", async () => {
        expect(taipyReducer({...INITIAL_STATE}, {type: "CLIENT_ID", id: "id"} as TaipyBaseAction).id).toBeDefined();
    });
    it("set Acknowledgement", async () => {
        expect(taipyReducer({...INITIAL_STATE}, {type: "ACKNOWLEDGEMENT", id: "id"} as TaipyBaseAction)).toEqual(INITIAL_STATE);
    });
    it("remove Acknowledgement", async () => {
        expect(taipyReducer({...INITIAL_STATE, ackList: ["ack"]}, {type: "ACKNOWLEDGEMENT", id: "ack"} as TaipyBaseAction)).toEqual(INITIAL_STATE);
    });
    it("set Theme", async () => {
        expect(taipyReducer({...INITIAL_STATE}, {type: "SET_THEME", payload: {value: "dark"}} as TaipyBaseAction).theme).toBeDefined();
    });
    it("set TimeZone", async () => {
        expect(taipyReducer({...INITIAL_STATE}, {type: "SET_TIMEZONE", payload: {timeZone: "tz"}} as TaipyBaseAction).timeZone).toBeDefined();
    });
    it("set default TimeZone", async () => {
        expect(taipyReducer({...INITIAL_STATE}, {type: "SET_TIMEZONE", payload: {}} as TaipyBaseAction).timeZone).toBeDefined();
    });
    it("set Menu", async () => {
        expect(taipyReducer({...INITIAL_STATE}, {type: "SET_MENU", menu: {}} as TaipyBaseAction).menu).toBeDefined();
    });
    it("sets download", async () => {
        expect(taipyReducer({...INITIAL_STATE}, {type: "DOWNLOAD_FILE", content: {}} as TaipyBaseAction).download).toBeDefined();
    });
    it("resets download", async () => {
        expect(taipyReducer({...INITIAL_STATE}, {type: "DOWNLOAD_FILE"} as TaipyBaseAction).download).toBeUndefined();
    });
    it("sets partial", async () => {
        expect(taipyReducer({...INITIAL_STATE}, {type: "PARTIAL", name: "partial", create: true} as TaipyBaseAction).data.partial).toBeDefined();
    });
    it("resets partial", async () => {
        expect(taipyReducer({...INITIAL_STATE, data: {partial: true}}, {type: "PARTIAL", name: "partial"} as TaipyBaseAction).data.partial).toBeUndefined();
    });
    it("creates an alert action", () => {
        expect(createAlertAction({atype: "I", message: "message"} as AlertMessage).type).toBe("SET_ALERT");
        expect(createAlertAction({atype: "err", message: "message"} as AlertMessage).atype).toBe("error");
        expect(createAlertAction({atype: "Wa", message: "message"} as AlertMessage).atype).toBe("warning");
        expect(createAlertAction({atype: "sUc", message: "message"} as AlertMessage).atype).toBe("success");
        expect(createAlertAction({atype: "  ", message: "message"} as AlertMessage).atype).toBe("");
    });
});
