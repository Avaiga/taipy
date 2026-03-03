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

import React, { ReactNode, Suspense, lazy, useEffect, useMemo } from "react";

import {
    useClassNames,
    useDispatch,
    useDispatchRequestUpdateOnFirstRender,
    useDynamicProperty,
    useModule,
} from "taipy-gui";

interface TripsProps {
    id?: string;
    updateVarName?: string;
    active?: boolean;
    defaultActive?: boolean;
    updateVars: string;
    libClassName?: string;
    className?: string;
    dynamicClassName?: string;
    propagate?: boolean;
    children?: ReactNode;
    trips?: unknown;
    visible_trips?: string[];
}

const JsonViewer = lazy(() => import("@textea/json-viewer").then((module) => ({ default: module.JsonViewer })));

const Trips = (props: TripsProps) => {
    const { id, trips, visible_trips } = props;

    const dispatch = useDispatch();
    const module = useModule();
    useDispatchRequestUpdateOnFirstRender(dispatch, id, module, props.updateVars);

    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);

    const shownTrips = useMemo(() => {
        if (!trips || !visible_trips) {
            return trips;
        }
        if (typeof trips === "object") {
            return Object.fromEntries(Object.entries(trips).filter(([id]) => visible_trips.includes(id)));
        }
        return trips;
    }, [trips, visible_trips]);

    return (
        <Suspense fallback={<div>Loading...</div>}>
            <JsonViewer className={className} editable={active} value={shownTrips} style={{maxHeight: "70vh", overflowY: "auto"}}></JsonViewer>
        </Suspense>
    );
};
export default Trips;
