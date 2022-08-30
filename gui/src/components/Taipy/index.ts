/*
 * Copyright 2022 Avaiga Private Limited
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
import { Route, Routes } from "react-router-dom";
import Button from "./Button";
import Chart from "./Chart";
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
import MainPage from "../pages/MainPage";
import MenuCtl from "./MenuCtl";
import NavBar from "./NavBar";
import NotFound404 from "../pages/NotFound404";
import PageContent from "../pages/PageContent";
import Pane from "./Pane";
import Part from "./Part";
import Selector from "./Selector";
import Slider from "./Slider";
import StatusList from "./StatusList";
import Table from "./Table";
import TaipyRendered from "../pages/TaipyRendered";
import Toggle from "./Toggle";
import TreeView from "./TreeView";

// Need some more fidling to get the type right ...
const taipyComponents: Record<string, ComponentType> = {
    a: Link as ComponentType,
    Button: Button as ComponentType,
    Chart: Chart as ComponentType,
    DateSelector: DateSelector as ComponentType,
    Dialog: Dialog as ComponentType,
    Expandable: Expandable,
    Field: Field as ComponentType,
    FileDownload: FileDownload as ComponentType,
    FileSelector: FileSelector as ComponentType,
    Image: Image as ComponentType,
    Indicator: Indicator as ComponentType,
    Input: Input as ComponentType,
    Layout: Layout,
    MenuCtl: MenuCtl as ComponentType,
    NavBar: NavBar as ComponentType,
    PageContent: PageContent,
    Pane: Pane,
    Part: Part,
    Selector: Selector as ComponentType,
    Slider: Slider as ComponentType,
    Status: StatusList as ComponentType,
    Table: Table as ComponentType,
    Toggle: Toggle as ComponentType,
    TreeView: TreeView as ComponentType,
};

const registeredComponents: Record<string, ComponentType> = {};

export const getRegisteredComponents = () => {
    if (registeredComponents.TreeView === undefined) {
        Object.keys(taipyComponents).forEach(name => registeredComponents[name] = taipyComponents[name]);
        if (window.taipyConfig?.extensions) {
            Object.keys(window.taipyConfig.extensions).forEach(libName => {
                if (window.taipyConfig.extensions[libName]) {
                    const libParts = libName.split("/");
                    const modName = libParts.length > 2 ? libParts[2] : libName;
                    const mod: Record<string, (s: string) => Record<string, ComponentType>> = window[modName] as Record<string, (s: string) => Record<string, ComponentType>>;
                    if (mod) {
                        const fn = mod[window.taipyConfig.extensions[libName]];
                        if (fn) {
                            try {
                                const comps = fn(modName);
                                Object.keys(comps).forEach(name => registeredComponents[name] = comps[name]);
                            } catch (e) {
                                console.error("module '", modName, "'.'", window.taipyConfig.extensions[libName], "' error: ", e);
                            }
                        } else {
                            console.error("module '", modName, "' doesn't export function '", window.taipyConfig.extensions[libName], "'");
                        }
                    }
                }
            });
        }
    }
    return registeredComponents;
};

// for JSXParser in app.tsx (cant get redirect as componentType, will need more digging)
export const JSXReactRouterComponents: Record<string, unknown> = {
    Routes: Routes,
    Route: Route,
    NotFound404: NotFound404,
    TaipyRendered: TaipyRendered,
    MainPage: MainPage,
};
