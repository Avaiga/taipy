import React, { useState, useContext, useCallback, useEffect, useMemo, CSSProperties } from "react";
import { Theme, useTheme } from "@mui/material/styles";
import Box from "@mui/material/Box";
import Checkbox from "@mui/material/Checkbox";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import ListItemAvatar from "@mui/material/ListItemAvatar";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import OutlinedInput from "@mui/material/OutlinedInput";
import Avatar from "@mui/material/Avatar";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import Chip from "@mui/material/Chip";

import { doNotPropagateEvent, TaipyImage } from "./utils";
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
    <ListItemButton
        onClick={createClickHandler(value)}
        selected={selectedValue.indexOf(value) !== -1}
        disabled={disabled}
    >
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
            <Checkbox
                disabled={disabled}
                edge="start"
                checked={selectedValue.indexOf(value) !== -1}
                tabIndex={-1}
                disableRipple
            />
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

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const getMenuProps = (width: string | number, height?: string | number) => ({
    PaperProps: {
        style: {
            maxHeight: height || ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
            width: width,
        },
    },
});

const getStyles = (id: string, ids: readonly string[], theme: Theme) => ({
    fontWeight: ids.indexOf(id) === -1 ? theme.typography.fontWeightRegular : theme.typography.fontWeightMedium,
});

const renderBoxSx = { display: "flex", flexWrap: "wrap", gap: 0.5 } as CSSProperties;

const Selector = (props: SelTreeProps) => {
    const {
        id,
        defaultValue = "",
        value,
        tp_varname = "",
        defaultLov = "",
        filter = false,
        multiple = false,
        dropdown = false,
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
    const theme = useTheme();

    const active = useDynamicProperty(props.active, props.defaultActive, true);

    useDispatchRequestUpdateOnFirstRender(dispatch, id, tp_updatevars, tp_varname);

    const lovList = useLovListMemo(lov, defaultLov);
    const listSx = useMemo(() => ({ ...treeSelBaseSx, maxWidth: width }), [width]);
    const paperSx = useMemo(
        () => (height === undefined ? paperBaseSx : { ...paperBaseSx, maxHeight: height }),
        [height]
    );
    const controlSx = useMemo(() => ({ m: 1, width: width }), [width]);

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

    const handleChange = (event: SelectChangeEvent<typeof selectedValue>) => {
        const {
            target: { value },
        } = event;
        // On autofill we get a stringified value.
        const keys = typeof value === "string" ? value.split(",") : value;
        setSelectedValue(keys);
        dispatch(createSendUpdateAction(tp_varname, keys, propagate));
    };

    const handleDelete = useCallback(
        (e) => {
            const id = e.currentTarget.parentElement.getAttribute("data-id");
            id &&
                setSelectedValue((vals) => {
                    const keys = vals.filter((valId) => valId !== id);
                    dispatch(createSendUpdateAction(tp_varname, keys, propagate));
                    return keys;
                });
        },
        [tp_varname, propagate, dispatch]
    );

    const createClickHandler = useCallback((key: string) => () => clickHandler(key), [clickHandler]);

    const handleInput = useCallback((e) => setSearchValue(e.target.value), []);

    return (
        <Box id={id} sx={boxSx} className={className}>
            {dropdown ? (
                <FormControl sx={controlSx}>
                    <Select
                        multiple={multiple}
                        value={selectedValue}
                        onChange={handleChange}
                        input={<OutlinedInput />}
                        renderValue={(selected) => (
                            <Box sx={renderBoxSx}>
                                {lovList
                                    .filter((it) => selected.includes(it.id))
                                    .map((item, idx) => {
                                        if (multiple) {
                                            const chipProps = {} as Record<string, unknown>;
                                            if (typeof item.item === "string") {
                                                chipProps.label = item.item;
                                            } else {
                                                chipProps.label = item.item.text || "";
                                                chipProps.avatar = <Avatar src={item.item.path} />;
                                            }
                                            return (
                                                <Chip
                                                    key={item.id}
                                                    {...chipProps}
                                                    onDelete={handleDelete}
                                                    data-id={item.id}
                                                    onMouseDown={doNotPropagateEvent}
                                                />
                                            );
                                        } else if (idx === 0) {
                                            return typeof item.item === "string" ? (
                                                item.item
                                            ) : (
                                                <LovImage item={item.item} />
                                            );
                                        } else {
                                            return null;
                                        }
                                    })}
                            </Box>
                        )}
                        MenuProps={getMenuProps(width, height)}
                    >
                        {lovList.map((item) => (
                            <MenuItem key={item.id} value={item.id} style={getStyles(item.id, selectedValue, theme)}>
                                {typeof item.item === "string" ? (
                                    item.item
                                ) : (
                                    <LovImage item={item.item as TaipyImage} />
                                )}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
            ) : (
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
            )}
        </Box>
    );
};

export default Selector;
