/*
 * Copyright 2023 Avaiga Private Limited
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

import React, { useCallback, useContext, useState } from "react";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Box from "@mui/material/Box";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Drawer from "@mui/material/Drawer";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import Menu from "@mui/icons-material/Menu";
import { useLocation, useNavigate } from "react-router";

import Link from "./Link";
import { LovProps, useLovListMemo, LovImage } from "./lovUtils";
import { useClassNames, useDynamicProperty, useIsMobile } from "../../utils/hooks";
import { TaipyContext } from "../../context/taipyContext";
import { LovItem } from "../../utils/lov";

const boxSx = { borderBottom: 1, borderColor: "divider", width: "fit-content" };

const NavBar = (props: LovProps) => {
    const { id, lov, defaultLov = "" } = props;
    const { state } = useContext(TaipyContext);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const location = useLocation();
    const navigate = useNavigate();
    const isMobile = useIsMobile();
    const [opened, setOpened] = useState(false);

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);
    let lovList = useLovListMemo(lov, defaultLov);
    if (!lovList.length) {
        lovList = Object.keys(state.locations || {})
            .filter((key) => key !== "/")
            .map((key) => ({ id: key, item: state.locations[key].substring(1) } as LovItem));
    }

    const linkChange = useCallback(
        (evt: React.SyntheticEvent, val: string) => {
            if (Object.keys(state.locations || {}).some((route) => val === route)) {
                navigate(val);
            } else {
                const win = window.open(val, "_blank");
                win?.focus();
            }
        },
        [navigate, state.locations]
    );

    const selectedVal =
        !isMobile &&
        (lovList.find((it) => it.id === location.pathname)?.id || (lovList.length ? lovList[0].id : false));

    return isMobile ? (
        <Tooltip title={hover || ""}>
            <>
                <Drawer open={opened} onClose={() => setOpened(false)}>
                    <List>
                        {lovList.map((val) => (
                            <ListItem key={val.id} onClick={() => setOpened(false)} disabled={!active}>
                                <ListItemText>
                                    <Link href={val.id}>
                                        {typeof val.item === "string" ? val.item : <LovImage item={val.item} />}
                                    </Link>
                                </ListItemText>
                            </ListItem>
                        ))}
                    </List>
                </Drawer>
                <IconButton onClick={() => setOpened((o) => !o)}>
                    <Menu />
                </IconButton>
            </>
        </Tooltip>
    ) : (
        <Box sx={boxSx} className={className}>
            <Tooltip title={hover || ""}>
                <Tabs value={selectedVal} id={id} onChange={linkChange}>
                    {lovList.map((val) => (
                        <Tab
                            key={val.id}
                            value={val.id}
                            disabled={!active}
                            label={typeof val.item === "string" ? val.item : <LovImage item={val.item} />}
                        />
                    ))}
                </Tabs>
            </Tooltip>
        </Box>
    );
};

export default NavBar;
