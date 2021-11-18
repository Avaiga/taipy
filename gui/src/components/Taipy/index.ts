import { ComponentType } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Input from "./Input";
import Field from "./Field";
import DateSelector from "./DateSelector";
import Table from "./Table";
import TaipyRendered from "../pages/TaipyRendered";
import NotFound404 from "../pages/NotFound404";
import Link from "./Link";
import Selector from "./Selector";
import Dialog from "./Dialog";
import Chart from "./Chart";
import StatusList from "./StatusList";
import Toggle from "./Toggle";
import Slider from "./Slider";
import Button from "./Button";
import Layout from "./Layout";
import NavBar from "./NavBar";
import Part from "./Part";
import MainPage from "../pages/MainPage";
import PageContent from "../pages/PageContent";
import Expandable from "./Expandable";

// Need some more fidling to get the type right ...
export const taipyComponents: Record<string, ComponentType> = {
    Input: Input as ComponentType,
    Field: Field as ComponentType,
    DateSelector: DateSelector as ComponentType,
    Table: Table as ComponentType,
    a: Link as ComponentType,
    Selector: Selector as ComponentType,
    Dialog: Dialog as ComponentType,
    Chart: Chart as ComponentType,
    Status: StatusList as ComponentType,
    Toggle: Toggle as ComponentType,
    Slider: Slider as ComponentType,
    Button: Button as ComponentType,
    NavBar: NavBar as ComponentType,
    PageContent: PageContent,
    Layout: Layout,
    Part: Part,
    Expandable: Expandable,
};

// for JSXParser in app.tsx (cant get redirect as componentType, will need more digging)
export const JSXReactRouterComponents: Record<string, unknown> = {
    Routes: Routes,
    Route: Route,
    Router: BrowserRouter,
    NotFound404: NotFound404,
    TaipyRendered: TaipyRendered,
    MainPage: MainPage,
};
