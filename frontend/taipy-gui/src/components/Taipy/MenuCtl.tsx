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

import React, { useMemo, useEffect } from "react";

import { LovProps, useLovListMemo } from "./lovUtils";
import { useClassNames, useDispatch, useDispatchRequestUpdateOnFirstRender, useDynamicProperty, useIsMobile, useModule } from "../../utils/hooks";
import { createSetMenuAction } from "../../context/taipyReducers";
import { MenuProps } from "../../utils/lov";

interface MenuCtlProps extends LovProps<string> {
    label?: string;
    width?: string;
    width_Mobile_?: string;
    onAction?: string;
    inactiveIds?: string[];
    defaultInactiveIds?: string;
}

const MenuCtl = (props: MenuCtlProps) => {
    const {
        id,
        label,
        onAction,
        defaultLov = "",
        width = "15vw",
        width_Mobile_ = "85vw",
    } = props;
    const dispatch = useDispatch();
    const isMobile = useIsMobile();
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);

    useDispatchRequestUpdateOnFirstRender(dispatch, id, module, props.updateVars, props.updateVarName);

    const lovList = useLovListMemo(props.lov, defaultLov, true);

    const inactiveIds = useMemo(() => {
        if (props.inactiveIds) {
            return props.inactiveIds;
        }
        if (props.defaultInactiveIds) {
            try {
                return JSON.parse(props.defaultInactiveIds) as string[];
            } catch {
                // too bad
            }
        }
        return [];
    }, [props.inactiveIds, props.defaultInactiveIds]);

    useEffect(() => {
        dispatch(
            createSetMenuAction({
                label: label,
                onAction: onAction,
                active: active,
                lov: lovList,
                inactiveIds: inactiveIds,
                width: isMobile ? width_Mobile_ : width,
                className: className,
            } as MenuProps)
        );
        return () => dispatch(createSetMenuAction({}));
    }, [
        label,
        onAction,
        active,
        lovList,
        inactiveIds,
        width,
        width_Mobile_,
        isMobile,
        className,
        dispatch,
    ]);

    return <></>;
};

export default MenuCtl;
