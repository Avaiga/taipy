import React, { useCallback, useContext, useMemo, useState, MouseEvent, useEffect, useRef } from "react";
import MenuIco from "@mui/icons-material/Menu";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import ListItemIcon from "@mui/material/ListItemIcon";

import { LovProps, useLovListMemo, SingleItem } from "./lovUtils";
import { TaipyContext } from "../../context/taipyContext";
import { useDispatchRequestUpdateOnFirstRender, useDynamicProperty } from "../../utils/hooks";
import { createMenuMargin, createSendActionNameAction } from "../../context/taipyReducers";
import { Box, useTheme } from "@mui/material";

interface MenuProps extends LovProps<string> {
    label?: string;
    width?: string;
    tp_onAction?: string;
    inactiveIds?: string[];
    defaultInactiveIds?: string;
}

const baseDrawerSx = { overflowX: "hidden", maxHeight: "100vh" };

const Menu = (props: MenuProps) => {
    const { id, label, tp_onAction, defaultLov = "" } = props;
    const [selectedValue, setSelectedValue] = useState<string>("");
    const [opened, setOpened] = useState(false);
    const { dispatch } = useContext(TaipyContext);
    const boxRef = useRef<HTMLDivElement>(null);
    const theme = useTheme();

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

    const clickHandler = useCallback(
        (evt: MouseEvent<HTMLElement>) => {
            if (active) {
                const { id: key = "" } = evt.currentTarget.dataset;
                setSelectedValue(() => {
                    dispatch(createSendActionNameAction(id, tp_onAction, key));
                    return key;
                });
            }
        },
        [id, tp_onAction, dispatch, active]
    );

    const openHandler = useCallback((evt: MouseEvent<HTMLElement>) => {
        evt.stopPropagation();
        setOpened((o) => !o);
    }, []);

    const drawerSx = useMemo(() => {
        const w = opened ? props.width : `calc(${theme.spacing(9)} + 1px)`;
        return w ? { ...baseDrawerSx, width: w } : baseDrawerSx;
    }, [opened, props.width, theme]);

    useEffect(() => {
        drawerSx && boxRef.current && dispatch(createMenuMargin(boxRef.current.offsetWidth));
        return () => dispatch(createMenuMargin(0));
    }, [boxRef, drawerSx, dispatch]);

    return (
        <Drawer variant="permanent" anchor="left">
            <Box sx={drawerSx} ref={boxRef}>
                <List>
                    <ListItemButton key="taipy_menu_0" onClick={openHandler}>
                        <ListItemIcon>
                            <MenuIco />
                        </ListItemIcon>
                        {opened && label ? <ListItemText primary={label} /> : null}
                    </ListItemButton>
                    {lovList.map((elt) => (
                        <SingleItem
                            key={elt.id}
                            value={elt.id}
                            item={elt.item}
                            selectedValue={selectedValue}
                            clickHandler={clickHandler}
                            disabled={!active || inactiveIds.includes(elt.id)}
                            withAvatar={true}
                        />
                    ))}
                </List>
            </Box>
        </Drawer>
    );
};

export default Menu;
