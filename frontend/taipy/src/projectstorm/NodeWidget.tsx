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

import React, { useCallback } from "react";
import styled from "@emotion/styled";
import { DefaultPortModel, PortWidget } from "@projectstorm/react-diagrams";
import { DiagramEngine } from "@projectstorm/react-diagrams-core";

import { DataNode, Task, Sequence } from "../utils/names";
import { Datanode as DIcon, Task as TIcon, Sequence as PIcon, Scenario as SIcon } from "../icons";
import { TaipyNodeModel } from "./models";
import { IN_PORT_NAME } from "../utils/diagram";
import { Input, Output } from "../icons";
import { TaskStatus } from "../utils/types";

// eslint-disable-next-line @typescript-eslint/no-namespace
namespace S {
    export const Node = styled.div<{ background?: string; selected?: boolean, $status?: TaskStatus }>`
        background-color: ${(p) => p.background};
        border-radius: 5px;
        color: white;
        border: solid 2px black;
        overflow: visible;
        border: solid 2px ${(p) => (p.selected ? "rgb(0,192,255)" : getStatusColor(p.$status))};
    `;
    export const Title = styled.div`
        background: rgba(0, 0, 0, 0.3);
        display: flex;
        white-space: nowrap;
        justify-items: center;
    `;

    export const TitleName = styled.div`
        flex-grow: 1;
        padding: 5px 5px;
    `;

    export const SubTitleName = styled.span`
        font-size: smaller;
        padding-left: 0.7em;
    `;

    export const TitleIcon = styled.div`
        padding: 5px 0 5px 5px;
    `;

    export const Ports = styled.div`
        display: flex;
        background-image: linear-gradient(rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.2));
    `;

    export const PortsContainer = styled.div`
        flex-grow: 1;
        display: flex;
        flex-direction: column;
    `;

    export const OutPortLabel = styled.div`
        display: flex;
        align-items: end;
        justify-content: end;
        & svg {
            display: block;
        }
    `;

    export const InPortLabel = styled.div`
        display: flex;
        align-items: end;
        & svg {
            display: block;
        }
    `;
}

interface NodeProps {
    node: TaipyNodeModel;
    engine: DiagramEngine;
}

const getStatusLabel = (status?: TaskStatus) => status == TaskStatus.Running ? "Running" : status == TaskStatus.Pending ? "Pending" : undefined
const getStatusColor = (status?: TaskStatus) => status == TaskStatus.Running ? "rgb(0,163,108)" : status == TaskStatus.Pending ? "rgb(255,165,0)" : "black"

const NodeWidget = ({ node, engine }: NodeProps) => {
    const generatePort = useCallback(
        (port: DefaultPortModel) =>
            port.getName() == IN_PORT_NAME ? (
                <S.InPortLabel key="inlabel">
                    <PortWidget engine={engine} port={port} key={port.getID()}>
                        <Input />
                    </PortWidget>
                </S.InPortLabel>
            ) : (
                <S.OutPortLabel key="outlabel">
                    <PortWidget engine={engine} port={port} key={port.getID()}>
                        <Output />
                    </PortWidget>
                </S.OutPortLabel>
            ),
        [engine]
    );

    return (
        <S.Node
            data-default-node-name={node.getOptions().name}
            selected={node.isSelected()}
            background={node.getOptions().color}
            title={getStatusLabel(node.status)}
            $status={node.status}
        >
            <S.Title>
                <S.TitleIcon className="icon" title={node.getType()}>
                    {node.getType() == DataNode ? (
                        <DIcon />
                    ) : node.getType() == Task ? (
                        <TIcon />
                    ) : node.getType() == Sequence ? (
                        <PIcon />
                    ) : (
                        <SIcon />
                    )}
                </S.TitleIcon>
                <S.TitleName>
                    {node.getOptions().name}
                    {node.subtype ? <S.SubTitleName>{node.subtype}</S.SubTitleName> : null}
                </S.TitleName>
            </S.Title>
            <S.Ports>
                <S.PortsContainer>{node.getInPorts().map(generatePort)}</S.PortsContainer>
                <S.PortsContainer>{node.getOutPorts().map(generatePort)}</S.PortsContainer>
            </S.Ports>
        </S.Node>
    );
};

export default NodeWidget;
