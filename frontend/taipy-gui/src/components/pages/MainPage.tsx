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

import React, { useContext, useEffect } from "react";
import { useNavigate, useLocation } from "react-router";

import TaipyRendered from "./TaipyRendered";
import { TaipyContext } from "../../context/taipyContext";

interface MainPageProps {
    path: string;
    route?: string;
}

const MainPage = (props: MainPageProps) => {
    const { config } = useContext(TaipyContext);
    const navigate = useNavigate();
    const location = useLocation();
    const baseUrl = config?.baseURL || "/";

    useEffect(() => {
        if (props.route && baseUrl.includes(location.pathname)) {
           navigate(props.route.substring(1));
        }
    }, [location.pathname, navigate, props.route, baseUrl]);

    return <TaipyRendered path={props.path} />;
};

export default MainPage;
