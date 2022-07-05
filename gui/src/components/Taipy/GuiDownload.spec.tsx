import React from "react";
import { render, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";

import GuiDownload from "./GuiDownload";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";

describe("GuiDownload Component", () => {
    it("renders with nothing", async () => {
        render(<GuiDownload />);
        const elt = document.getElementById("Gui-download-file");
        expect(elt).toBeInTheDocument();
        expect(elt?.tagName).toBe("A");
        expect((elt as HTMLAnchorElement)?.href).toBe("");
    });
    it("renders with link", async () => {
        render(<GuiDownload download={{ content: "/some/link/to.png" }} />);
        const elt = document.getElementById("Gui-download-file");
        expect(elt).toBeInTheDocument();
        expect(elt?.tagName).toBe("A");
        expect((elt as HTMLAnchorElement)?.href).toBe("http://localhost/some/link/to.png");
        expect((elt as HTMLAnchorElement)?.download).toBe("");
    });
    it("renders with link and name", async () => {
        render(<GuiDownload download={{ content: "/some/link/to.png", name: "from.png" }} />);
        const elt = document.getElementById("Gui-download-file");
        expect(elt).toBeInTheDocument();
        expect(elt?.tagName).toBe("A");
        expect((elt as HTMLAnchorElement)?.download).toBe("from.png");
    });
    it("emits a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <GuiDownload download={{ content: "/some/link/to.png", name: "from.png", onAction: "onActionMsg" }} />
            </TaipyContext.Provider>
        );
        const elt = document.getElementById("Gui-download-file");
        expect(elt).toBeInTheDocument();
        expect(elt?.tagName).toBe("A");
        expect((elt as HTMLAnchorElement)?.download).toBe("from.png");
        await waitFor(() =>
            expect(dispatch).toHaveBeenCalledWith({
                name: "Gui.download",
                payload: { args: ["/some/link/to.png"], action: "onActionMsg" },
                type: "SEND_ACTION_ACTION",
            })
        );
    });
});
