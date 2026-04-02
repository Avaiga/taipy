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
import { render, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";

import Part from "./Part";
import { INITIAL_STATE, TaipyState } from "../../context/taipyReducers";
import { TaipyContext } from "../../context/taipyContext";

describe("Part Component", () => {
    it("renders", async () => {
        const { getByText } = render(<Part>bar</Part>);
        const elt = getByText("bar");
        expect(elt.tagName).toBe("DIV");
        expect(elt).toHaveClass("MuiBox-root");
    });
    it("displays the right info for string", async () => {
        const { getByText } = render(<Part className="taipy-part">bar</Part>);
        const elt = getByText("bar");
        expect(elt).toHaveClass("taipy-part");
    });
    it("displays with width=70%", async () => {
        const { getByText } = render(<Part width="70%">bar</Part>);
        const elt = getByText("bar");
        expect(elt).toHaveStyle("width: 70%");
    });
    it("displays with width=500", async () => {
        const { getByText } = render(<Part width={500}>bar</Part>);
        const elt = getByText("bar");
        expect(elt).toHaveStyle("width: 500px");
    });
    it("renders an iframe", async () => {
        const { getByText } = render(
            <Part className="taipy-part" page="http://taipy.io">
                bar
            </Part>
        );
        const elt = getByText("bar");
        expect(elt.parentElement?.firstElementChild?.tagName).toBe("DIV");
        expect(elt.parentElement?.firstElementChild?.firstElementChild?.tagName).toBe("IFRAME");
    });
    describe("Drag n Drop", () => {
        it("is not draggable if not dragType", async () => {
            const { getByText } = render(<Part dragType="">bar</Part>);
            const elt = getByText("bar");
            expect(elt.draggable).toBe(false);
        });
        it("is draggable if dragType", async () => {
            const { getByText } = render(<Part dragType="drag_type">bar</Part>);
            const elt = getByText("bar");
            expect(elt.draggable).toBe(true);
        });
        it("does not send a message if drag_type is not in drop_types", async () => {
            const dispatch = jest.fn();
            const state: TaipyState = INITIAL_STATE;
            const { getByText } = render(
                <TaipyContext.Provider value={{ state, dispatch }}>
                    <Part dragType="drag_type">bar</Part>
                    <Part allowedDragTypes={'"drop_type"'}>foo</Part>
                </TaipyContext.Provider>
            );
            const sourceElt = getByText("bar");
            const targetElt = getByText("foo");
            fireEvent.drop(targetElt, {
                dataTransfer: {
                    getData: (type: string) =>
                        type.endsWith("-done")
                            ? undefined
                            : JSON.stringify({
                                  type: "drag_type",
                                  itemId: "itemId",
                                  varName: "varName",
                                  sourceId: "sourceId",
                                  dragData: { par: "par" },
                              }),
                    setData: jest.fn(),
                },
            });
            fireEvent.dragEnd(sourceElt);
            expect(dispatch).not.toHaveBeenCalled();
        });
        it("sends a message if drag_type is in drop_types", async () => {
            const dispatch = jest.fn();
            const state: TaipyState = INITIAL_STATE;
            const { getByText } = render(
                <TaipyContext.Provider value={{ state, dispatch }}>
                    <Part dragType="drag_type">bar</Part>
                    <Part
                        allowedDragTypes={JSON.stringify(["drop_type", "drag_type"])}
                        defaultDropData={JSON.stringify({ drop: "drop" })}
                    >
                        foo
                    </Part>
                </TaipyContext.Provider>
            );
            const sourceElt = getByText("bar");
            const targetElt = getByText("foo");
            fireEvent.dragStart(sourceElt, { dataTransfer: { setData: jest.fn() } });
            fireEvent.dragOver(targetElt);
            fireEvent.drop(targetElt, {
                dataTransfer: {
                    getData: (type: string) =>
                        type.endsWith("-done")
                            ? undefined
                            : JSON.stringify({
                                  type: "drag_type",
                                  itemId: "itemId",
                                  varName: "varName",
                                  sourceId: "sourceId",
                                  sourceData: { par: "par" },
                              }),
                    setData: jest.fn(),
                },
            });
            fireEvent.dragEnd(sourceElt);
            expect(dispatch).toHaveBeenCalledWith({
                context: undefined,
                name: "",
                payload: {
                    args: [],
                    reason: "drop",
                    source_id: "sourceId",
                    source_item_id: "itemId",
                    source_data: {
                        par: "par",
                    },
                    source_var_name: "varName",
                    target_id: undefined,
                    target_item_id: undefined,
                    target_data: { drop: "drop" },
                },
                type: "SEND_ACTION_ACTION",
            });
        });
    });
});
