import React from "react";
import { render } from "@testing-library/react";
import "@testing-library/jest-dom";
import TaipyAlert from "./Alert";

describe("TaipyAlert Component", () => {
    it("renders with default properties", () => {
        const { getByRole } = render(<TaipyAlert message="Default Alert" />);
        const alert = getByRole("alert");
        expect(alert).toBeInTheDocument();
        expect(alert).toHaveClass("MuiAlert-filledError");
    });

    it("applies the correct severity", () => {
        const { getByRole } = render(<TaipyAlert message="Warning Alert" severity="warning" />);
        const alert = getByRole("alert");
        expect(alert).toBeInTheDocument();
        expect(alert).toHaveClass("MuiAlert-filledWarning");
    });

    it("applies the correct variant", () => {
        const { getByRole } = render(<TaipyAlert message="Outlined Alert" variant="outlined" />);
        const alert = getByRole("alert");
        expect(alert).toBeInTheDocument();
        expect(alert).toHaveClass("MuiAlert-outlinedError");
    });

    it("does not render if render prop is false", () => {
        const { queryByRole } = render(<TaipyAlert message="Hidden Alert" render={false} />);
        const alert = queryByRole("alert");
        expect(alert).toBeNull();
    });

    it("handles dynamic class names", () => {
        const { getByRole } = render(<TaipyAlert message="Dynamic Alert" className="custom-class" />);
        const alert = getByRole("alert");
        expect(alert).toHaveClass("custom-class");
    });
});
