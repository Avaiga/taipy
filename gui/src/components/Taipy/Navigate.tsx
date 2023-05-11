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

import { useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { TaipyContext } from "../../context/taipyContext";
import { createNavigateAction } from "../../context/taipyReducers";

interface NavigateProps {
    to?: string;
    tab?: string;
}

const Navigate = ({ to, tab }: NavigateProps) => {
    const { dispatch, state } = useContext(TaipyContext);
    const navigate = useNavigate();

    useEffect(() => {
        if (to) {
            const tos = "/" + to;
            if (Object.keys(state.locations || {}).some((route) => tos === route)) {
                navigate(tos.substring(1));
            } else {
                window.open(to, tab || "_blank")?.focus();
            }
            dispatch(createNavigateAction());
        }
    }, [to, tab, state.locations, dispatch, navigate]);

    return null;
};

export default Navigate;
