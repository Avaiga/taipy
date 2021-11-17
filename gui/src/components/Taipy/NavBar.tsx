import React, { useCallback, useContext } from "react";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Box from "@mui/material/Box";
import { useLocation, useNavigate } from "react-router";

import { LovItem, LovProps, useLovListMemo } from "./lovUtils";
import { useDynamicProperty } from "../../utils/hooks";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyImage } from "./utils";

const boxSx = { borderBottom: 1, borderColor: "divider", width: "fit-content" };

const NavBar = (props: LovProps) => {
    const { id, className, lov, defaultLov = "" } = props;
    const { state } = useContext(TaipyContext);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const location = useLocation();
    const navigate = useNavigate();
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

    return (
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
