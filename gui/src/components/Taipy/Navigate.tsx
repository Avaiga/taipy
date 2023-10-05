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
import { useLocation, useNavigate } from "react-router-dom";
import { TaipyContext } from "../../context/taipyContext";
import { createNavigateAction } from "../../context/taipyReducers";

interface NavigateProps {
    to?: string;
    params?: Record<string, string>;
    tab?: string;
    force?: boolean;
}

const Navigate = ({ to, params, tab, force }: NavigateProps) => {
    const { dispatch, state } = useContext(TaipyContext);
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        if (to) {
            const tos = to === "/" ? to : "/" + to;
            const searchParams = new URLSearchParams(params);
            if (Object.keys(state.locations || {}).some((route) => tos === route)) {
                const searchParamsLocation = new URLSearchParams(location.search);
                if (force && location.pathname === tos && searchParamsLocation.toString() === searchParams.toString()) {
                    navigate(0);
                } else {
                    navigate({ pathname: to, search: `?${searchParams.toString()}` });
                }
            } else {
                window.open(`${to}?${searchParams.toString()}`, tab || "_blank")?.focus();
            }
            dispatch(createNavigateAction());
        }
        // we surely don't want to depend on location.pathname, and location.search!
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [to, tab, force, state.locations, dispatch, navigate, params]);

    return null;
};

export default Navigate;
