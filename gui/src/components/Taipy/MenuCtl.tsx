import React, { useContext, useMemo, useEffect } from "react";

import { LovProps, useLovListMemo } from "./lovUtils";
import { TaipyContext } from "../../context/taipyContext";
import { useDispatchRequestUpdateOnFirstRender, useDynamicProperty, useIsMobile } from "../../utils/hooks";
import { createSetMenuAction } from "../../context/taipyReducers";
import { MenuProps } from "../../utils/lov";

interface MenuCtlProps extends LovProps<string> {
    label?: string;
    width?: string;
    width_Mobile_?: string;
    tp_onAction?: string;
    inactiveIds?: string[];
    defaultInactiveIds?: string;
}

const MenuCtl = (props: MenuCtlProps) => {
    const {
        id,
        label,
        tp_onAction,
        defaultLov = "",
        width = "15vw",
        className,
        width_Mobile_ = "85vw",
    } = props;
    const { dispatch } = useContext(TaipyContext);
    const isMobile = useIsMobile();

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
        dispatch(
            createSetMenuAction({
                label: label,
                tp_onAction: tp_onAction,
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
        tp_onAction,
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
