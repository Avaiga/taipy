import { ComponentType } from "react";
import { Route, Routes } from "react-router-dom";
import Button from "./Button";
import Chart from "./Chart";
import DateSelector from "./DateSelector";
import Dialog from "./Dialog";
import Expandable from "./Expandable";
import Field from "./Field";
import Image from "./Image";
import Input from "./Input";
import Layout from "./Layout";
import Link from "./Link";
import MainPage from "../pages/MainPage";
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
export const taipyComponents: Record<string, ComponentType> = {
    a: Link as ComponentType,
    Button: Button as ComponentType,
    Chart: Chart as ComponentType,
    DateSelector: DateSelector as ComponentType,
    Dialog: Dialog as ComponentType,
    Expandable: Expandable,
    Field: Field as ComponentType,
    Image: Image as ComponentType,
    Input: Input as ComponentType,
    Layout: Layout,
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

// for JSXParser in app.tsx (cant get redirect as componentType, will need more digging)
export const JSXReactRouterComponents: Record<string, unknown> = {
    Routes: Routes,
    Route: Route,
    NotFound404: NotFound404,
    TaipyRendered: TaipyRendered,
    MainPage: MainPage,
};
