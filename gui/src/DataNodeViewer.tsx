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

import React, { useState, useCallback, useEffect, useMemo, ChangeEvent, SyntheticEvent, MouseEvent } from "react";
import Accordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
import Box from "@mui/material/Box";
import Checkbox from "@mui/material/Checkbox";
import Divider from "@mui/material/Divider";
import FormControl from "@mui/material/FormControl";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import InputLabel from "@mui/material/InputLabel";
import ListItemText from "@mui/material/ListItemText";
import MenuItem from "@mui/material/MenuItem";
import OutlinedInput from "@mui/material/OutlinedInput";
import Popover from "@mui/material/Popover";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import Switch from "@mui/material/Switch";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import {
    CheckCircle,
    Cancel,
    ArrowForwardIosSharp,
    Launch,
    TableChartOutlined,
    BarChartOutlined,
} from "@mui/icons-material";
import { DateTimePicker } from "@mui/x-date-pickers/DateTimePicker";
import { BaseDateTimePickerSlotsComponentsProps } from "@mui/x-date-pickers/DateTimePicker/shared";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { format } from "date-fns";

import {
    ColumnDesc,
    RowValue,
    Table,
    TableValueType,
    createRequestUpdateAction,
    createSendActionNameAction,
    getUpdateVar,
    useDispatch,
    useDynamicProperty,
    useModule,
} from "taipy-gui";

import { Cycle as CycleIcon, Scenario as ScenarioIcon } from "./icons";
import {
    AccordionIconSx,
    AccordionSummarySx,
    FieldNoMaxWidth,
    IconPaddingSx,
    MainBoxSx,
    hoverSx,
    iconLabelSx,
    popoverOrigin,
    tinySelPinIconButtonSx,
    useClassNames,
} from "./utils";
import PropertiesEditor from "./PropertiesEditor";
import { NodeType, Scenarios } from "./utils/types";
import CoreSelector from "./CoreSelector";
import { useUniqueId } from "./utils/hooks";
import { ToggleButton, ToggleButtonGroup } from "@mui/material";
import DataNodeChart from "./DataNodeChart";

const editTimestampFormat = "YYY/MM/dd HH:mm";

const tabBoxSx = { borderBottom: 1, borderColor: "divider" };
const noDisplay = { display: "none" };
const gridSx = { mt: 0 };
const editSx = {
    borderRight: 1,
    color: "secondary.main",
    fontSize: "smaller",
    "& > div": { writingMode: "vertical-rl", transform: "rotate(180deg)", paddingBottom: "1em" },
};
const textFieldProps = { textField: { margin: "dense" } } as BaseDateTimePickerSlotsComponentsProps<Date>;

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
    PaperProps: {
        style: {
            maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
            width: 250,
        },
    },
};
const colsSelectSx = { m: 1, width: 300 };

type DataNodeFull = [string, string, string, string, string, string, string, string, number, Array<[string, string]>];

enum DataNodeFullProps {
    id,
    type,
    config_id,
    last_edit_date,
    expiration_date,
    label,
    ownerId,
    ownerLabel,
    ownerType,
    properties,
}
const DataNodeFullLength = Object.keys(DataNodeFullProps).length / 2;

type DatanodeData = [RowValue, string | null, boolean | null, string | null];
enum DatanodeDataProps {
    value,
    type,
    tabular,
    error,
}

interface DataNodeViewerProps {
    id?: string;
    expandable?: boolean;
    expanded?: boolean;
    updateVarName?: string;
    updateVars: string;
    defaultDataNode?: string;
    dataNode?: DataNodeFull | Array<DataNodeFull>;
    onEdit?: string;
    onIdSelect?: string;
    error?: string;
    coreChanged?: Record<string, unknown>;
    defaultActive: boolean;
    active: boolean;
    showConfig?: boolean;
    showOwner?: boolean;
    showEditDate?: boolean;
    showExpirationDate?: boolean;
    showProperties?: boolean;
    showHistory?: boolean;
    showData?: boolean;
    chartConfigs?: string;
    libClassName?: string;
    className?: string;
    dynamicClassName?: string;
    scenarios?: Scenarios;
    history?: Array<[string, string, string]>;
    data?: DatanodeData;
    tabularData?: TableValueType;
    tabularColumns?: string;
    onDataValue?: string;
    onTabularDataEdit?: string;
    chartConfig?: string;
}

const getDataValue = (value?: RowValue, dType?: string | null) => (dType == "date" ? new Date(value as string) : value);

const getValidDataNode = (datanode: DataNodeFull | DataNodeFull[]) =>
    datanode.length == DataNodeFullLength && typeof datanode[DataNodeFullProps.id] === "string"
        ? (datanode as DataNodeFull)
        : datanode.length == 1
        ? (datanode[0] as DataNodeFull)
        : undefined;

const TableViewType = "table";

const DataNodeViewer = (props: DataNodeViewerProps) => {
    const {
        id = "",
        expandable = true,
        expanded = true,
        showConfig = false,
        showOwner = true,
        showEditDate = false,
        showExpirationDate = false,
        showProperties = true,
        showHistory = true,
        showData = true,
    } = props;

    const dispatch = useDispatch();
    const module = useModule();
    const uniqid = useUniqueId(id);

    const [
        dnId,
        dnType,
        dnConfig,
        dnEditDate,
        dnExpirationDate,
        dnLabel,
        dnOwnerId,
        dnOwnerLabel,
        dnOwnerType,
        dnProperties,
        isDataNode,
    ] = useMemo(() => {
        let dn: DataNodeFull | undefined = undefined;
        if (Array.isArray(props.dataNode)) {
            dn = getValidDataNode(props.dataNode);
        } else if (props.defaultDataNode) {
            try {
                dn = getValidDataNode(JSON.parse(props.defaultDataNode));
            } catch {
                // DO nothing
            }
        }
        return dn ? [...dn, true] : ["", "", "", "", "", "", "", "", -1, [], false];
    }, [props.dataNode, props.defaultDataNode]);

    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);

    // history & data
    const [historyRequested, setHistoryRequested] = useState(false);
    const [dataRequested, setDataRequested] = useState(false);

    // userExpanded
    const [userExpanded, setUserExpanded] = useState(isDataNode && expanded);
    const onExpand = useCallback(
        (e: SyntheticEvent, expand: boolean) => expandable && setUserExpanded(expand),
        [expandable]
    );

    // focus
    const [focusName, setFocusName] = useState("");
    const onFocus = useCallback((e: MouseEvent<HTMLElement>) => {
        e.stopPropagation();
        setFocusName(e.currentTarget.dataset.focus || "");
    }, []);

    // Label
    const [label, setLabel] = useState<string>();
    const editLabel = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            if (isDataNode) {
                dispatch(createSendActionNameAction(id, module, props.onEdit, { id: dnId, name: label }));
                setFocusName("");
            }
        },
        [isDataNode, props.onEdit, dnId, label, id, dispatch, module]
    );
    const cancelLabel = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            setLabel(dnLabel);
            setFocusName("");
        },
        [dnLabel, setLabel, setFocusName]
    );
    const onLabelChange = useCallback((e: ChangeEvent<HTMLInputElement>) => setLabel(e.target.value), []);

    // scenarios
    const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
    const showScenarios = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            if (isDataNode) {
                dispatch(createSendActionNameAction(id, module, props.onIdSelect, { owner_id: dnOwnerId }));
                setAnchorEl(e.currentTarget);
            }
        },
        [dnOwnerId, dispatch, id, isDataNode, module, props.onIdSelect]
    );
    const handleClose = useCallback(() => setAnchorEl(null), []);
    const scenarioUpdateVars = useMemo(
        () => [getUpdateVar(props.updateVars, "scenario"), getUpdateVar(props.updateVars, "scenarios")],
        [props.updateVars]
    );

    // on datanode change
    useEffect(() => {
        setLabel(dnLabel);
        setUserExpanded(expanded && isDataNode);
        setTabValue(0);
        setHistoryRequested(false);
        setDataRequested(false);
        setViewType(TableViewType);
    }, [dnLabel, isDataNode, expanded]);

    // Datanode data
    const dtValue = (props.data && props.data[DatanodeDataProps.value]) ?? undefined;
    const dtType = props.data && props.data[DatanodeDataProps.type];
    const dtTabular = (props.data && props.data[DatanodeDataProps.tabular]) ?? false;
    const dtError = props.data && props.data[DatanodeDataProps.error];
    const [dataValue, setDataValue] = useState<RowValue | Date>();
    const editDataValue = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            if (isDataNode) {
                dispatch(
                    createSendActionNameAction(id, module, props.onDataValue, {
                        id: dnId,
                        value: dataValue,
                        type: dtType,
                    })
                );
                setFocusName("");
            }
        },
        [isDataNode, props.onDataValue, dnId, dataValue, dtType, id, dispatch, module]
    );
    const cancelDataValue = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            setDataValue(getDataValue(dtValue, dtType));
            setFocusName("");
        },
        [dtValue, dtType, setDataValue, setFocusName]
    );
    const onDataValueChange = useCallback((e: ChangeEvent<HTMLInputElement>) => setDataValue(e.target.value), []);
    const onDataValueDateChange = useCallback((d: Date | null) => d && setDataValue(d), []);
    useEffect(() => {
        if (dtValue !== undefined) {
            setDataValue(getDataValue(dtValue, dtType));
        }
    }, [dtValue, dtType]);

    // Refresh on broadcast
    useEffect(() => {
        const ids = props.coreChanged?.datanode;
        if (typeof ids === "string" ? ids === dnId : Array.isArray(ids) ? ids.includes(dnId) : ids) {
            props.updateVarName && dispatch(createRequestUpdateAction(id, module, [props.updateVarName], true));
        }
    }, [props.coreChanged, props.updateVarName, id, module, dispatch, dnId]);

    // Tabs
    const [tabValue, setTabValue] = useState(0);
    const handleTabChange = useCallback(
        (_: SyntheticEvent, newValue: number) => {
            if (isDataNode) {
                newValue == 1 &&
                    setHistoryRequested(
                        (req) =>
                            req ||
                            dispatch(createSendActionNameAction(id, module, props.onIdSelect, { history_id: dnId })) ||
                            true
                    );
                newValue == 2 &&
                    setDataRequested(
                        (req) =>
                            req ||
                            dispatch(createSendActionNameAction(id, module, props.onIdSelect, { data_id: dnId })) ||
                            true
                    );
                setTabValue(newValue);
            }
        },
        [dnId, dispatch, id, isDataNode, module, props.onIdSelect]
    );

    // Tabular viewType
    const [viewType, setViewType] = useState(TableViewType);
    const onViewTypeChange = useCallback(
        (e: MouseEvent, value?: string) => {
            if (value) {
                dispatch(createSendActionNameAction(id, module, props.onIdSelect, { chart_id: dnId }));
                setViewType(value);
            }
        },
        [dnId, dispatch, id, module, props.onIdSelect]
    );

    // base tabular columns
    const tabularColumns = useMemo(() => {
        if (dtTabular && props.tabularColumns) {
            try {
                return JSON.parse(props.tabularColumns) as Record<string, ColumnDesc>;
            } catch {
                // ignore error
            }
        }
        return undefined;
    }, [dtTabular, props.tabularColumns]);

    // tabular selected columns
    const [selectedCols, setSelectedCols] = useState<string[]>([]);
    const onColsChange = useCallback(
        (e: SelectChangeEvent<typeof selectedCols>) => {
            const sc = typeof e.target.value == "string" ? e.target.value.split(",") : e.target.value;
            localStorage && localStorage.setItem(`${dnConfig}-selected-cols`, JSON.stringify(sc));
            setSelectedCols(sc);
        },
        [dnConfig]
    );
    useEffect(() => {
        if (tabularColumns) {
            let tc = Object.entries(tabularColumns).map((e) => e[1].dfid);
            const storedSel = localStorage && localStorage.getItem(`${dnConfig}-selected-cols`);
            if (storedSel) {
                try {
                    const storedCols = JSON.parse(storedSel);
                    if (Array.isArray(storedCols)) {
                        tc = tc.filter((c) => storedCols.includes(c));
                    }
                } catch {
                    // do nothing
                }
            }
            setSelectedCols(tc);
        }
    }, [tabularColumns, dnConfig]);

    // tabular columns
    const [tabCols, setTabCols] = useState<Record<string, ColumnDesc>>({});
    useEffect(() => {
        if (tabularColumns) {
            const res = {} as Record<string, ColumnDesc>;
            const dfids = {} as Record<string, string>;
            Object.entries(tabularColumns).forEach(([k, v]) => (dfids[v.dfid] = k));
            selectedCols.forEach((c) => dfids[c] && (res[dfids[c]] = tabularColumns[dfids[c]]));
            setTabCols(res);
        }
    }, [tabularColumns, selectedCols]);

    return (
        <>
            <Box sx={MainBoxSx} id={id} onClick={onFocus} className={className}>
                <Accordion
                    defaultExpanded={expanded}
                    expanded={userExpanded}
                    onChange={onExpand}
                    disabled={!isDataNode}
                >
                    <AccordionSummary
                        expandIcon={expandable ? <ArrowForwardIosSharp sx={AccordionIconSx} /> : null}
                        sx={AccordionSummarySx}
                    >
                        <Grid container alignItems="baseline" direction="row" spacing={1}>
                            <Grid item>{dnLabel}</Grid>
                            <Grid item>
                                <Typography fontSize="smaller">{dnType}</Typography>
                            </Grid>
                        </Grid>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Box sx={tabBoxSx}>
                            <Tabs value={tabValue} onChange={handleTabChange} aria-label="basic tabs example">
                                <Tab
                                    label="Properties"
                                    id={`${uniqid}-properties`}
                                    aria-controls={`${uniqid}-dn-tabpanel-properties`}
                                />
                                <Tab
                                    label="History"
                                    id={`${uniqid}-history`}
                                    aria-controls={`${uniqid}-dn-tabpanel-history`}
                                    style={showHistory ? undefined : noDisplay}
                                />
                                <Tab
                                    label="Data"
                                    id={`${uniqid}-data`}
                                    aria-controls={`${uniqid}-dn-tabpanel-data`}
                                    style={showData ? undefined : noDisplay}
                                />
                            </Tabs>
                        </Box>
                        <div
                            role="tabpanel"
                            hidden={tabValue !== 0}
                            id={`${uniqid}-dn-tabpanel-properties`}
                            aria-labelledby={`${uniqid}-properties`}
                        >
                            <Grid container rowSpacing={2} sx={gridSx}>
                                <Grid item xs={12} container justifyContent="space-between" spacing={1}>
                                    <Grid
                                        item
                                        xs={12}
                                        container
                                        justifyContent="space-between"
                                        data-focus="label"
                                        onClick={onFocus}
                                        sx={hoverSx}
                                    >
                                        {active && focusName === "label" ? (
                                            <TextField
                                                label="Label"
                                                variant="outlined"
                                                fullWidth
                                                sx={FieldNoMaxWidth}
                                                value={label || ""}
                                                onChange={onLabelChange}
                                                InputProps={{
                                                    endAdornment: (
                                                        <InputAdornment position="end">
                                                            <IconButton sx={IconPaddingSx} onClick={editLabel}>
                                                                <CheckCircle color="primary" />
                                                            </IconButton>
                                                            <IconButton sx={IconPaddingSx} onClick={cancelLabel}>
                                                                <Cancel color="inherit" />
                                                            </IconButton>
                                                        </InputAdornment>
                                                    ),
                                                }}
                                                disabled={!isDataNode}
                                            />
                                        ) : (
                                            <>
                                                <Grid item xs={4}>
                                                    <Typography variant="subtitle2">Label</Typography>
                                                </Grid>
                                                <Grid item xs={8}>
                                                    <Typography variant="subtitle2">{dnLabel}</Typography>
                                                </Grid>
                                            </>
                                        )}
                                    </Grid>
                                </Grid>
                                {showEditDate ? (
                                    <Grid item xs={12} container justifyContent="space-between">
                                        <Grid item xs={4}>
                                            <Typography variant="subtitle2">Last edit date</Typography>
                                        </Grid>
                                        <Grid item xs={8}>
                                            <Typography variant="subtitle2">{dnEditDate}</Typography>
                                        </Grid>
                                    </Grid>
                                ) : null}
                                {showExpirationDate ? (
                                    <Grid item xs={12} container justifyContent="space-between">
                                        <Grid item xs={4}>
                                            <Typography variant="subtitle2">Expiration date</Typography>
                                        </Grid>
                                        <Grid item xs={8}>
                                            <Typography variant="subtitle2">{dnExpirationDate}</Typography>
                                        </Grid>
                                    </Grid>
                                ) : null}
                                {showConfig ? (
                                    <Grid item xs={12} container justifyContent="space-between">
                                        <Grid item xs={4} pb={2}>
                                            <Typography variant="subtitle2">Config ID</Typography>
                                        </Grid>
                                        <Grid item xs={8}>
                                            <Typography variant="subtitle2">{dnConfig}</Typography>
                                        </Grid>
                                    </Grid>
                                ) : null}
                                {showOwner ? (
                                    <Grid item xs={12} container justifyContent="space-between">
                                        <Grid item xs={4}>
                                            <Typography variant="subtitle2">Owner</Typography>
                                        </Grid>
                                        <Grid item xs={7} sx={iconLabelSx}>
                                            {dnOwnerType === NodeType.CYCLE ? (
                                                <CycleIcon fontSize="small" color="primary" />
                                            ) : dnOwnerType === NodeType.SCENARIO ? (
                                                <ScenarioIcon fontSize="small" color="primary" />
                                            ) : null}
                                            <Typography variant="subtitle2">{dnOwnerLabel}</Typography>
                                        </Grid>
                                        <Grid item xs={1}>
                                            <IconButton
                                                sx={tinySelPinIconButtonSx}
                                                onClick={showScenarios}
                                                disabled={!isDataNode}
                                            >
                                                <Launch />
                                            </IconButton>
                                            <Popover
                                                open={Boolean(anchorEl)}
                                                anchorEl={anchorEl}
                                                onClose={handleClose}
                                                anchorOrigin={popoverOrigin}
                                            >
                                                <CoreSelector
                                                    entities={props.scenarios}
                                                    leafType={NodeType.SCENARIO}
                                                    lovPropertyName="scenarios"
                                                    height="50vh"
                                                    showPins={false}
                                                    updateVarName={scenarioUpdateVars[0]}
                                                    updateVars={`scenarios=${scenarioUpdateVars[1]}`}
                                                    onSelect={handleClose}
                                                />
                                            </Popover>
                                        </Grid>
                                    </Grid>
                                ) : null}
                                <Grid item xs={12}>
                                    <Divider />
                                </Grid>
                                <PropertiesEditor
                                    entityId={dnId}
                                    active={active}
                                    isDefined={isDataNode}
                                    entProperties={dnProperties}
                                    show={showProperties}
                                    focusName={focusName}
                                    setFocusName={setFocusName}
                                    onFocus={onFocus}
                                    onEdit={props.onEdit}
                                />
                            </Grid>
                        </div>
                        <div
                            role="tabpanel"
                            hidden={tabValue !== 1}
                            id={`${uniqid}-dn-tabpanel-history`}
                            aria-labelledby={`${uniqid}-history`}
                        >
                            {historyRequested && Array.isArray(props.history) ? (
                                <Grid container spacing={1}>
                                    {props.history.map((edit, idx) => (
                                        <>
                                            {idx != 0 ? (
                                                <Grid item xs={12}>
                                                    <Divider />
                                                </Grid>
                                            ) : null}
                                            <Grid item container key={`edit-${idx}`}>
                                                <Grid item xs={0.4} sx={editSx}>
                                                    <Box>{(props.history || []).length - idx}</Box>
                                                </Grid>
                                                <Grid item xs={0.1}></Grid>
                                                <Grid item container xs={11.5}>
                                                    <Grid item xs={12}>
                                                        <Typography variant="subtitle1">
                                                            {edit[0]
                                                                ? format(new Date(edit[0]), editTimestampFormat)
                                                                : "no date"}
                                                        </Typography>
                                                    </Grid>
                                                    <Grid item xs={12}>
                                                        {edit[2]}
                                                    </Grid>
                                                    <Grid item xs={12}>
                                                        <Typography fontSize="smaller">{edit[1]}</Typography>
                                                    </Grid>
                                                </Grid>
                                            </Grid>
                                        </>
                                    ))}
                                </Grid>
                            ) : (
                                "History will come here"
                            )}
                        </div>
                        <div
                            role="tabpanel"
                            hidden={tabValue !== 2}
                            id={`${uniqid}-dn-tabpanel-data`}
                            aria-labelledby={`${uniqid}-data`}
                        >
                            {dataRequested ? (
                                dtValue !== undefined ? (
                                    <Grid container justifyContent="space-between" spacing={1}>
                                        <Grid
                                            item
                                            container
                                            xs={12}
                                            justifyContent="space-between"
                                            data-focus="data-value"
                                            onClick={onFocus}
                                            sx={hoverSx}
                                        >
                                            {active && focusName === "data-value" ? (
                                                typeof dtValue == "boolean" ? (
                                                    <>
                                                        <Grid item xs={10}>
                                                            <Switch
                                                                value={dataValue as boolean}
                                                                onChange={onDataValueChange}
                                                            />
                                                        </Grid>
                                                        <Grid item xs={2}>
                                                            <IconButton
                                                                onClick={editDataValue}
                                                                size="small"
                                                                sx={IconPaddingSx}
                                                            >
                                                                <CheckCircle color="primary" />
                                                            </IconButton>
                                                            <IconButton
                                                                onClick={cancelDataValue}
                                                                size="small"
                                                                sx={IconPaddingSx}
                                                            >
                                                                <Cancel color="inherit" />
                                                            </IconButton>
                                                        </Grid>
                                                    </>
                                                ) : dtType == "date" ? (
                                                    <LocalizationProvider dateAdapter={AdapterDateFns}>
                                                        <Grid item xs={10}>
                                                            <DateTimePicker
                                                                value={dataValue as Date}
                                                                onChange={onDataValueDateChange}
                                                                slotProps={textFieldProps}
                                                            />
                                                        </Grid>
                                                        <Grid item xs={2}>
                                                            <IconButton
                                                                onClick={editDataValue}
                                                                size="small"
                                                                sx={IconPaddingSx}
                                                            >
                                                                <CheckCircle color="primary" />
                                                            </IconButton>
                                                            <IconButton
                                                                onClick={cancelDataValue}
                                                                size="small"
                                                                sx={IconPaddingSx}
                                                            >
                                                                <Cancel color="inherit" />
                                                            </IconButton>
                                                        </Grid>
                                                    </LocalizationProvider>
                                                ) : (
                                                    <TextField
                                                        label="Value"
                                                        variant="outlined"
                                                        fullWidth
                                                        sx={FieldNoMaxWidth}
                                                        value={dataValue || ""}
                                                        onChange={onDataValueChange}
                                                        type={typeof dtValue == "number" ? "number" : undefined}
                                                        InputProps={{
                                                            endAdornment: (
                                                                <InputAdornment position="end">
                                                                    <IconButton
                                                                        sx={IconPaddingSx}
                                                                        onClick={editDataValue}
                                                                    >
                                                                        <CheckCircle color="primary" />
                                                                    </IconButton>
                                                                    <IconButton
                                                                        sx={IconPaddingSx}
                                                                        onClick={cancelDataValue}
                                                                    >
                                                                        <Cancel color="inherit" />
                                                                    </IconButton>
                                                                </InputAdornment>
                                                            ),
                                                        }}
                                                        disabled={!isDataNode}
                                                    />
                                                )
                                            ) : (
                                                <>
                                                    <Grid item xs={4}>
                                                        <Typography variant="subtitle2">Value</Typography>
                                                    </Grid>
                                                    <Grid item xs={8}>
                                                        {typeof dtValue == "boolean" ? (
                                                            <Switch
                                                                defaultChecked={dtValue}
                                                                disabled={true}
                                                                title={`${dtValue}`}
                                                            />
                                                        ) : (
                                                            <Typography variant="subtitle2">
                                                                {dtType == "date"
                                                                    ? dataValue &&
                                                                      format(dataValue as Date, "yyyy/MM/dd HH:mm:ss")
                                                                    : dtValue}
                                                            </Typography>
                                                        )}
                                                    </Grid>
                                                </>
                                            )}
                                        </Grid>
                                    </Grid>
                                ) : dtError ? (
                                    <Typography>{dtError}</Typography>
                                ) : dtTabular ? (
                                    <>
                                        <ToggleButtonGroup
                                            onChange={onViewTypeChange}
                                            exclusive
                                            value={viewType}
                                            color="primary"
                                        >
                                            <ToggleButton value={TableViewType}>
                                                <TableChartOutlined />
                                            </ToggleButton>
                                            <ToggleButton value="chart">
                                                <BarChartOutlined />
                                            </ToggleButton>
                                        </ToggleButtonGroup>
                                        {viewType === TableViewType ? (
                                            <>
                                                <FormControl sx={colsSelectSx}>
                                                    <InputLabel id={uniqid + "-cols-label"}>Columns</InputLabel>
                                                    <Select
                                                        labelId={uniqid + "-cols-label"}
                                                        multiple
                                                        value={selectedCols}
                                                        onChange={onColsChange}
                                                        input={<OutlinedInput label="Columns" />}
                                                        renderValue={(selected) => selected.join(", ")}
                                                        MenuProps={MenuProps}
                                                    >
                                                        {Object.values(tabularColumns || {}).map((colDesc) => (
                                                            <MenuItem key={colDesc.dfid} value={colDesc.dfid}>
                                                                <Checkbox
                                                                    checked={selectedCols.includes(colDesc.dfid)}
                                                                />
                                                                <ListItemText primary={colDesc.dfid} />
                                                            </MenuItem>
                                                        ))}
                                                    </Select>
                                                </FormControl>
                                                <Table
                                                    defaultColumns={JSON.stringify(tabCols)}
                                                    updateVarName={getUpdateVar(props.updateVars, "tabularData")}
                                                    data={props.tabularData}
                                                    userData={dnId}
                                                    onEdit={props.onTabularDataEdit}
                                                    filter={true}
                                                />
                                            </>
                                        ) : (
                                            <DataNodeChart
                                                uniqid={uniqid}
                                                columns={tabularColumns}
                                                tabularData={props.tabularData}
                                                configId={dnConfig}
                                                defaultConfig={props.chartConfig}
                                                updateVarName={getUpdateVar(props.updateVars, "tabularData")}
                                            />
                                        )}
                                    </>
                                ) : (
                                    "type: unknown"
                                )
                            ) : (
                                "Data shall be shown here"
                            )}
                        </div>
                    </AccordionDetails>
                </Accordion>
                <Box>{props.error}</Box>
            </Box>
        </>
    );
};
export default DataNodeViewer;
