import { ComponentType } from "react";
import { BrowserRouter as Router, Route, Switch, Redirect } from "react-router-dom";
import Input from "./Input";
import Field from "./Field";
import DateSelector from "./DateSelector";
import Table from "./Table";
import TaipyRendered from "../pages/TaipyRendered";
import NotFound404 from "../pages/NotFound404";
import Link from "./Link";

// Need some more fidling to get the type right ...
export const taipyComponents: Record<string, ComponentType> = {
    Input: Input as ComponentType,
    Field: Field as ComponentType,
    DateSelector: DateSelector as ComponentType,
    Table: Table as ComponentType,
    a: Link as ComponentType,
};

// for JSXParser in app.tsx (cant get redirect as componentType, will need more digging)
export const JSXReactRouterComponents: Record<string, unknown> = {
    Switch: Switch,
    Route: Route,
    Router: Router,
    Redirect: Redirect,
    NotFound404: NotFound404,
    TaipyRendered: TaipyRendered,
};

