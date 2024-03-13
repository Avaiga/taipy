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
            const searchParams = new URLSearchParams(params || "");
            // Handle Resource Handler Id
            let tprh: string | null = null;
            let meta: string | null = null;
            if (searchParams.has("tprh")) {
                tprh = searchParams.get("tprh");
                searchParams.delete("tprh");
                if (searchParams.has("tp_cp_meta")) {
                    meta = searchParams.get("tp_cp_meta");
                    searchParams.delete("tp_cp_meta");
                }
            }
            if (Object.keys(state.locations || {}).some((route) => tos === route)) {
                const searchParamsLocation = new URLSearchParams(location.search);
                if (force && location.pathname === tos && searchParamsLocation.toString() === searchParams.toString()) {
                    navigate(0);
                } else {
                    navigate({ pathname: to, search: `?${searchParams.toString()}` });
                    if (tprh !== null) {
                        // Add a session cookie for the resource handler id
                        document.cookie = `tprh=${tprh};path=/;`;
                        if (meta !== null) {
                            localStorage.setItem("tp_cp_meta", meta);
                        }
                        navigate(0);
                    }
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
