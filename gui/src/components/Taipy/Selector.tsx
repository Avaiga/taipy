import React, { useState, useContext, useCallback, useEffect, useMemo } from "react";
import Box from "@mui/material/Box";
import Checkbox from "@mui/material/Checkbox";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import ListItemAvatar from "@mui/material/ListItemAvatar";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";

import { TaipyImage } from "./utils";
import { TaipyContext } from "../../context/taipyContext";
import { createSendUpdateAction } from "../../context/taipyReducers";
import { boxSx, LovImage, paperBaseSx, SelTreeProps, showItem, treeSelBaseSx, useLovListMemo } from "./lovUtils";
import { useDispatchRequestUpdateOnFirstRender, useDynamicProperty } from "../../utils/hooks";

interface ItemProps {
    value: string;
    createClickHandler: (key: string) => () => void;
    selectedValue: string[];
    item: string | TaipyImage;
    disabled: boolean;
}

const SingleItem = ({ value, createClickHandler, selectedValue, item, disabled }: ItemProps) => (
    <ListItemButton onClick={createClickHandler(value)} selected={selectedValue.indexOf(value) !== -1} disabled={disabled}>
        {typeof item === "string" ? (
            <ListItemText primary={item} />
        ) : (
            <ListItemAvatar>
                <LovImage item={item} />
            </ListItemAvatar>
        )}
    </ListItemButton>
);

const MultipleItem = ({ value, createClickHandler, selectedValue, item, disabled }: ItemProps) => (
    <ListItemButton onClick={createClickHandler(value)} dense disabled={disabled}>
        <ListItemIcon>
            <Checkbox disabled={disabled} edge="start" checked={selectedValue.indexOf(value) !== -1} tabIndex={-1} disableRipple />
        </ListItemIcon>
        {typeof item === "string" ? (
            <ListItemText primary={item} />
        ) : (
            <ListItemAvatar>
                <LovImage item={item} />
            </ListItemAvatar>
        )}
    </ListItemButton>
);

const Selector = (props: SelTreeProps) => {
    const {
        id,
        defaultValue = "",
        value,
        tp_varname = "",
        defaultLov = "",
        filter = false,
        multiple = false,
        className,
        propagate = true,
        lov,
        tp_updatevars = "",
        width = 360,
        height,
    } = props;
    const [searchValue, setSearchValue] = useState("");
    const [selectedValue, setSelectedValue] = useState<string[]>([]);
    const { dispatch } = useContext(TaipyContext);

    const active = useDynamicProperty(props.active, props.defaultActive, true);

    useDispatchRequestUpdateOnFirstRender(dispatch, id, tp_updatevars, tp_varname);

    const lovList = useLovListMemo(lov, defaultLov);
    const listSx = useMemo(() => ({...treeSelBaseSx, maxWidth: width}), [width]);
    const paperSx = useMemo(() => height === undefined ? paperBaseSx : {...paperBaseSx, maxHeight: height}, [height]);

    useEffect(() => {
        if (value !== undefined) {
            setSelectedValue(Array.isArray(value) ? value : [value]);
        } else if (defaultValue) {
            let parsedValue;
            try {
                parsedValue = JSON.parse(defaultValue);
            } catch (e) {
                parsedValue = defaultValue;
            }
            setSelectedValue(Array.isArray(parsedValue) ? parsedValue : [parsedValue]);
        }
    }, [defaultValue, value]);

    const clickHandler = useCallback(
        (key: string) => {
            active &&
                setSelectedValue((keys) => {
                    if (multiple) {
                        const newKeys = [...keys];
                        const p = newKeys.indexOf(key);
                        if (p === -1) {
                            newKeys.push(key);
                        } else {
                            newKeys.splice(p, 1);
                        }
                        dispatch(createSendUpdateAction(tp_varname, newKeys, propagate));
                        return newKeys;
                    } else {
                        dispatch(createSendUpdateAction(tp_varname, key, propagate));
                        return [key];
                    }
                });
        },
        [tp_varname, dispatch, multiple, propagate, active]
    );

    const createClickHandler = useCallback((key: string) => () => clickHandler(key), [clickHandler]);

    const handleInput = useCallback((e) => setSearchValue(e.target.value), []);

    return (
        <Box id={id} sx={boxSx} className={className}>
            <Paper sx={paperSx}>
                <Box>
                {filter && (
                    <TextField
                        margin="dense"
                        placeholder="Search field"
                        value={searchValue}
                        onChange={handleInput}
                        disabled={!active}
                    />
                )}
                </Box>
                <List sx={listSx}>
                    {lovList
                        .filter((elt) => showItem(elt, searchValue))
                        .map((elt) =>
                            multiple ? (
                                <MultipleItem
                                    key={elt.id}
                                    value={elt.id}
                                    item={elt.item}
                                    selectedValue={selectedValue}
                                    createClickHandler={createClickHandler}
                                    disabled={!active}
                                />
                            ) : (
                                <SingleItem
                                    key={elt.id}
                                    value={elt.id}
                                    item={elt.item}
                                    selectedValue={selectedValue}
                                    createClickHandler={createClickHandler}
                                    disabled={!active}
                                />
                            )
                        )}
                </List>
            </Paper>
        </Box>
    );
};

export default Selector;
