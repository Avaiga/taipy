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
import axios from "axios";
import { useLocation, useNavigate } from "react-router-dom";

import { TaipyContext } from "../../context/taipyContext";
import { createNavigateAction } from "../../context/taipyReducers";
import { getBaseURL } from "../../utils";

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
    const SPECIAL_PARAMS = ["tp_reload_all", "tp_reload_same_route_only", "tprh"];

    useEffect(() => {
        if (to) {
            const tos = to === "/" ? to : "/" + to;
            const navigatePath = getBaseURL() + tos.slice(1)
            const filteredParams = params
                ? Object.keys(params).reduce((acc, key) => {
                      if (!SPECIAL_PARAMS.includes(key)) {
                          acc[key] = params[key];
                      }
                      return acc;
                  }, {} as Record<string, string>)
                : {};
            const searchParams = new URLSearchParams(filteredParams);
            // Special case for notebook reload
            const reloadAll = params?.tp_reload_all === "true";
            const reloadSameRouteOnly = params?.tp_reload_same_route_only === "true";
            if (reloadAll) {
                return navigate(0);
            }
            if (reloadSameRouteOnly) {
                if (location.pathname === tos) {
                    navigate(0);
                }
                return;
            }
            // Regular navigate cases
            if (Object.keys(state.locations || {}).some((route) => tos === route)) {
                const searchParamsLocation = new URLSearchParams(location.search);
                if (force && location.pathname === navigatePath  && searchParamsLocation.toString() === searchParams.toString()) {
                    navigate(0);
                } else {
                    navigate({ pathname: navigatePath, search: `?${searchParams.toString()}` });
                    // Handle Resource Handler Id
                    const tprh = params?.tprh;
                    if (tprh !== undefined) {
                        axios.post(`taipy-rh`, { tprh, is_secure: window.location.protocol.includes("https") }).then(() => {
                            localStorage.setItem("tprh", tprh);
                            navigate(0);
                        }).catch((error) => {
                            console.error(
                                "Cannot resolve resource handler. Route `/taipy-rh` might be missing.",
                                error,
                            );
                        });
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
