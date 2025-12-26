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
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

import ScenarioSelector from "./ScenarioSelector";
import { NodeType } from "./utils/types";

// Mock the CoreSelector component
jest.mock("./CoreSelector", () => {
    return function MockCoreSelector(props: any) {
        return (
            <div data-testid="core-selector">
                {props.editComponent ? (
                    <div data-testid="edit-component">Edit Component Present</div>
                ) : (
                    <div data-testid="no-edit-component">No Edit Component</div>
                )}
            </div>
        );
    };
});

// Mock other dependencies
jest.mock("taipy-gui", () => ({
    useClassNames: () => "mock-class",
    useDispatch: () => jest.fn(),
    useModule: () => "mock-module",
    useDynamicProperty: (prop: any, defaultProp: any, defaultValue: any) => defaultValue,
}));

const mockProps = {
    id: "test-scenario-selector",
    onScenarioCrud: "mock-crud",
    onScenarioSelect: "mock-select",
    height: "50vh",
    innerScenarios: [],
    configs: [],
    libClassName: "mock-lib-class",
    dynamicClassName: "mock-dynamic-class",
    className: "mock-class",
    active: true,
    defaultActive: true,
};

describe("ScenarioSelector Editable Property", () => {
    it("should render edit component when editable is true (default)", () => {
        render(<ScenarioSelector {...mockProps} />);
        
        expect(screen.getByTestId("edit-component")).toBeInTheDocument();
        expect(screen.queryByTestId("no-edit-component")).not.toBeInTheDocument();
    });

    it("should render edit component when editable is explicitly true", () => {
        render(<ScenarioSelector {...mockProps} editable={true} />);
        
        expect(screen.getByTestId("edit-component")).toBeInTheDocument();
        expect(screen.queryByTestId("no-edit-component")).not.toBeInTheDocument();
    });

    it("should not render edit component when editable is false", () => {
        render(<ScenarioSelector {...mockProps} editable={false} />);
        
        expect(screen.getByTestId("no-edit-component")).toBeInTheDocument();
        expect(screen.queryByTestId("edit-component")).not.toBeInTheDocument();
    });

    it("should still render add button when editable is false", () => {
        render(<ScenarioSelector {...mockProps} editable={false} showAddButton={true} />);
        
        // The add button should still be present
        expect(screen.getByText("Add scenario")).toBeInTheDocument();
    });

    it("should maintain backward compatibility when editable prop is not provided", () => {
        const propsWithoutEditable = { ...mockProps };
        delete (propsWithoutEditable as any).editable;
        
        render(<ScenarioSelector {...propsWithoutEditable} />);
        
        // Should default to editable=true, so edit component should be present
        expect(screen.getByTestId("edit-component")).toBeInTheDocument();
    });

    it("should pass all other props correctly regardless of editable value", () => {
        const { rerender } = render(<ScenarioSelector {...mockProps} editable={true} />);
        
        expect(screen.getByTestId("core-selector")).toBeInTheDocument();
        
        rerender(<ScenarioSelector {...mockProps} editable={false} />);
        
        expect(screen.getByTestId("core-selector")).toBeInTheDocument();
    });
});