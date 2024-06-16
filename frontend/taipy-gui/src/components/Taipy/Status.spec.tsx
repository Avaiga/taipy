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
import {render} from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";
import { CheckCircle, Error, Warning, Info } from '@mui/icons-material';

import { PlusOneOutlined } from "@mui/icons-material";

import Status, { StatusType } from './Status';

const status: StatusType = {status: "status", message: "message"};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'S':
      return <CheckCircle data-testid="CheckCircleIcon" />;
    case 'E':
      return <Error data-testid="ErrorIcon" />;
    case 'W':
      return <Warning data-testid="WarningIcon" />;
    case 'I':
      return <Info data-testid="InfoIcon" />;
    default:
      return '❓';
  }
};


describe("Status Component", () => {
    it("renders", async () => {
        const {getByText} = render(<Status value={status} />);
        const elt = getByText("message");
        const av = getByText("S");
        expect(elt.tagName).toBe("SPAN");
        expect(av.tagName).toBe("DIV");
    })
    it("uses the class", async () => {
        const {getByText} = render(<Status value={status} className="taipy-status" />);
        const elt = getByText("message");
        expect(elt.parentElement).toHaveClass("taipy-status");
    })
    it("can be closed", async () => {
        const myClose = jest.fn();
        const {getByTestId} = render(<Status value={status} onClose={myClose} />);
        const elt = getByTestId("CancelIcon");
        await userEvent.click(elt);
        expect(myClose).toHaveBeenCalled();
    })
    it("displays the icon", async () => {
        const {getByTestId} = render(<Status value={status} icon={<PlusOneOutlined/>} onClose={jest.fn()} />);
        getByTestId("PlusOneOutlinedIcon");
    })
});

describe("StatusAvatar Icon Rendering", () => {
    it("renders the correct icon for 'S' status", () => {
        const { getByTestId } = render(getStatusIcon('S'));
        getByTestId("CheckCircleIcon");
    });

    it("renders the correct icon for 'E' status", () => {
        const { getByTestId } = render(getStatusIcon('E'));
        getByTestId("ErrorIcon");
    });

    it("renders the correct icon for 'W' status", () => {
        const { getByTestId } = render(getStatusIcon('W'));
        getByTestId("WarningIcon");
    });

    it("renders the correct icon for 'I' status", () => {
        const { getByTestId } = render(getStatusIcon('I'));
        getByTestId("InfoIcon");
    });

    it("renders the default emoji for unknown status", () => {
        const { getByText } = render(getStatusIcon('unknown'));
        getByText("❓");
    });
});
