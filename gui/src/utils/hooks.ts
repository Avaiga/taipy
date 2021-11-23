import { Dispatch, useContext, useEffect, useMemo, useRef } from "react";
import { useMediaQuery, useTheme } from "@mui/material";

import { getUpdateVars } from "../components/Taipy/utils";
import { TaipyContext } from "../context/taipyContext";
import { createRequestUpdateAction, FormatConfig, TaipyBaseAction } from "../context/taipyReducers";

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

export const useDispatchRequestUpdateOnFirstRender = (
    dispatch: Dispatch<TaipyBaseAction>,
    id?: string,
    updateVars?: string,
    varName?: string
) => {
    useEffect(() => {
        const updateArray = getUpdateVars(updateVars);
        varName && updateArray.push(varName);
        updateArray.length && dispatch(createRequestUpdateAction(id, updateArray));
    }, [updateVars, dispatch, id, varName]);
};

export const useFormatConfig = (): FormatConfig => {
    const { state } = useContext(TaipyContext);

    return useMemo(
        () =>
            ({
                timeZone: state.timeZone,
                dateTime: state.dateTimeFormat || "yyyy-MM-dd HH:mm:ss zzz",
                number: state.numberFormat || "%f",
            } as FormatConfig),
        [state.timeZone, state.dateTimeFormat, state.numberFormat]
    );
};

export const useIsMobile = () => {
    const theme = useTheme();
    return useMediaQuery(theme.breakpoints.down("sm"));
};

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
