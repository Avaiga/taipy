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

import { createSendActionNameAction, createSendUpdateAction } from "../context/taipyReducers";
import { useDispatch, useModule } from "../utils/hooks";

export const useActions = () => {
    const dispatch = useDispatch();
    const module = useModule();

    const sendAction = useCallback(
        (name: string | undefined, value: unknown, ...args: unknown[]) => {
            dispatch(createSendActionNameAction(name, module, value, ...args));
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
};
