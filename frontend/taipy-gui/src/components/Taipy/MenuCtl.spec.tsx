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

import React from "react";
import { render, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import mediaQuery from "css-mediaquery";
import { createTheme, ThemeProvider } from "@mui/material";

import MenuCtl from "./MenuCtl";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";
import { LoV } from "./lovUtils";

const lov: LoV = [
    ["id1", "Item 1"],
    ["id2", "Item 2"],
    ["id3", "Item 3"],
    ["id4", "Item 4"],
];
const defiids = '["id1","id2"]';

describe("MenuCtl Component", () => {
    it("dispatch a well formed message", async () => {
        Object.defineProperty(window, "matchMedia", {
            writable: true,
            value: jest.fn().mockImplementation((query) => ({
                matches: mediaQuery.match(query, {
                    width: 1000,
                }),
                media: query,
                onchange: null,
                addListener: jest.fn(), // Deprecated
                removeListener: jest.fn(), // Deprecated
                addEventListener: jest.fn(),
                removeEventListener: jest.fn(),
                dispatchEvent: jest.fn(),
            })),
        });
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const {} = render(
            <ThemeProvider theme={createTheme()}>
                <TaipyContext.Provider value={{ state, dispatch }}>
                    <MenuCtl label="MenuCtl" onAction="on_action" lov={lov} defaultInactiveIds={defiids} />
                </TaipyContext.Provider>
            </ThemeProvider>
        );
        await waitFor(() => {
            expect(dispatch).toHaveBeenCalledWith({
                menu: {
                    active: true,
                    className: "",
                    inactiveIds: ["id1", "id2"],
                    label: "MenuCtl",
                    lov: [
                        {
                            children: [],
                            id: "id1",
                            item: "Item 1",
                        },
                        {
                            children: [],
                            id: "id2",
                            item: "Item 2",
                        },
                        {
                            children: [],
                            id: "id3",
                            item: "Item 3",
                        },
                        {
                            children: [],
                            id: "id4",
                            item: "Item 4",
                        },
                    ],
                    onAction: "on_action",
                    width: "15vw",
                },
                type: "SET_MENU",
            });
        });
    });
});
