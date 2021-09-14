import { ComponentType } from "react";
import { BrowserRouter as Router, Route, Switch, Redirect, Link } from "react-router-dom";
import Input from "./Input";
import Field from "./Field";
import DateSelector from "./DateSelector";
import Table from "./Table";
import TaipyRendered from "../pages/TaipyRendered";
import NotFound404 from "../pages/NotFound404";

// Need some more fidling to get the type right ...
export const taipyComponents: Record<string, ComponentType> = {
    Input: Input as ComponentType,
    Field: Field as ComponentType,
    DateSelector: DateSelector as ComponentType,
    Table: Table as ComponentType,
    Link: Link as ComponentType,
};

// for JSXParser in app.tsx (cant get redirect as componentType, will need more digging)
export const JSXReactRouterComponents: Record<string, any> = {
    Switch: Switch as ComponentType,
    Route: Route as ComponentType,
    Router: Router as ComponentType,
    Redirect: Redirect,
};

// for JSXParser in app.tsx
export const JSXRouterBindings: Record<string, ComponentType> = {
    NotFound404: NotFound404 as ComponentType,
    TaipyRendered: TaipyRendered as ComponentType,
};
