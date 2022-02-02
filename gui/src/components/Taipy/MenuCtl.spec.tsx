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
                    <MenuCtl label="MenuCtl" tp_onAction="on_action" lov={lov} defaultInactiveIds={defiids} />
                </TaipyContext.Provider>
            </ThemeProvider>
        );
        await waitFor(() => {
            expect(dispatch).toHaveBeenCalledWith({
                menu: {
                    active: true,
                    className: undefined,
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
                    tp_onAction: "on_action",
                    width: "15vw",
                },
                type: "SET_MENU",
            });
        });
    });
});
