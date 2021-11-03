import React, { useState, useContext, useCallback, useEffect } from "react";
import Avatar from "@mui/material/Avatar";
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
import { LovProps, useLovListMemo } from "./lovUtils";
import { useDispatchRequestUpdateOnFirstRender, useDynamicProperty } from "../../utils/hooks";

const boxSx = { width: "100%" };
const paperSx = { width: "100%", mb: 2 };
const listSx = { width: "100%", maxWidth: 360, bgcolor: "background.paper" };

interface ItemProps {
    value: string;
    createClickHandler: (key: string) => () => void;
    selectedValue: string[];
    item: string | TaipyImage;
}

const SingleItem = ({ value, createClickHandler, selectedValue, item }: ItemProps) => (
    <ListItemButton onClick={createClickHandler(value)} selected={selectedValue.indexOf(value) !== -1}>
        {typeof item === "string" ? (
            <ListItemText primary={item} />
        ) : (
            <ListItemAvatar>
                <Avatar alt={(item as TaipyImage).text || value} src={(item as TaipyImage).path} />
            </ListItemAvatar>
        )}
    </ListItemButton>
);

const MultipleItem = ({ value, createClickHandler, selectedValue, item }: ItemProps) => (
    <ListItemButton onClick={createClickHandler(value)} dense>
        <ListItemIcon>
            <Checkbox edge="start" checked={selectedValue.indexOf(value) !== -1} tabIndex={-1} disableRipple />
        </ListItemIcon>
        {typeof item === "string" ? (
            <ListItemText primary={item} />
        ) : (
            <ListItemAvatar>
                <Avatar alt={(item as TaipyImage).text || value} src={(item as TaipyImage).path} />
            </ListItemAvatar>
        )}
    </ListItemButton>
);

interface SelectorProps extends LovProps {
    filter: boolean;
    multiple: boolean;
}

const Selector = (props: SelectorProps) => {
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
    } = props;
    const [searchValue, setSearchValue] = useState("");
    const [selectedValue, setSelectedValue] = useState<string[]>([]);
    const { dispatch } = useContext(TaipyContext);

    const active = useDynamicProperty(props.active, props.defaultActive, true);

    useDispatchRequestUpdateOnFirstRender(dispatch, id, tp_updatevars, tp_varname);

    const lovList = useLovListMemo(lov, defaultLov);

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
                {filter && (
                    <TextField
                        margin="dense"
                        placeholder="Search field"
                        value={searchValue}
                        onChange={handleInput}
                        disabled={!active}
                    />
                )}
                <List sx={listSx}>
                    {lovList
                        .filter(
                            (elt) =>
                                !filter ||
                                (
                                    (typeof elt.item === "string"
                                        ? (elt.item as string)
                                        : (elt.item as TaipyImage).text) || elt.id
                                )
                                    .toLowerCase()
                                    .indexOf(searchValue.toLowerCase()) > -1
                        )
                        .map((elt) =>
                            multiple ? (
                                <MultipleItem
                                    key={elt.id}
                                    value={elt.id}
                                    item={elt.item}
                                    selectedValue={selectedValue}
                                    createClickHandler={createClickHandler}
                                />
                            ) : (
                                <SingleItem
                                    key={elt.id}
                                    value={elt.id}
                                    item={elt.item}
                                    selectedValue={selectedValue}
                                    createClickHandler={createClickHandler}
                                />
                            )
                        )}
                </List>
            </Paper>
        </Box>
    );
};

export default Selector;
