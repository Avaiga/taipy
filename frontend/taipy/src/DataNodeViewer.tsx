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
    useState,
    useCallback,
    useContext,
    useEffect,
    useMemo,
    ChangeEvent,
    SyntheticEvent,
    MouseEvent,
    useRef,
} from "react";
import { CheckCircle, Cancel, ArrowForwardIosSharp, Launch, LockOutlined } from "@mui/icons-material";
import Accordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import Popover from "@mui/material/Popover";
import Switch from "@mui/material/Switch";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import { DateTimePicker } from "@mui/x-date-pickers/DateTimePicker";
import { BaseDateTimePickerSlotsComponentsProps } from "@mui/x-date-pickers/DateTimePicker/shared";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { format } from "date-fns";
import deepEqual from "fast-deep-equal/es6";

import {
    ColumnDesc,
    Context,
    RowValue,
    TableValueType,
    createRequestUpdateAction,
    createSendActionNameAction,
    getUpdateVar,
    useDynamicProperty,
    useModule,
    Store,
} from "taipy-gui";

import { Cycle as CycleIcon, Scenario as ScenarioIcon } from "./icons";
import {
    AccordionIconSx,
    AccordionSummarySx,
    FieldNoMaxWidth,
    IconPaddingSx,
    MainBoxSx,
    TableViewType,
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
import DataNodeChart from "./DataNodeChart";
import DataNodeTable from "./DataNodeTable";

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

type DataNodeFull = [
    string, // id
    string, // type
    string, // config_id
    string, // last_edit_date
    string, // expiration_date
    string, // label
    string, // ownerId
    string, // ownerLabel
    number, // ownerType
    Array<[string, string]>, // properties
    boolean, // editInProgress
    string, // editorId
    boolean, // readable
    boolean // editable
];

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
    editInProgress,
    editorId,
    readable,
    editable,
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
    width?: string;
    onLock?: string;
}

const dataValueFocus = "data-value";

const getDataValue = (value?: RowValue, dType?: string | null) => (dType == "date" ? new Date(value as string) : value);

const getValidDataNode = (datanode: DataNodeFull | DataNodeFull[]) =>
    datanode.length == DataNodeFullLength && typeof datanode[DataNodeFullProps.id] === "string"
        ? (datanode as DataNodeFull)
        : datanode.length == 1
        ? (datanode[0] as DataNodeFull)
        : undefined;

const invalidDatanode: DataNodeFull = ["", "", "", "", "", "", "", "", -1, [], false, "", false, false];

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

    const { state, dispatch } = useContext<Store>(Context);
    const module = useModule();
    const uniqid = useUniqueId(id);
    const editorId = (state as { id: string }).id;
    const editLock = useRef(false);
    const [valid, setValid] = useState(false);
    const [datanode, setDatanode] = useState<DataNodeFull>(invalidDatanode);

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
        dnEditInProgress,
        dnEditorId,
        dnReadable,
        dnEditable,
    ] = datanode;

    // Tabs
    const [tabValue, setTabValue] = useState(0);
    const handleTabChange = useCallback(
        (_: SyntheticEvent, newValue: number) => {
            if (valid) {
                if (newValue == 1) {
                    setHistoryRequested(
                        (req) =>
                            req ||
                            dispatch(createSendActionNameAction(id, module, props.onIdSelect, { history_id: dnId })) ||
                            true
                    );
                } else if (newValue == 2) {
                    setDataRequested(
                        (req) =>
                            req ||
                            dispatch(createSendActionNameAction(id, module, props.onIdSelect, { data_id: dnId })) ||
                            true
                    );
                    setHistoryRequested(false);
                }
                setTabValue(newValue);
            }
        },
        [dnId, dispatch, id, valid, module, props.onIdSelect]
    );

    useEffect(() => {
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
        setValid(!!dn);
        setDatanode((oldDn) => {
            if (oldDn === dn) {
                return oldDn;
            }
            const isNewDn = oldDn[DataNodeFullProps.id] !== (dn || invalidDatanode)[DataNodeFullProps.id];
            // clean lock on change
            if (oldDn[DataNodeFullProps.id] && isNewDn && editLock.current) {
                dispatch(
                    createSendActionNameAction(id, module, props.onLock, {
                        id: oldDn[DataNodeFullProps.id],
                        lock: false,
                    })
                );
            }
            if (!dn || isNewDn) {
                setTabValue(0);
            }
            if (!dn) {
                return invalidDatanode;
            }
            editLock.current = dn[DataNodeFullProps.editInProgress];
            setHistoryRequested((req) => {
                if (req && !isNewDn && tabValue == 1) {
                    dispatch(
                        createSendActionNameAction(id, module, props.onIdSelect, {
                            history_id: oldDn[DataNodeFullProps.id],
                        })
                    );
                    return true;
                }
                return false;
            });
            setDataRequested((req) => {
                if (req && !isNewDn && tabValue == 2) {
                    dispatch(
                        createSendActionNameAction(id, module, props.onIdSelect, {
                            data_id: oldDn[DataNodeFullProps.id],
                        })
                    );
                    return true;
                }
                return false;
            });
            if (deepEqual(oldDn, dn)) {
                return oldDn;
            }
            return dn;
        });
    }, [props.dataNode, props.defaultDataNode, id, dispatch, module, props.onLock, tabValue, props.onIdSelect]);

    // clean lock on unmount
    useEffect(
        () => () => {
            dnId &&
                editLock.current &&
                dispatch(createSendActionNameAction(id, module, props.onLock, { id: dnId, lock: false }));
        },
        [dnId, id, dispatch, module, props.onLock]
    );

    const active = useDynamicProperty(props.active, props.defaultActive, true) && dnReadable;
    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);

    // history & data
    const [historyRequested, setHistoryRequested] = useState(false);
    const [dataRequested, setDataRequested] = useState(false);

    // userExpanded
    const [userExpanded, setUserExpanded] = useState(valid && expanded);
    const onExpand = useCallback(
        (e: SyntheticEvent, expand: boolean) => expandable && setUserExpanded(expand),
        [expandable]
    );

    // focus
    const [focusName, setFocusName] = useState("");
    const onFocus = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            setFocusName(e.currentTarget.dataset.focus || "");
            if (e.currentTarget.dataset.focus === dataValueFocus && !editLock.current) {
                dispatch(createSendActionNameAction(id, module, props.onLock, { id: dnId, lock: true }));
                editLock.current = true;
            }
        },
        [dnId, props.onLock, id, dispatch, module]
    );

    // Label
    const [label, setLabel] = useState<string>();
    const editLabel = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            if (valid) {
                dispatch(createSendActionNameAction(id, module, props.onEdit, { id: dnId, name: label }));
                setFocusName("");
            }
        },
        [valid, props.onEdit, dnId, label, id, dispatch, module]
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
            if (valid) {
                dispatch(createSendActionNameAction(id, module, props.onIdSelect, { owner_id: dnOwnerId }));
                setAnchorEl(e.currentTarget);
            }
        },
        [dnOwnerId, dispatch, id, valid, module, props.onIdSelect]
    );
    const handleClose = useCallback(() => setAnchorEl(null), []);
    const scenarioUpdateVars = useMemo(
        () => [getUpdateVar(props.updateVars, "scenario"), getUpdateVar(props.updateVars, "scenarios")],
        [props.updateVars]
    );

    const [comment, setComment] = useState("");
    const changeComment = useCallback((e: ChangeEvent<HTMLInputElement>) => {
        setComment(e.currentTarget.value);
    }, []);

    // on datanode change
    useEffect(() => {
        setLabel(dnLabel);
        setUserExpanded(expanded && valid);
        setTabValue(0);
        setHistoryRequested(false);
        setDataRequested(false);
        setViewType(TableViewType);
        setComment("");
    }, [dnId, dnLabel, valid, expanded]);

    // Datanode data
    const dtValue = (props.data && props.data[DatanodeDataProps.value]) ?? undefined;
    const dtType = props.data && props.data[DatanodeDataProps.type];
    const dtTabular = (props.data && props.data[DatanodeDataProps.tabular]) ?? false;
    const dtError = props.data && props.data[DatanodeDataProps.error];
    const [dataValue, setDataValue] = useState<RowValue | Date>();
    const editDataValue = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            if (valid) {
                dispatch(
                    createSendActionNameAction(id, module, props.onDataValue, {
                        id: dnId,
                        value: dataValue,
                        type: dtType,
                        comment: comment,
                    })
                );
                setFocusName("");
            }
        },
        [valid, props.onDataValue, dnId, dataValue, dtType, id, dispatch, module, comment]
    );
    const cancelDataValue = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            setDataValue(getDataValue(dtValue, dtType));
            setFocusName("");
            dispatch(createSendActionNameAction(id, module, props.onLock, { id: dnId, lock: false }));
        },
        [dtValue, dtType, dnId, id, dispatch, module, props.onLock, setDataValue, setFocusName]
    );
    const onDataValueChange = useCallback((e: ChangeEvent<HTMLInputElement>) => setDataValue(e.target.value), []);
    const onDataValueDateChange = useCallback((d: Date | null) => d && setDataValue(d), []);
    useEffect(() => {
        if (dtValue !== undefined) {
            setDataValue(getDataValue(dtValue, dtType));
        }
    }, [dtValue, dtType]);

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

    const dnMainBoxSx = useMemo(
        () => (props.width ? { ...MainBoxSx, maxWidth: props.width } : MainBoxSx),
        [props.width]
    );

    // Refresh on broadcast
    useEffect(() => {
        const ids = props.coreChanged?.datanode;
        if ((typeof ids === "string" && ids === dnId) || (Array.isArray(ids) && ids.includes(dnId))) {
            props.updateVarName && dispatch(createRequestUpdateAction(id, module, [props.updateVarName], true));
        }
    }, [props.coreChanged, props.updateVarName, id, module, dispatch, dnId]);

    return (
        <>
            <Box sx={dnMainBoxSx} id={id} onClick={onFocus} className={className}>
                <Accordion defaultExpanded={expanded} expanded={userExpanded} onChange={onExpand} disabled={!valid}>
                    <AccordionSummary
                        expandIcon={expandable ? <ArrowForwardIosSharp sx={AccordionIconSx} /> : null}
                        sx={AccordionSummarySx}
                    >
                        <Grid container alignItems="baseline" direction="row" spacing={1}>
                            <Grid item>{dnLabel}</Grid>
                            <Grid item>
                                <Typography fontSize="smaller">{dnType}</Typography>
                            </Grid>
                            <Grid item>{}</Grid>
                        </Grid>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Box sx={tabBoxSx}>
                            <Tabs value={tabValue} onChange={handleTabChange}>
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
                                    label={
                                        <Grid container alignItems="center">
                                            <Grid item>Data</Grid>
                                            {dnEditInProgress ? (
                                                <Grid item>
                                                    <Tooltip
                                                        title={"locked " + (dnEditorId === editorId ? "by you" : "")}
                                                    >
                                                        <LockOutlined
                                                            fontSize="small"
                                                            color={dnEditorId === editorId ? "disabled" : "primary"}
                                                        />
                                                    </Tooltip>
                                                </Grid>
                                            ) : null}
                                        </Grid>
                                    }
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
                                        {active && dnEditable && focusName === "label" ? (
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
                                                            <Tooltip title="Apply">
                                                                <IconButton
                                                                    sx={IconPaddingSx}
                                                                    onClick={editLabel}
                                                                    size="small"
                                                                >
                                                                    <CheckCircle color="primary" />
                                                                </IconButton>
                                                            </Tooltip>
                                                            <Tooltip title="Cancel">
                                                                <IconButton
                                                                    sx={IconPaddingSx}
                                                                    onClick={cancelLabel}
                                                                    size="small"
                                                                >
                                                                    <Cancel color="inherit" />
                                                                </IconButton>
                                                            </Tooltip>
                                                        </InputAdornment>
                                                    ),
                                                }}
                                                disabled={!valid}
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
                                            {dnOwnerId ? (
                                                <>
                                                    <Tooltip title="Show Scenarios">
                                                        <span>
                                                            <IconButton
                                                                sx={tinySelPinIconButtonSx}
                                                                onClick={showScenarios}
                                                                disabled={!valid}
                                                            >
                                                                <Launch />
                                                            </IconButton>
                                                        </span>
                                                    </Tooltip>
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
                                                </>
                                            ) : null}
                                        </Grid>
                                    </Grid>
                                ) : null}
                                <Grid item xs={12}>
                                    <Divider />
                                </Grid>
                                <PropertiesEditor
                                    entityId={dnId}
                                    active={active}
                                    isDefined={valid}
                                    entProperties={dnProperties}
                                    show={showProperties}
                                    focusName={focusName}
                                    setFocusName={setFocusName}
                                    onFocus={onFocus}
                                    onEdit={props.onEdit}
                                    editable={dnEditable}
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
                                                    {edit[2] ? (
                                                        <Grid item xs={12}>
                                                            {edit[2]}
                                                        </Grid>
                                                    ) : null}
                                                    {edit[1] ? (
                                                        <Grid item xs={12}>
                                                            <Typography fontSize="smaller">{edit[1]}</Typography>
                                                        </Grid>
                                                    ) : null}
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
                                            data-focus={dataValueFocus}
                                            onClick={onFocus}
                                            sx={hoverSx}
                                        >
                                            {active &&
                                            dnEditable &&
                                            dnEditInProgress &&
                                            dnEditorId === editorId &&
                                            focusName === dataValueFocus ? (
                                                <>
                                                    {typeof dtValue == "boolean" ? (
                                                        <>
                                                            <Grid item xs={10}>
                                                                <Switch
                                                                    value={dataValue as boolean}
                                                                    onChange={onDataValueChange}
                                                                />
                                                            </Grid>
                                                            <Grid item xs={2}>
                                                                <Tooltip title="Apply">
                                                                    <IconButton
                                                                        onClick={editDataValue}
                                                                        size="small"
                                                                        sx={IconPaddingSx}
                                                                    >
                                                                        <CheckCircle color="primary" />
                                                                    </IconButton>
                                                                </Tooltip>
                                                                <Tooltip title="Cancel">
                                                                    <IconButton
                                                                        onClick={cancelDataValue}
                                                                        size="small"
                                                                        sx={IconPaddingSx}
                                                                    >
                                                                        <Cancel color="inherit" />
                                                                    </IconButton>
                                                                </Tooltip>
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
                                                                <Tooltip title="Apply">
                                                                    <IconButton
                                                                        onClick={editDataValue}
                                                                        size="small"
                                                                        sx={IconPaddingSx}
                                                                    >
                                                                        <CheckCircle color="primary" />
                                                                    </IconButton>
                                                                </Tooltip>
                                                                <Tooltip title="Cancel">
                                                                    <IconButton
                                                                        onClick={cancelDataValue}
                                                                        size="small"
                                                                        sx={IconPaddingSx}
                                                                    >
                                                                        <Cancel color="inherit" />
                                                                    </IconButton>
                                                                </Tooltip>
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
                                                                        <Tooltip title="Apply">
                                                                            <IconButton
                                                                                sx={IconPaddingSx}
                                                                                onClick={editDataValue}
                                                                                size="small"
                                                                            >
                                                                                <CheckCircle color="primary" />
                                                                            </IconButton>
                                                                        </Tooltip>
                                                                        <Tooltip title="Cancel">
                                                                            <IconButton
                                                                                sx={IconPaddingSx}
                                                                                onClick={cancelDataValue}
                                                                                size="small"
                                                                            >
                                                                                <Cancel color="inherit" />
                                                                            </IconButton>
                                                                        </Tooltip>
                                                                    </InputAdornment>
                                                                ),
                                                            }}
                                                            disabled={!valid}
                                                        />
                                                    )}
                                                    <TextField
                                                        value={comment}
                                                        onChange={changeComment}
                                                        label="Comment"
                                                    ></TextField>
                                                </>
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
                                        {viewType === TableViewType ? (
                                            <DataNodeTable
                                                active={active}
                                                uniqid={uniqid}
                                                columns={tabularColumns}
                                                data={props.tabularData}
                                                nodeId={dnId}
                                                configId={dnConfig}
                                                onViewTypeChange={onViewTypeChange}
                                                updateVarName={getUpdateVar(props.updateVars, "tabularData")}
                                                onEdit={props.onTabularDataEdit}
                                                onLock={props.onLock}
                                                editInProgress={dnEditInProgress && dnEditorId !== editorId}
                                                editLock={editLock}
                                                editable={dnEditable}
                                            />
                                        ) : (
                                            <DataNodeChart
                                                active={active}
                                                uniqid={uniqid}
                                                columns={tabularColumns}
                                                tabularData={props.tabularData}
                                                configId={dnConfig}
                                                defaultConfig={props.chartConfig}
                                                updateVarName={getUpdateVar(props.updateVars, "tabularData")}
                                                chartConfigs={props.chartConfigs}
                                                onViewTypeChange={onViewTypeChange}
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
