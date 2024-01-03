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

import React, { useCallback, useMemo, useState, MouseEvent, CSSProperties } from "react";
import MenuIco from "@mui/icons-material/Menu";
import ListItemButton from "@mui/material/ListItemButton";
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import Avatar from "@mui/material/Avatar";
import CardHeader from "@mui/material/CardHeader";
import ListItemAvatar from "@mui/material/ListItemAvatar";
import Box from "@mui/material/Box";
import Tooltip from '@mui/material/Tooltip';
import { Theme, useTheme } from "@mui/system";

import { SingleItem } from "./lovUtils";
import { createSendActionNameAction } from "../../context/taipyReducers";
import { MenuProps } from "../../utils/lov";
import { useClassNames, useDispatch, useModule } from "../../utils/hooks";

const boxDrawerStyle = { overflowX: "hidden" } as CSSProperties;
const headerSx = { padding: 0 };
const avatarSx = { bgcolor: (theme: Theme) => theme.palette.text.primary };
const baseTitleProps = { noWrap: true, variant: "h6" } as const;

const Menu = (props: MenuProps) => {
    const { label, onAction = "", lov, width, inactiveIds = [], active = true } = props;
    const [selectedValue, setSelectedValue] = useState("");
    const [opened, setOpened] = useState(false);
    const dispatch = useDispatch();
    const theme = useTheme();
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);

    const clickHandler = useCallback(
        (evt: MouseEvent<HTMLElement>) => {
            if (active) {
                const { id: key = "" } = evt.currentTarget.dataset;
                setSelectedValue(() => {
                    dispatch(createSendActionNameAction("menu", module, onAction, key));
                    return key;
                });
            }
        },
        [onAction, dispatch, active, module]
    );

    const openHandler = useCallback((evt: MouseEvent<HTMLElement>) => {
        evt.stopPropagation();
        setOpened((o) => !o);
    }, []);

    const [drawerSx, titleProps] = useMemo(() => {
        const drawerWidth = opened ? width : `calc(${theme.spacing(9)} + 1px)`;
        const titleWidth = opened ? `calc(${width} - ${theme.spacing(10)})`: undefined;
        return [{
            width: drawerWidth,
            flexShrink: 0,
            "& .MuiDrawer-paper": {
                width: drawerWidth,
                boxSizing: "border-box",
                transition: "width 0.3s",
            },
            transition: "width 0.3s",
        }, {...baseTitleProps, width: titleWidth}];
    }, [opened, width, theme]);

    return lov && lov.length ? (
        <Drawer variant="permanent" anchor="left" sx={drawerSx} className={className}>
            <Box style={boxDrawerStyle}>
                <List>
                    <ListItemButton key="taipy_menu_0" onClick={openHandler}>
                        <ListItemAvatar>
                            <CardHeader
                                sx={headerSx}
                                avatar={
                                    <Tooltip title={label || false}><Avatar sx={avatarSx}>
                                        <MenuIco />
                                    </Avatar></Tooltip>
                                }
                                title={label}
                                titleTypographyProps={titleProps}
                            />
                        </ListItemAvatar>
                    </ListItemButton>
                    {lov.map((elt) => (
                        <SingleItem
                            key={elt.id}
                            value={elt.id}
                            item={elt.item}
                            selectedValue={selectedValue}
                            clickHandler={clickHandler}
                            disabled={!active || inactiveIds.includes(elt.id)}
                            withAvatar={true}
                            titleTypographyProps={titleProps}
                        />
                    ))}
                </List>
            </Box>
        </Drawer>
    ) : null;
};

export default Menu;
