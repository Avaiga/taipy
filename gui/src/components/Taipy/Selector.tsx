import React, { useState, useContext, useCallback } from "react";
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

import { TaipyImage, TaipyInputProps } from "./utils";
import { TaipyContext } from "../../context/taipyContext";
import { createSendUpdateAction } from "../../context/taipyReducers";

interface SelectorProps extends TaipyInputProps {
    lov: Record<string, string | TaipyImage>;
    filter: boolean;
    multiple: boolean;
}

const boxSx = { width: "100%" };
const paperSx = { width: "100%", mb: 2 };

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

const Selector = (props: SelectorProps) => {
    const { defaultvalue, tp_varname, lov, filter, multiple } = props;
    const [selectedValue, setSelectedValue] = useState<string[]>(() => (defaultvalue ? [defaultvalue] : []));
    const [searchValue, setSearchValue] = useState("");
    const { dispatch } = useContext(TaipyContext);

    const clickHandler = useCallback(
        (key: string) => {
            setSelectedValue((keys) => {
                if (multiple) {
                    const newKeys = [...keys];
                    const p = newKeys.indexOf(key);
                    if (p === -1) {
                        newKeys.push(key);
                    } else {
                        newKeys.splice(p);
                    }
                    dispatch(createSendUpdateAction(tp_varname, newKeys));
                    return newKeys;
                } else {
                    dispatch(createSendUpdateAction(tp_varname, key));
                    return [key];
                }
            });
        },
        [tp_varname, dispatch, multiple]
    );

    const createClickHandler = useCallback((key: string) => () => clickHandler(key), [clickHandler]);

    const handleInput = useCallback((e) => {
        setSearchValue(e.target.value);
    }, []);

    return (
        <Box sx={boxSx}>
            <Paper sx={paperSx}>
                {filter && (
                    <TextField margin="dense" placeholder="Search field" value={searchValue} onChange={handleInput} />
                )}
                <List sx={{ width: "100%", maxWidth: 360, bgcolor: "background.paper" }}>
                    {lov &&
                        Object.keys(lov)
                            .filter(
                                (key) =>
                                    !filter ||
                                    (
                                        (typeof lov[key] === "string"
                                            ? (lov[key] as string)
                                            : (lov[key] as TaipyImage).text) || key
                                    )
                                        .toLowerCase()
                                        .indexOf(searchValue.toLowerCase()) > -1
                            )
                            .map((key) =>
                                multiple ? (
                                    <MultipleItem
                                        key={key}
                                        value={key}
                                        item={lov[key]}
                                        selectedValue={selectedValue}
                                        createClickHandler={createClickHandler}
                                    />
                                ) : (
                                    <SingleItem
                                        key={key}
                                        value={key}
                                        item={lov[key]}
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
