import React, { useCallback, useContext, useMemo, useState, MouseEvent, CSSProperties } from "react";
import MenuIco from "@mui/icons-material/Menu";
import ListItemButton from "@mui/material/ListItemButton";
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import Avatar from "@mui/material/Avatar";
import CardHeader from "@mui/material/CardHeader";
import ListItemAvatar from "@mui/material/ListItemAvatar";
import Box from "@mui/material/Box";
import Tooltip from '@mui/material/Tooltip';
import { useTheme } from "@mui/material";

import { SingleItem } from "./lovUtils";
import { TaipyContext } from "../../context/taipyContext";
import { createSendActionNameAction } from "../../context/taipyReducers";
import { MenuProps } from "../../utils/lov";

const boxDrawerStyle = { overflowX: "hidden" } as CSSProperties;
const headerSx = { padding: 0 };
const avatarSx = { bgcolor: "white" };
const baseTitleProps = { noWrap: true, variant: "h6" } as const;

const Menu = (props: MenuProps) => {
    const { label, tp_onAction, lov, width, inactiveIds = [], active = true, className } = props;
    const [selectedValue, setSelectedValue] = useState("");
    const [opened, setOpened] = useState(false);
    const { dispatch } = useContext(TaipyContext);
    const theme = useTheme();

    const clickHandler = useCallback(
        (evt: MouseEvent<HTMLElement>) => {
            if (active) {
                const { id: key = "" } = evt.currentTarget.dataset;
                setSelectedValue(() => {
                    dispatch(createSendActionNameAction("menu", tp_onAction, key));
                    return key;
                });
            }
        },
        [tp_onAction, dispatch, active]
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
