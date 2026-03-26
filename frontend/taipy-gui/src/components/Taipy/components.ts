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

import { ComponentType } from "react";

import Button from "./Button";
import Chat from "./Chat";
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
import Login from "./Login";
import Layout from "./Layout";
import Link from "./Link";
import MenuCtl from "./MenuCtl";
import Metric from "./Metric";
import NavBar from "./NavBar";
import PageContent from "../pages/PageContent";
import Pane from "./Pane";
import Part from "./Part";
import Progress from "./Progress";
import Selector from "./Selector";
import Slider from "./Slider";
import StatusList from "./StatusList";
import Table from "./Table";
import TaipyAlert from "./Alert";
import TaipyStyle from "./TaipyStyle";
import Toggle from "./Toggle";
import TimeSelector from "./TimeSelector";
import TreeView from "./TreeView";
import { ExtensionConfig } from "../../utils";

const registeredComponents: Record<string, ComponentType<object>> = {};

export const getRegisteredComponents = (extensions?: Record<string, ExtensionConfig>) => {
    if (registeredComponents.TreeView === undefined) {
        Object.entries({
            a: Link,
            Alert: TaipyAlert,
            Button,
            Chat,
            Chart,
            DateRange,
            DateSelector,
            Dialog,
            Expandable,
            Field,
            FileDownload,
            FileSelector,
            Image,
            Indicator,
            Input,
            Login,
            Layout,
            MenuCtl,
            Metric,
            NavBar,
            PageContent,
            Pane,
            Part,
            Selector,
            Slider,
            Status: StatusList,
            Table,
            TaipyStyle,
            TimeSelector,
            Toggle,
            TreeView,
            Progress,
        }).forEach(([name, comp]) => (registeredComponents[name] = comp as ComponentType));
    }
    if (extensions) {
        Object.entries(extensions).forEach(([libName, description]) => {
            if (libName) {
                if (description.loaded && description.components && description.components.length) {
                    if (registeredComponents[libName + "_" + description.components[0]] === undefined) {
                        const mod: Record<string, ComponentType> = window[libName] as Record<string, ComponentType>;
                        if (mod) {
                            description.components.forEach((elt) => {
                                const comp = mod[elt];
                                if (comp) {
                                    registeredComponents[libName + "_" + elt] = comp;
                                } else {
                                    console.error("module '", libName, "' doesn't export component '", elt, "'");
                                }
                            });
                            console.debug("module '", libName, "' is loaded.");
                        } else {
                            console.debug("module '", libName, "' cannot be loaded yet.");
                        }
                    }
                } else if (!description.loaded) {
                    console.debug(
                        "extension library'",
                        libName,
                        "' is not loaded yet, components won't be registered until its script(s) are loaded.",
                    );
                }
            }
        });
    }

    return registeredComponents as Record<string, ComponentType<unknown>>;
};
