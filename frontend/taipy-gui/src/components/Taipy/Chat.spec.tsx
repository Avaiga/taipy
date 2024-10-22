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
import { render, waitFor, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import Chat from "./Chat";
import { INITIAL_STATE, TaipyState } from "../../context/taipyReducers";
import { TaipyContext } from "../../context/taipyContext";
import { stringIcon } from "../../utils/icon";
import { TableValueType } from "./tableUtils";

const valueKey = "Infinite-Entity--asc";
const messages: TableValueType = {
    [valueKey]: {
        data: [
    ["1", "msg 1", "Fred"],
    ["2", "msg From Another unknown User", "Fredo"],
    ["3", "This from the sender User", "taipy"],
    ["4", "And from another known one", "Fredi"],
], rowcount: 4, start: 0}};
const user1: [string, stringIcon] = ["Fred", { path: "/images/favicon.png", text: "Fred.png" }];
const user2: [string, stringIcon] = ["Fredi", { path: "/images/fred.png", text: "Fredi.png" }];
const users = [user1, user2];

const searchMsg = messages[valueKey].data[0][1];

describe("Chat Component", () => {
    it("renders", async () => {
        const { getByText, getByLabelText } = render(<Chat messages={messages} defaultKey={valueKey} mode="raw" />);
        const elt = getByText(searchMsg);
        expect(elt.tagName).toBe("DIV");
        const input = getByLabelText("message (taipy)");
        expect(input.tagName).toBe("INPUT");
    });
    it("uses the class", async () => {
        const { getByText } = render(<Chat messages={messages} className="taipy-chat" defaultKey={valueKey} mode="raw" />);
        const elt = getByText(searchMsg);
        expect(elt.parentElement?.parentElement?.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass("taipy-chat");
    });
    it("can display an avatar", async () => {
        const { getByAltText } = render(<Chat messages={messages} users={users} defaultKey={valueKey} mode="raw"/>);
        const elt = getByAltText("Fred.png");
        expect(elt.tagName).toBe("IMG");
    });
    it("is disabled", async () => {
        const { getAllByRole } = render(<Chat messages={messages} active={false} defaultKey={valueKey} mode="raw"/>);
        const elts = getAllByRole("button");
        elts.forEach((elt) => expect(elt).toHaveClass("Mui-disabled"));
    });
    it("is enabled by default", async () => {
        const { getAllByRole } = render(<Chat messages={messages} defaultKey={valueKey} mode="raw"/>);
        const elts = getAllByRole("button");
        elts.forEach((elt) => expect(elt).not.toHaveClass("Mui-disabled"));
    });
    it("is enabled by active", async () => {
        const { getAllByRole } = render(<Chat messages={messages} active={true} defaultKey={valueKey} mode="raw"/>);
        const elts = getAllByRole("button");
        elts.forEach((elt) => expect(elt).not.toHaveClass("Mui-disabled"));
    });
    it("can hide input", async () => {
        render(<Chat messages={messages} withInput={false} className="taipy-chat" defaultKey={valueKey} mode="raw"/>);
        const elt = document.querySelector(".taipy-chat input");
        expect(elt).toBeNull();
    });
    it("renders markdown by default", async () => {
        render(<Chat messages={messages} className="taipy-chat" defaultKey={valueKey} />);
        const elt = document.querySelector(".taipy-chat .taipy-chat-received .MuiPaper-root");
        await waitFor(() => expect(elt?.querySelector("p")).not.toBeNull());
    });
    it("can render pre", async () => {
        const { getByText } = render(<Chat messages={messages} defaultKey={valueKey} className="taipy-chat"  mode="pre" />);
        const elt = getByText(searchMsg);
        expect(elt.tagName).toBe("PRE");
        expect(elt.parentElement).toHaveClass("taipy-chat-pre");
    });
    it("can render raw", async () => {
        const { getByText } = render(<Chat messages={messages} defaultKey={valueKey} className="taipy-chat"  mode="raw" />);
        const elt = getByText(searchMsg);
        expect(elt).toHaveClass("taipy-chat-raw");
    });
    it("dispatch a well formed message by Keyboard", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByLabelText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Chat messages={messages} updateVarName="varName" defaultKey={valueKey} mode="raw"/>
            </TaipyContext.Provider>
        );
        const elt = getByLabelText("message (taipy)");
        await userEvent.click(elt);
        await userEvent.keyboard("new message{Enter}");
        expect(dispatch).toHaveBeenCalledWith({
            type: "SEND_ACTION_ACTION",
            name: "",
            context: undefined,
            payload: {
                action: undefined,
                args: ["Enter", "varName", "new message", "taipy",null],
            },
        });
    });
    it("dispatch a well formed message by button", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByLabelText, getByRole } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Chat messages={messages} updateVarName="varName" defaultKey={valueKey} mode="raw"/>
            </TaipyContext.Provider>
        );
        const elt = getByLabelText("message (taipy)");
        await userEvent.click(elt);
        await userEvent.keyboard("new message");
        await userEvent.click(getByRole("button",{ name: /send message/i }))
        expect(dispatch).toHaveBeenCalledWith({
            type: "SEND_ACTION_ACTION",
            name: "",
            context: undefined,
            payload: {
                action: undefined,
                args: ["click", "varName", "new message", "taipy",null],
            },
        });
    });
    it("handle image upload",async()=>{
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByLabelText,getByText,getByAltText,queryByText,getByRole } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Chat messages={messages} updateVarName="varName" defaultKey={valueKey} mode="raw"/>
            </TaipyContext.Provider>
        );
        const file = new File(['(⌐□_□)'], 'test.png', { type: 'image/png' });
        URL.createObjectURL = jest.fn(() => 'mocked-url');
        URL.revokeObjectURL = jest.fn();

        const attachButton = getByLabelText('upload image');
        expect(attachButton).toBeInTheDocument();


        const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
        expect(fileInput).toBeInTheDocument();
        fireEvent.change(fileInput, { target: { files: [file] } });

        await waitFor(() => {
            const chipWithImage = getByText('test.png');
            expect(chipWithImage).toBeInTheDocument();
            const previewImg = getByAltText('Image preview');
            expect(previewImg).toBeInTheDocument();
            expect(previewImg).toHaveAttribute('src', 'mocked-url');
          });

          const elt = getByLabelText("message (taipy)");
          await userEvent.click(elt);
          await userEvent.keyboard("Test message with image");
          await userEvent.click(getByRole("button",{ name: /send message/i }))

          expect(dispatch).toHaveBeenNthCalledWith(2,
            expect.objectContaining({
              type: 'SEND_ACTION_ACTION',
              payload: expect.objectContaining({
                args: ['click', 'varName', 'Test message with image', 'taipy', 'mocked-url']
              })
            })
          );
          await waitFor(() => {
            const chipWithImage = queryByText('test.png');
            expect(chipWithImage).not.toBeInTheDocument();
          });
          jest.restoreAllMocks()
    })
    it("Not upload image over a file size limit",async()=>{
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText,getByAltText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Chat messages={messages} updateVarName="varName" maxFileSize={0} defaultKey={valueKey} mode="raw"/>
            </TaipyContext.Provider>
        );
        const file = new File(['(⌐□_□)'], 'test.png', { type: 'image/png' });
        URL.createObjectURL = jest.fn(() => 'mocked-url');

        const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
        expect(fileInput).toBeInTheDocument();
        fireEvent.change(fileInput, { target: { files: [file] } });

        await waitFor(() => {
            expect(() =>getByText('test.png')).toThrow()
            expect(()=>getByAltText('Image preview')).toThrow();
          });
          jest.restoreAllMocks()
    })
});
