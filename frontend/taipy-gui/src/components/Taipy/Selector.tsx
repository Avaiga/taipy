/*
 * Copyright 2021-2025 Avaiga Private Limited
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

import React, {
    ChangeEvent,
    CSSProperties,
    HTMLAttributes,
    MouseEvent,
    ReactNode,
    SyntheticEvent,
    useCallback,
    useEffect,
    useMemo,
    useRef,
    useState,
} from "react";
import Autocomplete, { AutocompleteRenderInputParams } from "@mui/material/Autocomplete";
import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import Checkbox from "@mui/material/Checkbox";
import Chip from "@mui/material/Chip";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormGroup from "@mui/material/FormGroup";
import FormLabel from "@mui/material/FormLabel";
import InputLabel from "@mui/material/InputLabel";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import ListItemAvatar from "@mui/material/ListItemAvatar";
import MenuItem from "@mui/material/MenuItem";
import OutlinedInput from "@mui/material/OutlinedInput";
import Paper from "@mui/material/Paper";
import Tooltip from "@mui/material/Tooltip";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import TextField from "@mui/material/TextField";
import { Theme, useTheme } from "@mui/material";

import { doNotPropagateEvent, expandSx, getCssSize, getSuffixedClassNames, getUpdateVar } from "./utils";
import { createSendActionNameAction, createSendUpdateAction } from "../../context/taipyReducers";
import { ItemProps, LovImage, paperBaseSx, SelTreeProps, showItem, SingleItem, useLovListMemo } from "./lovUtils";
import {
    useClassNames,
    useDispatch,
    useDispatchRequestUpdateOnFirstRender,
    useDynamicDictProperty,
    useDynamicProperty,
    useModule,
} from "../../utils/hooks";
import { Icon } from "../../utils/icon";
import { LovItem } from "../../utils/lov";
import { getComponentClassName } from "./TaipyStyle";
import { draggedSx, droppableSx, useDrag, useDrop } from "./dndUtils";

interface SelectAllProps {
    multiple: boolean;
    showSelectAll: boolean;
    selectedValueLength: number;
    lovListLength: number;
    active?: boolean;
    handleCheckAllChange: (event: SelectChangeEvent<HTMLInputElement>, checked: boolean) => void;
}

const SelectAll = ({
    multiple,
    showSelectAll,
    selectedValueLength,
    lovListLength,
    active,
    handleCheckAllChange,
}: SelectAllProps) =>
    multiple && showSelectAll ? (
        <Tooltip title={selectedValueLength == lovListLength ? "Deselect All" : "Select All"}>
            <Checkbox
                disabled={!active}
                indeterminate={selectedValueLength > 0 && selectedValueLength < lovListLength}
                checked={selectedValueLength == lovListLength}
                onChange={handleCheckAllChange}
            ></Checkbox>
        </Tooltip>
    ) : null;

const MultipleItem = ({
    value,
    clickHandler,
    selectedValue,
    item,
    disabled,
    dragType,
    dragVarName,
    sourceId,
    onDrop,
    dropTypes,
    draggedData: dragData,
}: ItemProps) => {
    const itemRef = useRef<HTMLDivElement>(null);
    const [isDragging] = useDrag(itemRef, dragType, dragData, value, dragVarName, sourceId);
    const [isDraggedOver] = useDrop(itemRef, dropTypes, value, onDrop);

    return (
        <ListItemButton
            onClick={clickHandler}
            data-id={value}
            dense
            disabled={disabled}
            sx={isDragging ? draggedSx : isDraggedOver ? droppableSx : undefined}
        >
            <ListItemIcon>
                <Checkbox
                    disabled={disabled}
                    edge="start"
                    checked={selectedValue.includes(value)}
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
};

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const getMenuProps = (height?: string | number) => ({
    PaperProps: {
        style: {
            maxHeight: height || ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
        },
    },
});

const getStyles = (id: string, ids: readonly string[], theme: Theme) => ({
    fontWeight: ids.indexOf(id) === -1 ? theme.typography.fontWeightRegular : theme.typography.fontWeightMedium,
});

const getOptionLabel = (option: LovItem) => (typeof option.item === "string" ? option.item : option.item?.text) || "";
const getOptionKey = (option: LovItem) => `${option.id}`;
const isOptionEqualToValue = (option: LovItem, value: LovItem) => option.id == value.id;
const renderOption = (props: HTMLAttributes<HTMLLIElement>, option: LovItem) => (
    <li {...props} key={option.id}>
        {typeof option.item === "string" ? option.item : <LovImage item={option.item} />}
    </li>
);

const getLovItemsFromStr = (value: string | string[] | undefined, lovList: LovItem[], multiple: boolean) => {
    const val = multiple
        ? Array.isArray(value)
            ? value
            : [value]
        : Array.isArray(value) && value.length
          ? value[0]
          : value;
    return Array.isArray(val)
        ? (val.map((v) => lovList.find((item) => item.id == "" + v)).filter((i) => i) as LovItem[])
        : (val && lovList.find((item) => item.id == "" + val)) || null;
};

const renderBoxSx = {
    display: "flex",
    flexWrap: "wrap",
    gap: 0.5,
    width: "100%",
} as CSSProperties;

interface SelectorProps extends SelTreeProps {
    dropdown?: boolean;
    mode?: string;
    selectionMessage?: string;
    defaultSelectionMessage?: string;
    showSelectAll?: boolean;
}

const Selector = (props: SelectorProps) => {
    const {
        id,
        defaultValue = "",
        value,
        updateVarName = "",
        defaultLov = "",
        filter = false,
        propagate = true,
        lov,
        updateVars = "",
        width = "100%",
        height,
        valueById,
        mode = "",
        showSelectAll = false,
    } = props;
    const [searchValue, setSearchValue] = useState("");
    const [selectedValue, setSelectedValue] = useState<string[]>([]);
    const dispatch = useDispatch();
    const module = useModule();
    const theme = useTheme();
    const listRef = useRef<HTMLUListElement>(null);

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);
    const selectionMessage = useDynamicProperty(props.selectionMessage, props.defaultSelectionMessage, undefined);

    useDispatchRequestUpdateOnFirstRender(dispatch, id, module, updateVars, updateVarName);

    const isRadio = mode && mode.toLocaleLowerCase() == "radio";
    const isCheck = mode && mode.toLocaleLowerCase() == "check";
    const dropdown = isRadio || isCheck || props.dropdown === undefined ? false : props.dropdown;
    const multiple = isCheck ? true : isRadio || props.multiple === undefined ? false : props.multiple;

    const lovList = useLovListMemo(lov, defaultLov);
    const lovVarName = useMemo(() => getUpdateVar(updateVars, "lov"), [updateVars]);

    const dragData = useDynamicDictProperty(
        props.dragData,
        props.defaultDragData || "",
        undefined as Record<string, unknown> | undefined,
    );
    const dropData = useDynamicDictProperty(
        props.dropData,
        props.defaultDropData || "",
        undefined as Record<string, unknown> | undefined,
    );
    const dropTypes = useMemo(() => {
        if (props.allowedDragTypes) {
            try {
                const drops = JSON.parse(props.allowedDragTypes);
                if (Array.isArray(drops) && drops.length) {
                    return drops as string[];
                }
            } catch (e) {
                console.error("Error parsing dropTypes:", e);
            }
        }
        return undefined;
    }, [props.allowedDragTypes]);

    const dropHandler = useCallback(
        (
            sourceId?: string,
            sourceItemId?: string,
            sourceData?: Record<string, unknown>,
            sourceVarName?: string,
            targetItemId?: string,
        ) => {
            dispatch(
                createSendActionNameAction(id, module, {
                    action: props.onAction,
                    reason: "drop",
                    source_id: sourceId,
                    source_item_id: sourceItemId,
                    source_data: sourceData,
                    source_var_name: sourceVarName,
                    target_id: id,
                    target_item_id: targetItemId,
                    target_data: dropData,
                    target_var_name: lovVarName,
                }),
            );
        },
        [props.onAction, dispatch, module, id, lovVarName, dropData],
    );

    const [isDraggedOver] = useDrop(listRef, dropTypes, undefined, dropHandler);

    const listSx = useMemo(
        () =>
            expandSx(
                { bgcolor: "transparent", overflowY: "auto", width: "100%", maxWidth: width },
                isDraggedOver ? droppableSx : undefined,
            ),
        [width, isDraggedOver],
    );
    const heightSx = useMemo(() => {
        if (!height) {
            return undefined;
        }
        return {
            maxHeight: height,
            display: "flex",
            flexFlow: "column nowrap",
            overflowY: "auto",
        };
    }, [height]);

    const paperSx = useMemo(() => {
        let sx = paperBaseSx;
        if (height !== undefined) {
            sx = { ...sx, maxHeight: height };
        }
        return sx;
    }, [height]);

    const controlSx = useMemo(
        () => ({
            my: 1,
            mx: 0,
            width: getCssSize(width),
            maxWidth: "unset",
            "& .MuiInputBase-root": { minHeight: 48, "& input": { minHeight: "unset" } },
        }),
        [width],
    );

    const autoCompleteSx = useMemo(
        () => ({
            my: 1,
            mx: 0,
            width: getCssSize(width),
            "& .MuiFormControl-root": {
                maxWidth: "unset",
                my: 0,
                "& .MuiInputBase-root": { minHeight: 48, "& input": { minHeight: "unset" } },
            },
        }),
        [width],
    );

    useEffect(() => {
        if (value !== undefined && value !== null) {
            setSelectedValue(Array.isArray(value) ? value.map((v) => "" + v) : ["" + value]);
            setAutoValue(getLovItemsFromStr(value, lovList, multiple));
        } else if (defaultValue) {
            let parsedValue;
            try {
                parsedValue = JSON.parse(defaultValue);
            } catch {
                parsedValue = defaultValue;
            }
            setSelectedValue(Array.isArray(parsedValue) ? parsedValue : [parsedValue]);
            setAutoValue(getLovItemsFromStr(parsedValue, lovList, multiple));
        }
    }, [defaultValue, value, lovList, multiple]);

    const selectHandler = useCallback(
        (key: string) => {
            setSelectedValue((keys) => {
                if (multiple) {
                    const newKeys = [...keys];
                    const p = newKeys.indexOf(key);
                    if (p === -1) {
                        newKeys.push(key);
                    } else {
                        newKeys.splice(p, 1);
                    }
                    dispatch(
                        createSendUpdateAction(
                            updateVarName,
                            newKeys,
                            module,
                            props.onChange,
                            propagate,
                            valueById ? undefined : lovVarName,
                        ),
                    );
                    return newKeys;
                } else {
                    dispatch(
                        createSendUpdateAction(
                            updateVarName,
                            key,
                            module,
                            props.onChange,
                            propagate,
                            valueById ? undefined : lovVarName,
                        ),
                    );
                    return [key];
                }
            });
        },
        [updateVarName, dispatch, multiple, propagate, lovVarName, valueById, props.onChange, module],
    );

    const clickHandler = useCallback(
        (evt: MouseEvent<HTMLElement>) => {
            if (active) {
                const { id: key = "" } = evt.currentTarget.dataset;
                selectHandler(key);
            }
        },
        [active, selectHandler],
    );

    const changeHandler = useCallback(
        (evt: ChangeEvent<HTMLInputElement>) => {
            if (active) {
                const { id: key = "" } = (evt.currentTarget as HTMLElement).parentElement?.dataset || {};
                selectHandler(key);
            }
        },
        [active, selectHandler],
    );

    const handleChange = useCallback(
        (event: SelectChangeEvent<typeof selectedValue>) => {
            const {
                target: { value },
            } = event;
            setSelectedValue(Array.isArray(value) ? value : [value]);
            dispatch(
                createSendUpdateAction(
                    updateVarName,
                    value,
                    module,
                    props.onChange,
                    propagate,
                    valueById ? undefined : lovVarName,
                ),
            );
        },
        [dispatch, updateVarName, propagate, lovVarName, valueById, props.onChange, module],
    );

    const handleCheckAllChange = useCallback(
        (event: SelectChangeEvent<HTMLInputElement>, checked: boolean) => {
            const sel = checked ? lovList.map((elt) => elt.id) : [];
            setSelectedValue(sel);
            dispatch(
                createSendUpdateAction(
                    updateVarName,
                    sel,
                    module,
                    props.onChange,
                    propagate,
                    valueById ? undefined : lovVarName,
                ),
            );
        },
        [lovList, dispatch, updateVarName, propagate, lovVarName, valueById, props.onChange, module],
    );

    const [autoValue, setAutoValue] = useState<LovItem | LovItem[] | null>(() => (multiple ? [] : null));
    const handleAutoChange = useCallback(
        (event: SyntheticEvent, sel: LovItem | LovItem[] | null) => {
            setAutoValue(sel);
            setSelectedValue(Array.isArray(sel) ? sel.map((item) => item.id) : sel ? [sel.id] : []);
            dispatch(
                createSendUpdateAction(
                    updateVarName,
                    Array.isArray(sel) ? sel.map((item) => item.id) : sel?.id,
                    module,
                    props.onChange,
                    propagate,
                    valueById ? undefined : lovVarName,
                ),
            );
        },
        [dispatch, updateVarName, propagate, lovVarName, valueById, props.onChange, module],
    );
    const handleCheckAllAutoChange = useCallback(
        (event: SelectChangeEvent<HTMLInputElement>, checked: boolean) => {
            const sel = checked ? lovList.slice() : [];
            const ids = sel.map((elt) => elt.id);
            setAutoValue(sel);
            setSelectedValue(ids);
            dispatch(
                createSendUpdateAction(
                    updateVarName,
                    ids,
                    module,
                    props.onChange,
                    propagate,
                    valueById ? undefined : lovVarName,
                ),
            );
        },
        [lovList, dispatch, updateVarName, propagate, lovVarName, valueById, props.onChange, module],
    );
    const renderAutoInput = useCallback(
        (params: AutocompleteRenderInputParams) => {
            if (params.InputProps) {
                if (selectionMessage) {
                    params.InputProps.startAdornment = [<Chip key="selectionMessage" label={selectionMessage}></Chip>];
                } else {
                    if (!params.InputProps.startAdornment) {
                        params.InputProps.startAdornment = [];
                    } else if (!Array.isArray(params.InputProps.startAdornment)) {
                        params.InputProps.startAdornment = [params.InputProps.startAdornment];
                    }
                }
                // will need to move to slotProps { input: { startAdornment: (
                (params.InputProps.startAdornment as Array<ReactNode>).unshift(
                    <SelectAll
                        multiple={multiple}
                        showSelectAll={showSelectAll}
                        selectedValueLength={selectedValue.length}
                        lovListLength={lovList.length}
                        active={active}
                        handleCheckAllChange={handleCheckAllAutoChange}
                        key="selectAll"
                    />,
                );
            } else {
                console.log("selector autocomplete needs to update params for slotProps.input.startAdornment\nrenderAutoInput", params);
            }
            return <TextField {...params} label={props.label} margin="dense" />;
        },
        [
            selectionMessage,
            props.label,
            multiple,
            showSelectAll,
            selectedValue.length,
            lovList.length,
            active,
            handleCheckAllAutoChange,
        ],
    );

    const handleDelete = useCallback(
        (event: React.SyntheticEvent) => {
            const id = event.currentTarget?.parentElement?.getAttribute("data-id");
            id &&
                setSelectedValue((oldKeys) => {
                    const keys = oldKeys.filter((valId) => valId !== id);
                    dispatch(
                        createSendUpdateAction(
                            updateVarName,
                            keys,
                            module,
                            props.onChange,
                            propagate,
                            valueById ? undefined : lovVarName,
                        ),
                    );
                    return keys;
                });
        },
        [updateVarName, propagate, dispatch, lovVarName, valueById, props.onChange, module],
    );

    const handleInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => setSearchValue(e.target.value), []);

    // Handle Enter key in filter input: select all filtered options in multi-select mode
    const handleFilterInputKeyDown = useCallback(
        (e: React.KeyboardEvent<HTMLInputElement>) => {
            if (e.key === "Enter" && multiple && filter) {
                // Find filtered items
                const filtered = lovList.filter((elt) => showItem(elt, searchValue));
                const filteredIds = filtered.map((elt) => elt.id);
                setSelectedValue(filteredIds);
                dispatch(
                    createSendUpdateAction(
                        updateVarName,
                        filteredIds,
                        module,
                        props.onChange,
                        propagate,
                        valueById ? undefined : lovVarName,
                    ),
                );
                e.preventDefault();
                e.stopPropagation();
            }
        },
        [
            multiple,
            filter,
            lovList,
            searchValue,
            setSelectedValue,
            dispatch,
            updateVarName,
            module,
            props.onChange,
            propagate,
            valueById,
            lovVarName,
        ],
    );

    const dropdownValue = ((dropdown || isRadio) &&
        (multiple ? selectedValue : selectedValue.length ? selectedValue[0] : "")) as string[];

    return (
        <>
            {isRadio || isCheck ? (
                <FormControl sx={controlSx} className={`${className} ${getComponentClassName(props.children)}`}>
                    {props.label ? <FormLabel>{props.label}</FormLabel> : null}
                    <Tooltip title={hover || ""}>
                        {isRadio ? (
                            <RadioGroup
                                value={dropdownValue}
                                onChange={handleChange}
                                className={getSuffixedClassNames(className, "-radio-group")}
                                sx={heightSx}
                            >
                                {lovList.map((item) => (
                                    <FormControlLabel
                                        key={item.id}
                                        value={item.id}
                                        control={<Radio />}
                                        label={
                                            typeof item.item === "string" ? (
                                                item.item
                                            ) : (
                                                <LovImage item={item.item as Icon} />
                                            )
                                        }
                                        style={getStyles(item.id, selectedValue, theme)}
                                        disabled={!active}
                                    />
                                ))}
                            </RadioGroup>
                        ) : (
                            <FormGroup className={getSuffixedClassNames(className, "-check-group")} sx={heightSx}>
                                {lovList.map((item) => (
                                    <FormControlLabel
                                        key={item.id}
                                        control={
                                            <Checkbox
                                                data-id={item.id}
                                                checked={selectedValue.includes(item.id)}
                                                onChange={changeHandler}
                                            />
                                        }
                                        label={
                                            typeof item.item === "string" ? (
                                                item.item
                                            ) : (
                                                <LovImage item={item.item as Icon} />
                                            )
                                        }
                                        style={getStyles(item.id, selectedValue, theme)}
                                        disabled={!active}
                                    ></FormControlLabel>
                                ))}
                            </FormGroup>
                        )}
                    </Tooltip>
                </FormControl>
            ) : dropdown ? (
                filter ? (
                    <Tooltip title={hover || ""} placement="top">
                        <Autocomplete
                            id={id}
                            disabled={!active}
                            multiple={multiple}
                            options={lovList}
                            value={autoValue}
                            onChange={handleAutoChange}
                            getOptionLabel={getOptionLabel}
                            getOptionKey={getOptionKey}
                            isOptionEqualToValue={isOptionEqualToValue}
                            sx={autoCompleteSx}
                            className={`${className} ${getComponentClassName(props.children)}`}
                            renderInput={renderAutoInput}
                            renderOption={renderOption}
                        />
                    </Tooltip>
                ) : (
                    <FormControl sx={controlSx} className={`${className} ${getComponentClassName(props.children)}`}>
                        {props.label ? <InputLabel disableAnimation>{props.label}</InputLabel> : null}
                        <Tooltip title={hover || ""} placement="top">
                            <Select
                                id={id}
                                multiple={multiple}
                                value={dropdownValue}
                                onChange={handleChange}
                                input={
                                    <OutlinedInput
                                        label={props.label}
                                        startAdornment={
                                            <SelectAll
                                                multiple={multiple}
                                                showSelectAll={showSelectAll}
                                                selectedValueLength={selectedValue.length}
                                                lovListLength={lovList.length}
                                                active={active}
                                                handleCheckAllChange={handleCheckAllChange}
                                            />
                                        }
                                    />
                                }
                                disabled={!active}
                                renderValue={(selected) => (
                                    <Box sx={renderBoxSx}>
                                        {typeof selectionMessage === "string" ? (
                                            <Chip key="selectionMessage" label={selectionMessage} />
                                        ) : (
                                            lovList
                                                .filter((it) =>
                                                    Array.isArray(selected)
                                                        ? selected.includes(it.id)
                                                        : selected === it.id,
                                                )
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
                                                                disabled={!active}
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
                                                })
                                        )}
                                    </Box>
                                )}
                                MenuProps={getMenuProps(height)}
                            >
                                {lovList.map((item) => (
                                    <MenuItem
                                        key={item.id}
                                        value={item.id}
                                        style={getStyles(item.id, selectedValue, theme)}
                                        disabled={item.id === null}
                                    >
                                        {typeof item.item === "string" ? (
                                            item.item
                                        ) : (
                                            <LovImage item={item.item as Icon} />
                                        )}
                                    </MenuItem>
                                ))}
                            </Select>
                        </Tooltip>
                    </FormControl>
                )
            ) : (
                <FormControl sx={controlSx} className={`${className} ${getComponentClassName(props.children)}`}>
                    {props.label ? (
                        <InputLabel disableAnimation className="static-label">
                            {props.label}
                        </InputLabel>
                    ) : null}
                    <Tooltip title={hover || ""}>
                        <Paper sx={paperSx}>
                            {filter ? (
                                <Box>
                                    <OutlinedInput
                                        margin="dense"
                                        placeholder="Search field"
                                        value={searchValue}
                                        onChange={handleInput}
                                        onKeyDown={handleFilterInputKeyDown}
                                        disabled={!active}
                                        startAdornment={
                                            multiple && showSelectAll ? (
                                                <Tooltip
                                                    title={
                                                        selectedValue.length == lovList.length
                                                            ? "Deselect All"
                                                            : "Select All"
                                                    }
                                                >
                                                    <Checkbox
                                                        disabled={!active}
                                                        indeterminate={
                                                            selectedValue.length > 0 &&
                                                            selectedValue.length < lovList.length
                                                        }
                                                        checked={selectedValue.length == lovList.length}
                                                        onChange={handleCheckAllChange}
                                                    ></Checkbox>
                                                </Tooltip>
                                            ) : null
                                        }
                                    />
                                </Box>
                            ) : multiple && showSelectAll ? (
                                <Box paddingLeft={1}>
                                    <FormControlLabel
                                        control={
                                            <Checkbox
                                                disabled={!active}
                                                indeterminate={
                                                    selectedValue.length > 0 && selectedValue.length < lovList.length
                                                }
                                                checked={selectedValue.length == lovList.length}
                                                onChange={handleCheckAllChange}
                                            ></Checkbox>
                                        }
                                        label={selectedValue.length == lovList.length ? "Deselect All" : "Select All"}
                                    />
                                </Box>
                            ) : null}
                            <List sx={listSx} id={id} ref={listRef}>
                                {lovList
                                    .filter((elt) => showItem(elt, searchValue))
                                    .map((elt) =>
                                        multiple ? (
                                            <MultipleItem
                                                key={elt.id}
                                                value={elt.id}
                                                item={elt.item}
                                                selectedValue={selectedValue}
                                                clickHandler={clickHandler}
                                                disabled={!active}
                                                dragType={props.dragType}
                                                dropTypes={dropTypes}
                                                dragVarName={lovVarName}
                                                sourceId={props.id}
                                                onDrop={dropHandler}
                                                draggedData={dragData}
                                            />
                                        ) : (
                                            <SingleItem
                                                key={elt.id}
                                                value={elt.id}
                                                item={elt.item}
                                                selectedValue={selectedValue}
                                                clickHandler={clickHandler}
                                                disabled={!active}
                                                dragType={props.dragType}
                                                dropTypes={dropTypes}
                                                dragVarName={lovVarName}
                                                sourceId={props.id}
                                                onDrop={dropHandler}
                                                draggedData={dragData}
                                            />
                                        ),
                                    )}
                            </List>
                        </Paper>
                    </Tooltip>
                </FormControl>
            )}
            {props.children}
        </>
    );
};

export default Selector;
