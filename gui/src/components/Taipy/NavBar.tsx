import React, { useCallback, useContext, useState } from "react";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Box from "@mui/material/Box";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Drawer from "@mui/material/Drawer";
import IconButton from "@mui/material/IconButton";
import Menu from "@mui/icons-material/Menu";
import { useMediaQuery, useTheme } from "@mui/material";
import { useLocation, useNavigate } from "react-router";

import { LovItem, LovProps, useLovListMemo } from "./lovUtils";
import { useDynamicProperty } from "../../utils/hooks";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyImage } from "./utils";
import Link from "./Link";

const boxSx = { borderBottom: 1, borderColor: "divider", width: "fit-content" };

const NavBar = (props: LovProps) => {
    const { id, className, lov, defaultLov = "" } = props;
    const { state } = useContext(TaipyContext);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const location = useLocation();
    const navigate = useNavigate();
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down("md"));
    const [opened, setOpened] = useState(false);

    let lovList = useLovListMemo(lov, defaultLov);
    if (!lovList.length) {
        lovList = Object.keys(state.locations || {})
            .filter((key) => key !== "/")
            .map((key) => ({ id: key, item: state.locations[key].substring(1) } as LovItem));
    }

    const linkChange = useCallback(
        (evt, val: string) => {
            if (Object.keys(state.locations || {}).some((route) => val === route)) {
                navigate(val);
            } else {
                const win = window.open(val, "_blank");
                win?.focus();
            }
        },
        [navigate, state.locations]
    );

    return isMobile ? (<>
        <Drawer open={opened} onClose={() => setOpened(false)}>
            <List>
                {lovList.map((val) => (
                    <ListItem key={val.id} onClick={() => setOpened(false)} disabled={!active}>
                        <ListItemText>
                            <Link href={val.id}>
                                {(typeof val.item === "string" ? val.item : (val.item as TaipyImage).text) || val.id}
                            </Link>
                        </ListItemText>
                    </ListItem>
                ))}
            </List>
        </Drawer>
        <IconButton onClick={() => setOpened(o => !o)}>
        <Menu />
      </IconButton>
        </>
    ) : (
        <Box sx={boxSx} className={className}>
            <Tabs value={location.pathname} id={id} onChange={linkChange}>
                {lovList.map((val) => (
                    <Tab
                        key={val.id}
                        value={val.id}
                        disabled={!active}
                        label={(typeof val.item === "string" ? val.item : (val.item as TaipyImage).text) || val.id}
                    />
                ))}
            </Tabs>
        </Box>
    );
};

export default NavBar;
