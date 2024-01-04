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
import { AbstractReactFactory, GenerateWidgetEvent, AbstractModelFactory } from "@projectstorm/react-canvas-core";
import { DiagramEngine } from "@projectstorm/react-diagrams-core";
import { TaipyNodeModel, TaipyPortModel } from "./models";
import NodeWidget from "./NodeWidget";

export class TaipyNodeFactory extends AbstractReactFactory<TaipyNodeModel, DiagramEngine> {
    constructor(nodeType: string) {
        super(nodeType);
    }

    generateReactWidget(event: GenerateWidgetEvent<TaipyNodeModel>): JSX.Element {
        return <NodeWidget engine={this.engine} node={event.model} />;
    }

    generateModel(): TaipyNodeModel {
        return new TaipyNodeModel();
    }
}

export class TaipyPortFactory extends AbstractModelFactory<TaipyPortModel, DiagramEngine> {
    constructor() {
        super("taipy-port");
    }

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    generateModel(): TaipyPortModel {
        return new TaipyPortModel({ type: "taipy-port", name: "fred" });
    }
}
