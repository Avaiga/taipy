/*
 * Copyright 2021-2024 Avaiga Private Limited
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
    useCallback,
    SyntheticEvent,
    useState,
    useEffect,
    useMemo,
    ComponentType,
    MouseEvent,
    ChangeEvent,
} from "react";
import { TextField, Theme, alpha } from "@mui/material";
import Badge, { BadgeOrigin } from "@mui/material/Badge";
import FormControlLabel from "@mui/material/FormControlLabel";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import Switch from "@mui/material/Switch";
import Tooltip from "@mui/material/Tooltip";
import ChevronRight from "@mui/icons-material/ChevronRight";
import FlagOutlined from "@mui/icons-material/FlagOutlined";
import PushPinOutlined from "@mui/icons-material/PushPinOutlined";
import SearchOffOutlined from "@mui/icons-material/SearchOffOutlined";
import SearchOutlined from "@mui/icons-material/SearchOutlined";
import { SimpleTreeView } from "@mui/x-tree-view/SimpleTreeView";
import { TreeItem } from "@mui/x-tree-view/TreeItem";

import {
    useDispatch,
    useModule,
    getUpdateVar,
    createSendUpdateAction,
    useDispatchRequestUpdateOnFirstRender,
    createRequestUpdateAction,
    useDynamicProperty,
    ColumnDesc,
    FilterDesc,
    TableFilter,
    SortDesc,
    TableSort,
} from "taipy-gui";

import { Cycles, Cycle, DataNodes, NodeType, Scenarios, Scenario, DataNode, Sequence, Sequences } from "./utils/types";
import {
    Cycle as CycleIcon,
    Datanode as DatanodeIcon,
    Sequence as SequenceIcon,
    Scenario as ScenarioIcon,
} from "./icons";
import {
    BadgePos,
    BadgeSx,
    BaseTreeViewSx,
    FlagSx,
    ParentItemSx,
    getUpdateVarNames,
    iconLabelSx,
    tinyIconButtonSx,
    tinySelPinIconButtonSx,
} from "./utils";

export interface EditProps {
    id: string;
    active: boolean;
}

const treeSlots = { expandIcon: ChevronRight };

type Entities = Cycles | Scenarios | DataNodes;
type Entity = Cycle | Scenario | Sequence | DataNode;
type Pinned = Record<string, boolean>;

interface CoreSelectorProps {
    id?: string;
    active?: boolean;
    defaultActive?: boolean;
    updateVarName?: string;
    entities?: Entities;
    coreChanged?: Record<string, unknown>;
    updateVars: string;
    onChange?: string;
    error?: string;
    displayCycles?: boolean;
    showPrimaryFlag?: boolean;
    propagate?: boolean;
    value?: string | string[];
    defaultValue?: string;
    height: string;
    libClassName?: string;
    className?: string;
    dynamicClassName?: string;
    multiple?: boolean;
    lovPropertyName: string;
    leafType: NodeType;
    editComponent?: ComponentType<EditProps>;
    showPins?: boolean;
    onSelect?: (id: string | string[] | null) => void;
    updateCoreVars: string;
    filter?: string;
    sort?: string;
    showSearch: boolean;
}

const tinyPinIconButtonSx = (theme: Theme) => ({
    ...tinyIconButtonSx,
    backgroundColor: alpha(theme.palette.text.secondary, 0.15),
    color: "text.secondary",

    "&:hover": {
        backgroundColor: alpha(theme.palette.secondary.main, 0.75),
        color: "secondary.contrastText",
    },
});

const switchBoxSx = { ml: 2, width: (theme: Theme) => `calc(100% - ${theme.spacing(2)})` };
const iconInRowSx = { fontSize: "body2.fontSize" };
const labelInRowSx = { "& .MuiFormControlLabel-label": iconInRowSx };

const CoreItem = (props: {
    item: Entity;
    displayCycles: boolean;
    showPrimaryFlag: boolean;
    leafType: NodeType;
    editComponent?: ComponentType<EditProps>;
    pins: [Pinned, Pinned];
    onPin?: (e: MouseEvent<HTMLElement>) => void;
    hideNonPinned: boolean;
    active: boolean;
}) => {
    const [id, label, items, nodeType, primary] = props.item;
    const isPinned = props.pins[0][id];
    const isShown = props.hideNonPinned ? props.pins[1][id] : true;

    return !props.displayCycles && nodeType === NodeType.CYCLE ? (
        <>
            {items
                ? items.map((item) => (
                      <CoreItem
                          key={item[0]}
                          item={item}
                          displayCycles={false}
                          showPrimaryFlag={props.showPrimaryFlag}
                          leafType={props.leafType}
                          pins={props.pins}
                          onPin={props.onPin}
                          hideNonPinned={props.hideNonPinned}
                          active={props.active}
                      />
                  ))
                : null}
        </>
    ) : isShown ? (
        <TreeItem
            key={id}
            itemId={id}
            data-selectable={nodeType === props.leafType}
            label={
                <Grid container alignItems="center" direction="row" flexWrap="nowrap" spacing={1}>
                    <Grid item xs sx={iconLabelSx}>
                        {nodeType === NodeType.CYCLE ? (
                            <CycleIcon fontSize="small" color="primary" />
                        ) : nodeType === NodeType.SCENARIO ? (
                            props.showPrimaryFlag && primary ? (
                                <Badge
                                    badgeContent={<FlagOutlined sx={FlagSx} />}
                                    color="primary"
                                    anchorOrigin={BadgePos as BadgeOrigin}
                                    sx={BadgeSx}
                                >
                                    <ScenarioIcon fontSize="small" color="primary" />
                                </Badge>
                            ) : (
                                <ScenarioIcon fontSize="small" color="primary" />
                            )
                        ) : nodeType === NodeType.SEQUENCE ? (
                            <SequenceIcon fontSize="small" color="primary" />
                        ) : (
                            <DatanodeIcon fontSize="small" color="primary" />
                        )}
                        {label}
                    </Grid>
                    {props.editComponent && nodeType === props.leafType ? (
                        <Grid item xs="auto">
                            <props.editComponent id={id} active={props.active} />
                        </Grid>
                    ) : null}
                    {props.onPin ? (
                        <Grid item xs="auto">
                            <Tooltip title={isPinned ? "Unpin" : "Pin"}>
                                <IconButton
                                    data-id={id}
                                    data-pinned={isPinned ? "pinned" : undefined}
                                    onClick={props.onPin}
                                    size="small"
                                    sx={isPinned ? tinySelPinIconButtonSx : tinyPinIconButtonSx}
                                >
                                    <PushPinOutlined />
                                </IconButton>
                            </Tooltip>
                        </Grid>
                    ) : null}
                </Grid>
            }
            sx={nodeType === NodeType.NODE ? undefined : ParentItemSx}
        >
            {items
                ? items.map((item) => (
                      <CoreItem
                          key={item[0]}
                          item={item}
                          displayCycles={true}
                          showPrimaryFlag={props.showPrimaryFlag}
                          leafType={props.leafType}
                          editComponent={props.editComponent}
                          pins={props.pins}
                          onPin={props.onPin}
                          hideNonPinned={props.hideNonPinned}
                          active={props.active}
                      />
                  ))
                : null}
        </TreeItem>
    ) : null;
};

const findEntityAndParents = (
    id: string,
    tree: Entity[],
    parentIds: Entity[] = []
): [Entity, Entity[], string[]] | undefined => {
    for (const entity of tree) {
        if (entity[0] === id) {
            return [entity, parentIds, getChildrenIds(entity)];
        }
        if (entity[2]) {
            const res = findEntityAndParents(id, entity[2], [entity, ...parentIds]);
            if (res) {
                return res;
            }
        }
    }
};

const getChildrenIds = (entity: Entity): string[] => {
    const res: string[] = [];
    entity[2]?.forEach((child) => {
        res.push(child[0]);
        res.push(...getChildrenIds(child));
    });
    return res;
};

const getExpandedIds = (nodeId: string, exp?: string[], entities?: Entities) => {
    const ret = entities && findEntityAndParents(nodeId, entities);
    if (ret && ret[1]) {
        const res = ret[1].map((r) => r[0]);
        return exp ? [...exp, ...res] : res;
    }
    return exp || [];
};

const emptyEntity = [] as unknown as Entity;
const filterTree = (entities: Entities, search: string, leafType: NodeType, count?: { nb: number }) => {
    let top = false;
    if (!count) {
        count = { nb: 0 };
        top = true;
    }
    const filtered = entities
        .map((item) => {
            const [, label, items, nodeType] = item;
            if (nodeType !== leafType || label.toLowerCase().includes(search)) {
                const newItem = [...item];
                if (Array.isArray(items) && items.length) {
                    newItem[2] = filterTree(items, search, leafType, count) as Scenarios | DataNodes | Sequences;
                }
                return newItem as Entity;
            }
            count.nb++;
            return emptyEntity;
        })
        .filter((i) => (i as unknown[]).length !== 0);
    if (top && count.nb == 0) {
        return entities;
    }
    return filtered;
};

const localStoreSet = (val: string, ...ids: string[]) => {
    const id = ids.filter((i) => !!i).join(" ");
    if (!id) {
        return;
    }
    try {
        id && localStorage && localStorage.setItem(id, val);
    } catch (e) {
        // Too bad
    }
};

const localStoreGet = (...ids: string[]) => {
    const id = ids.filter((i) => !!i).join(" ");
    if (!id) {
        return undefined;
    }
    const val = localStorage && localStorage.getItem(id);
    if (!val) {
        return undefined;
    }
    try {
        return JSON.parse(val);
    } catch (e) {
        return undefined;
    }
};

const CoreSelector = (props: CoreSelectorProps) => {
    const {
        id = "",
        entities,
        displayCycles = true,
        showPrimaryFlag = true,
        propagate = true,
        multiple = false,
        lovPropertyName,
        leafType,
        value,
        defaultValue,
        showPins = true,
        updateVarName,
        updateVars,
        onChange,
        onSelect,
        coreChanged,
        updateCoreVars,
        showSearch,
    } = props;

    const [selectedItems, setSelectedItems] = useState<string[]>([]);
    const [pins, setPins] = useState<[Pinned, Pinned]>([{}, {}]);
    const [hideNonPinned, setShowPinned] = useState(false);
    const [expandedItems, setExpandedItems] = useState<string[]>([]);

    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const dispatch = useDispatch();
    const module = useModule();

    useDispatchRequestUpdateOnFirstRender(dispatch, id, module, updateVars, undefined, true);

    const onItemExpand = useCallback((e: SyntheticEvent, itemId: string, expanded: boolean) => {
        setExpandedItems((old) => {
            if (!expanded) {
                return old.filter((id) => id != itemId);
            }
            return [...old, itemId];
        });
    }, []);

    const onNodeSelect = useCallback(
        (e: SyntheticEvent, nodeId: string | string[] | null) => {
            const { selectable = "false" } = e.currentTarget.parentElement?.dataset || {};
            const isSelectable = selectable === "true";
            if (!isSelectable && multiple) {
                return;
            }
            setSelectedItems(() => {
                if (isSelectable) {
                    const lovVar = getUpdateVar(updateVars, lovPropertyName);
                    const val = nodeId;
                    Promise.resolve().then(
                        // to avoid set state while render react errors
                        () => dispatch(createSendUpdateAction(updateVarName, val, module, onChange, propagate, lovVar))
                    );
                    onSelect && onSelect(val);
                }
                return Array.isArray(nodeId) ? nodeId : nodeId ? [nodeId] : [];
            });
        },
        [updateVarName, updateVars, onChange, onSelect, multiple, propagate, dispatch, module, lovPropertyName]
    );

    useEffect(() => {
        if (value !== undefined && value !== null) {
            setSelectedItems(Array.isArray(value) ? value : value ? [value] : []);
            setExpandedItems((exp) => (typeof value === "string" ? getExpandedIds(value, exp, props.entities) : exp));
        } else if (defaultValue) {
            try {
                const parsedValue = JSON.parse(defaultValue);
                if (Array.isArray(parsedValue)) {
                    setSelectedItems(parsedValue);
                    if (parsedValue.length > 1) {
                        setExpandedItems((exp) => getExpandedIds(parsedValue[0], exp, props.entities));
                    }
                } else {
                    setSelectedItems([parsedValue]);
                    setExpandedItems((exp) => getExpandedIds(parsedValue, exp, props.entities));
                }
            } catch {
                setSelectedItems([defaultValue]);
                setExpandedItems((exp) => getExpandedIds(defaultValue, exp, props.entities));
            }
        } else if (value === null) {
            setSelectedItems([]);
        }
    }, [defaultValue, value, props.entities]);

    useEffect(() => {
        if (entities && !entities.length) {
            setSelectedItems((old) => {
                if (old.length) {
                    const lovVar = getUpdateVar(updateVars, lovPropertyName);
                    Promise.resolve().then(() =>
                        dispatch(
                            createSendUpdateAction(
                                updateVarName,
                                multiple ? [] : "",
                                module,
                                onChange,
                                propagate,
                                lovVar
                            )
                        )
                    );
                    return [];
                }
                return old;
            });
        }
    }, [entities, updateVars, lovPropertyName, updateVarName, multiple, module, onChange, propagate, dispatch]);

    // Refresh on broadcast
    useEffect(() => {
        if (coreChanged?.scenario) {
            const updateVar = getUpdateVar(updateVars, lovPropertyName);
            updateVar && dispatch(createRequestUpdateAction(id, module, [updateVar], true));
        }
    }, [coreChanged, updateVars, module, dispatch, id, lovPropertyName]);

    const treeViewSx = useMemo(() => ({ ...BaseTreeViewSx, maxHeight: props.height || "50vh" }), [props.height]);

    const onShowPinsChange = useCallback(() => setShowPinned((sp) => !sp), []);

    const onPin = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            if (showPins && props.entities) {
                const { id = "", pinned = "" } = e.currentTarget.dataset || {};
                if (!id) {
                    return;
                }
                const [entity = undefined, parents = [], childIds = []] =
                    findEntityAndParents(id, props.entities) || [];
                if (!entity) {
                    return;
                }
                setPins(([pins, shows]) => {
                    if (pinned === "pinned") {
                        delete pins[id];
                        delete shows[id];
                        for (const parent of parents) {
                            const pinned = ((parent[2] as Entity[]) || []).some((child) => shows[child[0]]);
                            if (!pinned) {
                                delete shows[parent[0]];
                            } else {
                                break;
                            }
                        }
                        parents.forEach((parent) => delete pins[parent[0]]);
                        childIds.forEach((cId) => {
                            delete pins[cId];
                            delete shows[cId];
                        });
                    } else {
                        pins[id] = true;
                        shows[id] = true;
                        for (const parent of parents) {
                            const nonPinned = ((parent[2] as Entity[]) || []).some((child) => !pins[child[0]]);
                            if (!nonPinned) {
                                pins[parent[0]] = true;
                            } else {
                                break;
                            }
                        }
                        parents.forEach((p) => (shows[p[0]] = true));
                        childIds.forEach((cId) => {
                            pins[cId] = true;
                            shows[cId] = true;
                        });
                    }
                    return [pins, shows];
                });
            }
        },
        [showPins, props.entities]
    );

    // filters
    const colFilters = useMemo(() => {
        try {
            const res = props.filter
                ? (JSON.parse(props.filter) as Array<[string, string, string, string[]]>)
                : undefined;
            return Array.isArray(res)
                ? res.reduce((pv, [name, id, coltype, lov], idx) => {
                      pv[name] = {
                          dfid: id,
                          title: name,
                          type: coltype,
                          index: idx,
                          filter: true,
                          lov: lov,
                          freeLov: !!lov,
                      };
                      return pv;
                  }, {} as Record<string, ColumnDesc>)
                : undefined;
        } catch (e) {
            return undefined;
        }
    }, [props.filter]);
    const [filters, setFilters] = useState<FilterDesc[]>([]);

    const applyFilters = useCallback(
        (filters: FilterDesc[]) => {
            setFilters((old) => {
                const jsonFilters = JSON.stringify(filters);
                if (old.length != filters.length || JSON.stringify(old) != jsonFilters) {
                    localStoreSet(jsonFilters, id, lovPropertyName, "filter");
                    const filterVar = getUpdateVar(updateCoreVars, "filter");
                    const lovVar = getUpdateVarNames(updateVars, lovPropertyName);
                    Promise.resolve().then(() =>
                        dispatch(
                            createRequestUpdateAction(
                                id,
                                module,
                                lovVar,
                                true,
                                filterVar ? { [filterVar]: filters } : undefined
                            )
                        )
                    );
                    return filters;
                }
                return old;
            });
        },
        [updateVars, dispatch, id, updateCoreVars, lovPropertyName, module]
    );

    // sort
    const colSorts = useMemo(() => {
        try {
            const res = props.sort ? (JSON.parse(props.sort) as Array<[string, string]>) : undefined;
            return Array.isArray(res)
                ? res.reduce((pv, [name, id], idx) => {
                      pv[name] = { dfid: id, title: name, type: "str", index: idx };
                      return pv;
                  }, {} as Record<string, ColumnDesc>)
                : undefined;
        } catch (e) {
            return undefined;
        }
    }, [props.sort]);
    const [sorts, setSorts] = useState<SortDesc[]>([]);

    const applySorts = useCallback(
        (sorts: SortDesc[]) => {
            setSorts((old) => {
                const jsonSorts = JSON.stringify(sorts);
                if (old.length != sorts.length || JSON.stringify(old) != jsonSorts) {
                    localStoreSet(jsonSorts, id, lovPropertyName, "sort");
                    const sortVar = getUpdateVar(updateCoreVars, "sort");
                    dispatch(
                        createRequestUpdateAction(
                            id,
                            module,
                            getUpdateVarNames(updateVars, lovPropertyName),
                            true,
                            sortVar ? { [sortVar]: sorts } : undefined
                        )
                    );
                    return sorts;
                }
                return old;
            });
        },
        [updateVars, dispatch, id, updateCoreVars, lovPropertyName, module]
    );

    useEffect(() => {
        if (lovPropertyName) {
            if (colFilters) {
                const filters = localStoreGet(id, lovPropertyName, "filter") as FilterDesc[];
                filters &&
                    applyFilters(filters.filter((fd) => Object.values(colFilters).some((cd) => cd.dfid === fd.col)));
            }
            if (colSorts) {
                const sorts = localStoreGet(id, lovPropertyName, "sort") as SortDesc[];
                sorts && applySorts(sorts.filter((fd) => Object.values(colSorts).some((cd) => cd.dfid === fd.col)));
            }
        }
    }, [id, colFilters, colSorts, lovPropertyName, applyFilters, applySorts]);

    // Search
    const [searchValue, setSearchValue] = useState("");
    const onSearch = useCallback((e: ChangeEvent<HTMLInputElement>) => setSearchValue(e.currentTarget.value), []);
    const foundEntities = useMemo(() => {
        if (!entities || searchValue === "") {
            return entities;
        }
        return filterTree(entities, searchValue.toLowerCase(), props.leafType);
    }, [entities, searchValue, props.leafType]);
    const [revealSearch, setRevealSearch] = useState(false);
    const onRevealSearch = useCallback(() => {
        setRevealSearch((r) => !r);
        setSearchValue("");
    }, []);

    return (
        <>
            <Grid container sx={switchBoxSx} gap={1}>
                {active && colFilters ? (
                    <Grid item>
                        <TableFilter
                            columns={colFilters}
                            appliedFilters={filters}
                            filteredCount={0}
                            onValidate={applyFilters}
                        ></TableFilter>
                    </Grid>
                ) : null}
                {active && colSorts ? (
                    <Grid item>
                        <TableSort columns={colSorts} appliedSorts={sorts} onValidate={applySorts}></TableSort>
                    </Grid>
                ) : null}
                {showSearch ? (
                    <Grid item>
                        <IconButton onClick={onRevealSearch} size="small" sx={iconInRowSx}>
                            {revealSearch ? (
                                <SearchOffOutlined fontSize="inherit" />
                            ) : (
                                <SearchOutlined fontSize="inherit" />
                            )}
                        </IconButton>
                    </Grid>
                ) : null}
                {showPins ? (
                    <Grid item>
                        <FormControlLabel
                            control={
                                <Switch
                                    onChange={onShowPinsChange}
                                    checked={hideNonPinned}
                                    disabled={!hideNonPinned && !Object.keys(pins[0]).length}
                                    size="small"
                                />
                            }
                            label="Pinned only"
                            sx={labelInRowSx}
                        />
                    </Grid>
                ) : null}
                {showSearch && revealSearch ? (
                    <Grid item xs={12}>
                        <TextField
                            margin="dense"
                            value={searchValue}
                            onChange={onSearch}
                            fullWidth
                            label="Search"
                        ></TextField>
                    </Grid>
                ) : null}
            </Grid>
            <SimpleTreeView
                slots={treeSlots}
                sx={treeViewSx}
                onSelectedItemsChange={onNodeSelect}
                selectedItems={selectedItems}
                multiSelect={multiple}
                expandedItems={expandedItems}
                onItemExpansionToggle={onItemExpand}
            >
                {foundEntities
                    ? foundEntities.map((item) =>
                          item ? (
                              <CoreItem
                                  key={item[0]}
                                  item={item}
                                  displayCycles={displayCycles}
                                  showPrimaryFlag={showPrimaryFlag}
                                  leafType={leafType}
                                  editComponent={props.editComponent}
                                  onPin={showPins ? onPin : undefined}
                                  pins={pins}
                                  hideNonPinned={hideNonPinned}
                                  active={!!active}
                              />
                          ) : null
                      )
                    : null}
            </SimpleTreeView>
        </>
    );
};

export default CoreSelector;
