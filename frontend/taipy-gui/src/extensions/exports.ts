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

import Router from "../components/Router";
import Chart from "../components/Taipy/Chart";
import Dialog from "../components/Taipy/Dialog";
import FileSelector from "../components/Taipy/FileSelector";
import Login from "../components/Taipy/Login";
import Table from "../components/Taipy/Table";
import TableFilter, { FilterColumnDesc } from "../components/Taipy/TableFilter";
import { FilterDesc } from "../components/Taipy/tableUtils";
import TableSort, { SortColumnDesc, SortDesc } from "../components/Taipy/TableSort";
import { getComponentClassName } from "../components/Taipy/TaipyStyle";
import Metric from "../components/Taipy/Metric";
import { useLovListMemo, LoV, LoVElt } from "../components/Taipy/lovUtils";
import { LovItem } from "../utils/lov";
import { getUpdateVar, getSuffixedClassNames } from "../components/Taipy/utils";
import { ColumnDesc, RowType, RowValue } from "../components/Taipy/tableUtils";
import { TaipyContext, TaipyStore, PageContext } from "../context/taipyContext";
import { TaipyBaseAction, TaipyState } from "../context/taipyReducers";
import { useActions, useRequestUpdateOnFirstRender } from "../hooks";
import { TaipyConfig, ExtensionConfig } from "../utils";
import {
    useClassNames,
    useDispatchRequestUpdateOnFirstRender,
    useDispatch,
    useDynamicDictProperty,
    useDynamicProperty,
    useModule,
} from "../utils/hooks";
import {
    createSendActionNameAction,
    createSendUpdateAction,
    createRequestDataUpdateAction,
    createRequestUpdateAction,
} from "../context/taipyReducers";

export {
    Router,
    Chart,
    Dialog,
    FileSelector,
    Login,
    Table,
    TableFilter,
    TableSort,
    Metric,
    TaipyContext as Context,
    createRequestDataUpdateAction,
    createRequestUpdateAction,
    createSendActionNameAction,
    createSendUpdateAction,
    getComponentClassName,
    getSuffixedClassNames,
    getUpdateVar,
    useActions,
    useClassNames,
    useDispatchRequestUpdateOnFirstRender,
    useDispatch,
    useDynamicDictProperty,
    useDynamicProperty,
    useLovListMemo,
    useModule,
    useRequestUpdateOnFirstRender,
};

export type {
    ColumnDesc,
    FilterColumnDesc,
    FilterDesc,
    LoV,
    LoVElt,
    LovItem,
    RowType,
    RowValue,
    SortColumnDesc,
    SortDesc,
    TaipyStore as Store,
    TaipyState as State,
    TaipyBaseAction as Action,
    TaipyConfig,
    ExtensionConfig,
};

// For Taipy Custom Package (Designer)

import { sendWsMessage, TAIPY_CLIENT_ID } from "../context/wsUtils";
import { uploadFile } from "../workers/fileupload";
import { WsMessage, WsMessageType } from "../context/wsUtils";
import { IdMessage, storeClientId, getLocalStorageValue } from "../context/utils";

import ErrorFallback from "../utils/ErrorBoundary";
import { getRegisteredComponents } from "../components/Taipy/components";
import { renderError, unregisteredRender } from "../components/Taipy/Unregistered";
import {
    createRefreshThemesAction,
    INITIAL_STATE,
    initializeWebSocket,
    taipyInitialize,
    taipyReducer,
} from "../context/taipyReducers";

export {
    getLocalStorageValue,
    sendWsMessage,
    TAIPY_CLIENT_ID,
    uploadFile,
    storeClientId,
    PageContext,
    TaipyContext,
    ErrorFallback,
    getRegisteredComponents,
    renderError,
    unregisteredRender,
    createRefreshThemesAction,
    INITIAL_STATE,
    initializeWebSocket,
    taipyInitialize,
    taipyReducer,
};
export type { WsMessage, WsMessageType, IdMessage };
