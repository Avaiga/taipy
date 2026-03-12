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

import { useCallback } from "react";

import { useDispatchRequestUpdateOnFirstRender } from "../utils/hooks";
import { createSendActionNameAction, createSendUpdateAction } from "../context/taipyReducers";
import { useDispatch, useModule } from "../utils/hooks";

/**
 * A React hook that provides actions for updating data and triggering backend functions.
 *
 * The `sendUpdate` function allows to update a variable on the backend and trigger the `on_change`
 * callback.<br/>
 * The `sendAction` function allows to trigger an `on_action` callback on the backend with a custom
 * payload.
 *
 * @returns An object containing the following keys:
 * - *sendUpdate* is a function that can be used to update a variable on the backend and trigger the
 *   `on_change` callback. It takes the following parameters:
 *   - *name*: The name of the variable to update on the backend.
 *   - *value*: The new value for the variable.
 *   - *onChange*: The name of the `on_change` callback function to trigger.</br>
 *     If not provided, the default `on_change` callback will be triggered if it exists.
 *   - *propagate*: Whether to propagate the update to other components.
 *   - *relName*: The name of the related variable (used when the variable is a value in a list of
 *     values).
 * - *sendAction* is a function that can be used to trigger a backend callback with a custom payload.
 *   This function takes the following parameters:
 *   - *action*: The name of the callback function to trigger on the backend.</br>
 *     If not provided, the default `on_action` callback will be triggered if it exists.
 *   - *args*: Additional arguments sent to the backend in the `payload.args` array of the callback
 *     function.
 */
export function useActions() {
    const dispatch = useDispatch();
    const module = useModule();

    const sendAction = useCallback(
        (id: string | undefined, action: string | undefined, ...args: unknown[]) => {
            dispatch(createSendActionNameAction(id, module, action, ...args));
        },
        [dispatch, module],
    );

    const sendUpdate = useCallback(
        (name = "", value: unknown, onChange?: string, propagate = true, relName?: string) => {
            dispatch(createSendUpdateAction(name, value, module, onChange, propagate, relName));
        },
        [dispatch, module],
    );

    return { sendAction, sendUpdate };
}

/**
 * A React hook that requests an update from the backend for every dynamic property of the element
 * on its first render.
 *
 * @param id - The identifier of the element.
 * @param updateVars - The content of the property *updateVars* of the component.
 * @param varName - The default property backend provided variable (typically the *updateVarName*
 *        property of the component).
 * @param forceRefresh - If true, Taipy re-evaluates the variables. If false, it uses the current values.
 */
export function useRequestUpdateOnFirstRender(
    id?: string,
    updateVars?: string,
    varName?: string,
    forceRefresh?: boolean,
) {
    const dispatch = useDispatch();
    const module = useModule();

    useDispatchRequestUpdateOnFirstRender(dispatch, id, module, updateVars, varName, forceRefresh);
}
