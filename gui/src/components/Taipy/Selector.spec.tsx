import React from "react";
import { render } from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import Selector from "./Selector";
import { LoV } from "./lovUtils";
import { TaipyImage } from "./utils";
import { INITIAL_STATE, TaipyState } from "../../context/taipyReducers";
import { TaipyContext } from "../../context/taipyContext";

const lov: LoV = [
    ["id1", "Item 1"],
    ["id2", "Item 2"],
    ["id3", "Item 3"],
    ["id4", "Item 4"],
];
const defLov = '[["id10","Default Item"]]';

const imageItem: [string, string | TaipyImage] = ["ii1", { path: "/img/fred.png", text: "Image" }];

describe("Selector Component", () => {
    it("renders", async () => {
        const { getByText } = render(<Selector lov={lov} />);
        const elt = getByText("Item 1");
        expect(elt.tagName).toBe("SPAN");
    });
    it("uses the class", async () => {
        const { getByText } = render(<Selector lov={lov} className="taipy-selector" />);
        const elt = getByText("Item 1");
        expect(elt.parentElement?.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass(
            "taipy-selector"
        );
    });
    it("can display an image", async () => {
        const lovWithImage = [...lov, imageItem];
        const { getByAltText } = render(<Selector lov={lovWithImage} />);
        const elt = getByAltText("Image");
        expect(elt.tagName).toBe("IMG");
    });
    it("displays the right info for lov vs defaultLov", async () => {
        const { getByText, queryAllByText } = render(<Selector lov={lov} defaultLov={defLov} />);
        getByText("Item 1");
        expect(queryAllByText("Default Item")).toHaveLength(0);
    });
    it("displays the default LoV", async () => {
        const { getByText } = render(<Selector lov={undefined as unknown as []} defaultLov={defLov} />);
        getByText("Default Item");
    });
    it("shows a selection at start", async () => {
        const { getByText } = render(<Selector defaultValue="id1" lov={lov} />);
        const elt = getByText("Item 1");
        expect(elt.parentElement?.parentElement).toHaveClass("Mui-selected");
    });
    it("shows a selection at start through value", async () => {
        const { getByText } = render(<Selector defaultValue="id1" value="id2" lov={lov} />);
        const elt = getByText("Item 1");
        expect(elt.parentElement?.parentElement).not.toHaveClass("Mui-selected");
        const elt2 = getByText("Item 2");
        expect(elt2.parentElement?.parentElement).toHaveClass("Mui-selected");
    });
    it("is disabled", async () => {
        const { getAllByRole } = render(<Selector lov={lov} active={false} />);
        const elts = getAllByRole("button");
        elts.forEach((elt) => expect(elt).toHaveClass("Mui-disabled"));
    });
    it("is enabled by default", async () => {
        const { getAllByRole } = render(<Selector lov={lov} />);
        const elts = getAllByRole("button");
        elts.forEach((elt) => expect(elt).not.toHaveClass("Mui-disabled"));
    });
    it("is enabled by active", async () => {
        const { getAllByRole } = render(<Selector lov={lov} active={true} />);
        const elts = getAllByRole("button");
        elts.forEach((elt) => expect(elt).not.toHaveClass("Mui-disabled"));
    });
    it("dispatch a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Selector lov={lov} tp_varname="varname" />
            </TaipyContext.Provider>
        );
        const elt = getByText("Item 1");
        userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({
            name: "varname",
            payload: { value: "id1" },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
    //multiple
    describe("Selector Component with multiple", () => {
        it("displays checkboxes when multiple", async () => {
            const { queryAllByRole } = render(<Selector lov={lov} multiple={true} />);
            expect(queryAllByRole("checkbox")).toHaveLength(4);
        });
        it("does not display checkboxes when not multiple", async () => {
            const { queryAllByRole } = render(<Selector lov={lov} multiple={false} />);
            expect(queryAllByRole("checkbox")).toHaveLength(0);
        });
        it("selects 2 items", async () => {
            const { queryAllByRole } = render(<Selector lov={lov} multiple={true} value={["id1", "id2"]} />);
            const cks = queryAllByRole("checkbox");
            const ccks = cks.filter((ck) => (ck as HTMLInputElement).checked);
            expect(ccks).toHaveLength(2);
        });
        it("selects the checkbox when the line is selected", async () => {
            const { getByText } = render(<Selector lov={lov} multiple={true} value="id2" />);
            const elt = getByText("Item 2");
            const ck = elt.parentElement?.parentElement?.querySelector('input[type="checkbox"]') as HTMLInputElement;
            expect(ck).toBeDefined();
            expect(ck.checked).toBe(true);
        });
        it("dispatch a well formed message for multiple", async () => {
            const dispatch = jest.fn();
            const state: TaipyState = INITIAL_STATE;
            const { getByText } = render(
                <TaipyContext.Provider value={{ state, dispatch }}>
                    <Selector lov={lov} tp_varname="varname" multiple={true} />
                </TaipyContext.Provider>
            );
            const elt = getByText("Item 1");
            userEvent.click(elt);
            const elt2 = getByText("Item 2");
            userEvent.click(elt2);
            const elt3 = getByText("Item 3");
            userEvent.click(elt3);
            userEvent.click(elt2);
            expect(dispatch).toHaveBeenLastCalledWith({
                name: "varname",
                payload: { value: ["id1", "id3"] },
                propagate: true,
                type: "SEND_UPDATE_ACTION",
            });
        });
    });
    describe("Selector Component with filter", () => {
        //filter
        it("displays an input when filter", async () => {
            const { getByPlaceholderText } = render(<Selector lov={lov} filter={true} />);
            getByPlaceholderText("Search field");
        });
        it("does not display an input when filter is off", async () => {
            const { queryAllByPlaceholderText } = render(<Selector lov={lov} filter={false} />);
            expect(queryAllByPlaceholderText("Search field")).toHaveLength(0);
        });
        it("filters items by name", async () => {
            const { getByPlaceholderText, queryAllByText } = render(<Selector lov={lov} filter={true} />);
            expect(queryAllByText(/Item /)).toHaveLength(4);
            const search = getByPlaceholderText("Search field");
            userEvent.type(search, "m 3");
            expect(queryAllByText(/Item /)).toHaveLength(1);
            userEvent.clear(search);
            expect(queryAllByText(/Item /)).toHaveLength(4);
        });
    });
    describe("Selector Component with dropdown", () => {
        //dropdown
        it("displays as an empty control with arrow", async () => {
            const { getByTestId } = render(<Selector lov={lov} dropdown={true} />);
            getByTestId("ArrowDropDownIcon");
        });
        it("displays as an simple input with default value", async () => {
            const { getByText, getByTestId, queryAllByTestId } = render(<Selector lov={lov} defaultValue="id1" dropdown={true} />);
            getByText("Item 1");
            expect(queryAllByTestId("CancelIcon")).toHaveLength(0);
            getByTestId("ArrowDropDownIcon");
        });
        it("displays a delete icon when multiple", async () => {
            const { getByTestId } = render(<Selector lov={lov} defaultValue="id1" dropdown={true} multiple={true} />);
            getByTestId("CancelIcon");
        });
        it("opens a dropdown on click", async () => {
            const { getByText, getByRole, getByTestId, queryAllByRole } = render(<Selector lov={lov} dropdown={true} />);
            const butElt = getByRole("button");
            userEvent.click(butElt);
            getByRole("listbox");
            const elt = getByText("Item 2");
            userEvent.click(elt);
            expect(queryAllByRole("listbox")).toHaveLength(0);
        });
    });
});
