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

import { Dispatch, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { useMediaQuery, useTheme } from "@mui/material";

import { getUpdateVars } from "../components/Taipy/utils";
import { PageContext, TaipyContext } from "../context/taipyContext";
import { createRequestUpdateAction, FormatConfig, TaipyBaseAction } from "../context/taipyReducers";
import { TIMEZONE_CLIENT } from "../utils";

/**
 * A React hook to manage a dynamic scalar property.
 *
 * A dynamic scalar property  is defined by a default property and a bound property.
 * @typeParam T - The dynamic property type.
 * @param value - The bound value.
 * @param defaultValue - The default value.
 * @param defaultStatic - The default static value.
 * @returns The latest updated value.
 */
export const useDynamicProperty = <T>(value: T, defaultValue: T, defaultStatic: T): T => {
    return useMemo(() => {
        if (value !== undefined) {
            return value;
        }
        if (defaultValue !== undefined) {
            return defaultValue;
        }
        return defaultStatic;
    }, [value, defaultValue, defaultStatic]);
};

/**
 * A React hook to manage a dynamic json property.
 *
 * A dynamic json property  is defined by a default property and a bound property.
 * @typeParam T - The dynamic property type.
 * @param value - The bound value.
 * @param defaultValue - The default value.
 * @param defaultStatic - The default static value.
 * @returns The latest updated value.
 */
export const useDynamicJsonProperty = <T>(value: string | undefined, defaultValue: string, defaultStatic: T): T => {
    const defaultJson = useMemo(() => {
        if (defaultValue && typeof defaultValue === "string") {
            try {
                return JSON.parse(defaultValue);
            } catch (e) {
                console.warn("useDynamicJsonProperty: defaultValue", e);
            }
        }
        return defaultStatic;
    }, [defaultValue, defaultStatic]);
    return useMemo(() => {
        if (value && typeof value === "string") {
            try {
                return JSON.parse(value);
            } catch (e) {
                console.warn("useDynamicJsonProperty: value", e);
            }
        }
        return defaultJson;
    }, [value, defaultJson]);
};

/**
 * A React hook that requests an update for every dynamic property of the element.
 * @param dispatch - The React dispatcher associated to `TaipyContext`.
 * @param id - The identifier of the element.
 * @param context - The execution context.
 * @param updateVars - The content of the property `updateVars`.
 * @param varName - The default property backend provided variable (through property `updateVarName`).
 * @param forceRefresh - Should Taipy re-evaluate the variables or use the current values.
 */
export const useDispatchRequestUpdateOnFirstRender = (
    dispatch: Dispatch<TaipyBaseAction>,
    id?: string,
    context?: string,
    updateVars?: string,
    varName?: string,
    forceRefresh?: boolean
) => {
    useEffect(() => {
        const updateArray = getUpdateVars(updateVars).filter(uv => !uv.includes(","));
        varName && updateArray.push(varName);
        updateArray.length && dispatch(createRequestUpdateAction(id, context, updateArray, forceRefresh));
    }, [updateVars, dispatch, id, context, varName, forceRefresh]);
};

export const useFormatConfig = (): FormatConfig => {
    const { state } = useContext(TaipyContext);

    return useMemo(
        () =>
            ({
                timeZone: state.timeZone || TIMEZONE_CLIENT,
                forceTZ: !!state.timeZone,
                dateTime: state.dateTimeFormat || "yyyy-MM-dd HH:mm:ss zzz",
                date: state.dateFormat || "yyyy-MM-dd",
                number: state.numberFormat || "%f",
            } as FormatConfig),
        [state.timeZone, state.dateFormat, state.dateTimeFormat, state.numberFormat]
    );
};

export const useIsMobile = () => {
    const theme = useTheme();
    return useMediaQuery(theme.breakpoints.down("sm"));
};

/**
 * A React hook that returns the *dispatch* function.
 *
 * The *dispatch* function allows to send Actions to the Store and initiate backend\
 * communications.
 * @returns The *dispatch* function.
 */
export const useDispatch = () => {
    const { dispatch } = useContext(TaipyContext);
    return dispatch;
};

/**
 * A React hook that returns the page module.
 *
 * The *module* Needs to be added to all Actions to allow for the correct execution of backend functions.
 * @returns The page module.
 */
export const useModule = () => {
    const { module } = useContext(PageContext);
    return module;
};

/**
 * A React hook to manage classNames (dynamic and static).
 * cf. useDynamicProperty
 *
 * @param libClassName - The default static className.
 * @param dynamicClassName - The bound className.
 * @param className - The default user set className.
 * @returns The complete list of applicable classNames.
 */
export const useClassNames = (libClassName?: string, dynamicClassName?: string, className?: string) =>
    ((libClassName || "") + " " + (useDynamicProperty(dynamicClassName, className, undefined) || "")).trim();

export const useWhyDidYouUpdate = (name: string, props: Record<string, unknown>): void => {
    // Get a mutable ref object where we can store props ...
    // ... for comparison next time this hook runs.
    const previousProps = useRef({} as Record<string, unknown>);
    useEffect(() => {
        if (previousProps.current) {
            // Get all keys from previous and current props
            const allKeys = Object.keys({ ...previousProps.current, ...props });
            // Use this object to keep track of changed props
            const changesObj = {} as Record<string, unknown>;
            // Iterate through keys
            allKeys.forEach((key) => {
                // If previous is different from current
                if (previousProps.current[key] !== props[key]) {
                    // Add to changesObj
                    changesObj[key] = {
                        from: previousProps.current[key],
                        to: props[key],
                    };
                }
            });
            // If changesObj not empty then output to console
            if (Object.keys(changesObj).length) {
                console.log("[why-did-you-update]", name, changesObj);
            }
        }
        // Finally update previousProps with current props for next hook call
        previousProps.current = props;
    });
};

export const useElementVisible = (root: HTMLElement | null = null, rootMargin = "0px", threshold = 1.0) => {
    const [container, setRef] = useState<HTMLElement| null>(null);
    const [isVisible, setVisible] = useState(false);
    const onObserver = useCallback((entries: Array<IntersectionObserverEntry>) => setVisible(entries.some(e => e.isIntersecting)), [setVisible]);
    const observer = useMemo(() => new IntersectionObserver(onObserver, {root, rootMargin, threshold}), [root, rootMargin, threshold, onObserver]);
    useEffect(() => {
        if (!container) {
            return;
        }
        const contRef = container;
        const obsRef = observer;
        observer.observe(container);
        return () => {obsRef.unobserve(contRef);}
    }, [container, observer]);
    return [setRef, isVisible];
}
