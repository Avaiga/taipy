import React, {
    useContext,
    useMemo,
    useEffect,
} from "react";

import { LovProps, useLovListMemo } from "./lovUtils";
import { TaipyContext } from "../../context/taipyContext";
import { useDispatchRequestUpdateOnFirstRender, useDynamicProperty } from "../../utils/hooks";
import { createSetMenuAction } from "../../context/taipyReducers";
import { MenuProps } from "../../utils/lov";

interface MenuCtlProps extends LovProps<string> {
    label?: string;
    width?: string;
    tp_onAction?: string;
    inactiveIds?: string[];
    defaultInactiveIds?: string;
}

const MenuCtl = (props: MenuCtlProps) => {
    const { id, label, tp_onAction, defaultLov = "", width = "15vw", defaultValue, value, className } = props;
    const { dispatch } = useContext(TaipyContext);

    const active = useDynamicProperty(props.active, props.defaultActive, true);

    useDispatchRequestUpdateOnFirstRender(dispatch, id, props.tp_updatevars, props.tp_varname);

    const lovList = useLovListMemo(props.lov, defaultLov, true);

    const inactiveIds = useMemo(() => {
        if (props.inactiveIds) {
            return props.inactiveIds;
        }
        if (props.defaultInactiveIds) {
            try {
                return JSON.parse(props.defaultInactiveIds) as string[];
            } catch (e) {
                // too bad
            }
        }
        return [];
    }, [props.inactiveIds, props.defaultInactiveIds]);

    useEffect(() => {
        dispatch(createSetMenuAction({
            label: label,
            tp_onAction: tp_onAction,
            active: active,
            lov: lovList,
            inactiveIds: inactiveIds,
            value: value || defaultValue,
            width: width,
            className: className,
        } as MenuProps));
        return () => dispatch(createSetMenuAction({}));
    }, [label, tp_onAction, active, lovList, inactiveIds, value, defaultValue, width, className, dispatch]);

    return <></>;
};

export default MenuCtl;
