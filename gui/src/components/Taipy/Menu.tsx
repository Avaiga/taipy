import React, { useCallback, useContext, useMemo, useState, MouseEvent } from "react";
import IconButton from "@mui/material/IconButton";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import AppBar from "@mui/material/AppBar";
import MuiMenu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import ListItemAvatar from "@mui/material/ListItemAvatar";

import { LovProps, useLovListMemo, LovItem, LovImage } from "./lovUtils";
import { TaipyContext } from "../../context/taipyContext";
import { useDispatchRequestUpdateOnFirstRender, useDynamicProperty } from "../../utils/hooks";
import { Button } from "@mui/material";

const renderMenu = (
    lov: LovItem[],
    active: boolean,
    selectedValue: string,
    inactiveIds: string[],
    onClick: (evt: MouseEvent<HTMLDivElement>) => void
) => {
    return lov.map((li) => {
        const children = li.children ? renderMenu(li.children, active, selectedValue, inactiveIds, onClick) : [];
        return (
            <MenuItem key={li.id} disabled={!active || inactiveIds.includes(li.id)} selected={li.id === selectedValue}>
                <ListItemButton data-id={li.id} onClick={onClick}>
                    {typeof li.item === "string" ? (
                        <ListItemText primary={li.item} />
                    ) : (
                        <ListItemAvatar>
                            <LovImage item={li.item} />
                        </ListItemAvatar>
                    )}
                </ListItemButton>

                {children}
            </MenuItem>
        );
    });
};

interface MenuProps extends LovProps<string> {
    bar?: boolean;
    label?: string;
    width?: string;
    tp_onAction?: string;
    inactiveIds?: string[];
    defaultInactiveIds?: string;
}

const Menu = (props: MenuProps) => {
    const { id, bar = true, label, width = "100vw", tp_onAction, defaultLov = "" } = props;
    const [selectedValue, setSelectedValue] = useState<string>("");
    const [anchorEl, setAnchorEl] = useState(null);
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

    const handleClick = useCallback((event) => setAnchorEl(event.currentTarget), []);
    const handleClose = useCallback(() => setAnchorEl(null), []);
    const handleAction = useCallback((e) => {
        const { id } = e.currentTarget.dataset;
    }, []);

    return bar ? (
        <AppBar sx={{width: width}}>{
            lovList.map(elt => <Button key={elt.id} data-id={elt.id}></Button>)
            }</AppBar>
    ) : (
        <>
            {label ? <Button onClick={handleClick}>{label}</Button> : <IconButton onClick={handleClick}><MoreVertIcon /></IconButton>}
            <MuiMenu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleClose}>
                {renderMenu(lovList, !!active, selectedValue, inactiveIds, handleAction)}
            </MuiMenu>
        </>
    );
};
