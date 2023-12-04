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

import { ComponentType } from "react";
import Button from "./Button";
import Chart from "./Chart";
import DateRange from "./DateRange";
import DateSelector from "./DateSelector";
import Dialog from "./Dialog";
import Expandable from "./Expandable";
import Field from "./Field";
import FileDownload from "./FileDownload";
import FileSelector from "./FileSelector";
import Image from "./Image";
import Indicator from "./Indicator";
import Input from "./Input";
import Layout from "./Layout";
import Link from "./Link";
import MenuCtl from "./MenuCtl";
import NavBar from "./NavBar";
import PageContent from "../pages/PageContent";
import Pane from "./Pane";
import Part from "./Part";
import Selector from "./Selector";
import Slider from "./Slider";
import StatusList from "./StatusList";
import Table from "./Table";
import Toggle from "./Toggle";
import TreeView from "./TreeView";

const registeredComponents: Record<string, ComponentType> = {};

export const getRegisteredComponents = () => {
    if (registeredComponents.TreeView === undefined) {
        Object.entries({
            a: Link,
            Button: Button,
            Chart: Chart,
            DateRange: DateRange,
            DateSelector: DateSelector,
            Dialog: Dialog,
            Expandable: Expandable,
            Field: Field,
            FileDownload: FileDownload,
            FileSelector: FileSelector,
            Image: Image,
            Indicator: Indicator,
            Input: Input,
            Layout: Layout,
            MenuCtl: MenuCtl,
            NavBar: NavBar,
            PageContent: PageContent,
            Pane: Pane,
            Part: Part,
            Selector: Selector,
            Slider: Slider,
            Status: StatusList,
            Table: Table,
            Toggle: Toggle,
            TreeView: TreeView,
        }).forEach(([name, comp]) => (registeredComponents[name] = comp  as ComponentType));
        if (window.taipyConfig?.extensions) {
            Object.entries(window.taipyConfig.extensions).forEach(([libName, elts]) => {
                if (elts && elts.length) {
                    const libParts = libName.split("/");
                    const modName = libParts.length > 2 ? libParts[2] : libName;
                    const mod: Record<string, ComponentType> = window[modName] as Record<string, ComponentType>;
                    if (mod) {
                        elts.forEach((elt) => {
                            const comp = mod[elt];
                            if (comp) {
                                registeredComponents[modName + "_" + elt] = comp;
                            } else {
                                console.error("module '", modName, "' doesn't export component '", elt, "'");
                            }
                        });
                    } else {
                        console.error("module '", modName, "' cannot be loaded.");
                    }
                }
            });
        }
    }
    return registeredComponents;
};
