/*
 * Copyright 2023 Avaiga Private Limited
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

import {
    DefaultLinkModel,
    DefaultNodeModel,
    DefaultPortModel,
    LinkModel,
    DefaultDiagramState,
    DiagramEngine,
    DagreEngine,
    PointModel,
} from "@projectstorm/react-diagrams";

import { getNodeColor } from "./config";
import { TaipyDiagramModel, TaipyNodeModel } from "../projectstorm/models";
import { TaipyNodeFactory, TaipyPortFactory } from "../projectstorm/factories";
import { nodeTypes } from "./config";
import { DisplayModel } from "./types";

export const createDagreEngine = () => new DagreEngine({
    graph: {
        rankdir: "LR",
        ranker: "longest-path",
        marginx: 25,
        marginy: 25,
    },
    includeLinks: false,
});

export const initDiagram = (engine: DiagramEngine)  => {
    nodeTypes.forEach((nodeType) => engine.getNodeFactories().registerFactory(new TaipyNodeFactory(nodeType)));
    engine.getPortFactories().registerFactory(new TaipyPortFactory());
    const state = engine.getStateMachine().getCurrentState();
    if (state instanceof DefaultDiagramState) {
        state.dragNewLink.config.allowLooseLinks = false;
    }
};

export const getModelLinks = (model: TaipyDiagramModel) => Object.values(model.getActiveLinkLayer().getLinks());

export const IN_PORT_NAME = "In";
export const OUT_PORT_NAME = "Out";

export const getLinkId = (link: LinkModel) =>
    `LINK.${getNodeId(link.getSourcePort().getNode() as DefaultNodeModel)}.${getNodeId(
        link.getTargetPort().getNode() as DefaultNodeModel
    )}`;
export const getNodeId = (node: DefaultNodeModel) => `${node.getType()}.${node.getID()}`;

export const createNode = (nodeType: string, id: string, name: string, subtype: string) =>
    new TaipyNodeModel({
        id: id,
        type: nodeType,
        name: name,
        color: getNodeColor(nodeType),
        subtype: subtype,
    });

export const createLink = (outPort: DefaultPortModel, inPort: DefaultPortModel) =>
    outPort.link<DefaultLinkModel>(inPort);

const isInLine = (pnt: PointModel, startLine: PointModel, endLine: PointModel) => {
    const L2 =
        (endLine.getX() - startLine.getX()) * (endLine.getX() - startLine.getX()) +
        (endLine.getY() - startLine.getY()) * (endLine.getY() - startLine.getY());
    if (L2 === 0) {
        return false;
    }
    const r =
        ((pnt.getX() - startLine.getX()) * (endLine.getX() - startLine.getX()) +
            (pnt.getY() - startLine.getY()) * (endLine.getY() - startLine.getY())) /
        L2;

    //Assume line thickness is circular
    if (0 <= r && r <= 1) {
        //On the line segment
        const s =
            ((startLine.getY() - pnt.getY()) * (endLine.getX() - startLine.getX()) -
                (startLine.getX() - pnt.getX()) * (endLine.getY() - startLine.getY())) /
            L2;
        return Math.abs(s) * Math.sqrt(L2) <= lineLeeway;
    }
    return false;
};

const lineLeeway = 0.1;

export const relayoutDiagram = (engine: DiagramEngine, dagreEngine: DagreEngine) => {
    const model = engine.getModel();
    dagreEngine.redistribute(model);
    //  engine.getLinkFactories().getFactory<PathFindingLinkFactory>(PathFindingLinkFactory.NAME).calculateRoutingMatrix();
    getModelLinks(model).forEach((l) => {
        const points = l.getPoints();
        if (points.length === 3) {
            // remove unnecessary intermediate if same level
            if (
                Math.abs(points[0].getX() - points[2].getX()) < lineLeeway ||
                Math.abs(points[0].getY() - points[2].getY()) < lineLeeway
            ) {
                points.splice(1, 1);
                l.setPoints(points);
            }
        } else if (points.length > 3) {
            const pointsToRemove = [] as number[];
            let startIdx = 0;
            while (startIdx + 2 < points.length) {
                if (isInLine(points[startIdx + 1], points[startIdx], points[startIdx + 2])) {
                    pointsToRemove.push(startIdx + 1);
                }
                startIdx++;
            }
            pointsToRemove.reverse().forEach((idx) => points.splice(idx, 1));
            l.setPoints(points);
        }
    });
    engine.repaintCanvas();
};

export const populateModel = (displayModel: DisplayModel, model: TaipyDiagramModel) => {
    const linkModels: DefaultLinkModel[] = [];
    const nodeModels: Record<string, Record<string, DefaultNodeModel>> = {};

    displayModel[1] &&
        Object.entries(displayModel[1]).forEach(([nodeType, n]) => {
            Object.entries(n).forEach(([id, detail]) => {
                const node = createNode(nodeType, id, detail.name, detail.type);
                nodeModels[nodeType] = nodeModels[nodeType] || {};
                nodeModels[nodeType][id] = node;
            });
        });

    Array.isArray(displayModel[2]) &&
        displayModel[2].forEach(([nodeType, nodeId, childType, childId]) => {
            const parentNode = nodeModels[nodeType] && nodeModels[nodeType][nodeId];
            const childNode = nodeModels[childType] && nodeModels[childType][childId];
            if (parentNode && childNode) {
                const link = createLink(
                    (parentNode.getPort(OUT_PORT_NAME) || parentNode.addOutPort(OUT_PORT_NAME)) as DefaultPortModel,
                    (childNode.getPort(IN_PORT_NAME) || childNode.addInPort(IN_PORT_NAME)) as DefaultPortModel
                );
                linkModels.push(link);
            }
        });

    const nodeLayer = model.getActiveNodeLayer();
    Object.values(nodeModels).forEach((nm) => Object.values(nm).forEach((n) => nodeLayer.addModel(n)));
    const linkLayer = model.getActiveLinkLayer();
    linkModels.forEach((l) => linkLayer.addModel(l));
};
