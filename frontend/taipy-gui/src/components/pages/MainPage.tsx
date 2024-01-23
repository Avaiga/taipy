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

import React, { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

import TaipyRendered from "./TaipyRendered";
import { getBaseURL } from "../../utils";

interface MainPageProps {
    path: string;
    route?: string;
}

const MainPage = (props: MainPageProps) => {
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        if (props.route && getBaseURL().includes(location.pathname)) {
           navigate(props.route.substring(1));
        }
    }, [location.pathname, navigate, props.route]);

    return <TaipyRendered path={props.path} />;
};

export default MainPage;
