import React from "react";
import {render} from "@testing-library/react";
import "@testing-library/jest-dom";

import Expandable from './Expandable';

describe("Expandable Component", () => {
    it("renders", async () => {
        const {getByText} = render(<Expandable value="foo" >bar</Expandable>);
        const elt = getByText("foo");
        expect(elt.tagName).toBe("DIV");
    })
    it("displays the right info for string", async () => {
        const {getByText} = render(<Expandable value="foo" defaultValue="bar" className="taipy-expandable">bar</Expandable>);
        const elt = getByText("foo");
        expect(elt.parentElement?.parentElement).toHaveClass("taipy-expandable");
    })
    it("displays the default value", async () => {
        const {getByText} = render(<Expandable defaultValue="bar" value={undefined as unknown as string} >foobar</Expandable>);
        getByText("bar");
    })
    it("is disabled", async () => {
        const { getByRole } = render(<Expandable value="foo" active={false} >bar</Expandable>);
        const elt = getByRole("button");
        expect(elt).toHaveClass("Mui-disabled");
    });
    it("is enabled by default", async () => {
        const { getByRole } = render(<Expandable value="foo" >bar</Expandable>);
        const elt = getByRole("button");
        expect(elt).not.toHaveClass("Mui-disabled");
    });
    it("is enabled by active", async () => {
        const { getByRole } = render(<Expandable value="foo" active={true} >bar</Expandable>);
        const elt = getByRole("button");
        expect(elt).not.toHaveClass("Mui-disabled");
    });
    it("is collapsed", async () => {
        const { queryAllByText, getByText } = render(<Expandable value="foo" expanded={false} >bar</Expandable>);
        const elt = getByText("bar");
        const div = elt.closest("div.MuiCollapse-root");
        expect(div).toBeInTheDocument();
        expect(div).toHaveClass("MuiCollapse-hidden");
        expect(div).toHaveStyle({height: '0px'});
    });
    it("is not collapsed by default", async () => {
        const { queryAllByText, getByText } = render(<Expandable value="foo" >bar</Expandable>);
        const elt = getByText("bar");
        const div = elt.closest("div.MuiCollapse-root");
        expect(div).toBeInTheDocument();
        expect(div).not.toHaveClass("MuiCollapse-hidden");
        expect(div).not.toHaveStyle({height: '0px'});
    });
    it("is not collapsed by dexpandedefault", async () => {
        const { queryAllByText, getByText } = render(<Expandable value="foo" expanded={true} >bar</Expandable>);
        const elt = getByText("bar");
        const div = elt.closest("div.MuiCollapse-root");
        expect(div).toBeInTheDocument();
        expect(div).not.toHaveClass("MuiCollapse-hidden");
        expect(div).not.toHaveStyle({height: '0px'});
    });
});
