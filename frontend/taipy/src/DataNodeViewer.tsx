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
    Fragment,
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
import Accordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid2";
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import Popover from "@mui/material/Popover";
import Switch from "@mui/material/Switch";
import Stack from "@mui/material/Stack";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";

import ArrowForwardIosSharp from "@mui/icons-material/ArrowForwardIosSharp";
import Cancel from "@mui/icons-material/Cancel";
import CheckCircle from "@mui/icons-material/CheckCircle";
import Download from "@mui/icons-material/Download";
import Launch from "@mui/icons-material/Launch";
import LockOutlined from "@mui/icons-material/LockOutlined";
import Upload from "@mui/icons-material/Upload";

import { DateTimePicker } from "@mui/x-date-pickers/DateTimePicker";
import { BaseDateTimePickerSlotProps } from "@mui/x-date-pickers/DateTimePicker/shared";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFnsV3";
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
    useClassNames,
    useDynamicProperty,
    useModule,
    Store,
    FileSelector,
    getComponentClassName,
} from "taipy-gui";

import { Cycle as CycleIcon, Scenario as ScenarioIcon } from "./icons";
import {
    AccordionIconSx,
    AccordionSummarySx,
    CoreProps,
    FieldNoMaxWidth,
    IconPaddingSx,
    MainBoxSx,
    TableViewType,
    getUpdateVarNames,
    hoverSx,
    iconLabelSx,
    popoverOrigin,
    tinySelPinIconButtonSx,
} from "./utils";
import PropertiesEditor, { DatanodeProperties } from "./PropertiesEditor";
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
const textFieldProps = { textField: { margin: "dense" } } as BaseDateTimePickerSlotProps<Date>;
const buttonSx = { minWidth: "0px" };

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
    DatanodeData, // data
    boolean, // editInProgress
    string, // editorId
    string, // notReadableReason
    string, // notEditableReason
    boolean, // is file based
    string, // notDownloadableReason
    string // notUploadableReason
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
    data,
    editInProgress,
    editorId,
    notReadableReason,
    notEditableReason,
    isFileBased,
    notDownloadableReason,
    notUploadableReason,
}
const DataNodeFullLength = Object.keys(DataNodeFullProps).length / 2;

type DatanodeData = [RowValue, string | null, boolean | null, string | null];
enum DatanodeDataProps {
    value,
    type,
    tabular,
    error,
}

interface DataNodeViewerProps extends  CoreProps {
    expandable?: boolean;
    expanded?: boolean;
    defaultDataNode?: string;
    dataNode?: DataNodeFull | Array<DataNodeFull>;
    onEdit?: string;
    showConfig?: boolean;
    showOwner?: boolean;
    showEditDate?: boolean;
    showExpirationDate?: boolean;
    showProperties?: boolean;
    showHistory?: boolean;
    showData?: boolean;
    chartConfigs?: string;
    scenarios?: Scenarios;
    history?: Array<[string, string, string]>;
    data?: DatanodeData;
    tabularData?: TableValueType;
    tabularColumns?: string;
    dnProperties?: DatanodeProperties;
    onDataValue?: string;
    onTabularDataEdit?: string;
    chartConfig?: string;
    width?: string;
    onLock?: string;
    updateDnVars?: string;
    fileDownload?: boolean;
    fileUpload?: boolean;
    uploadCheck?: string;
    onFileAction?: string;
    showOwnerLabel?: boolean;
}

const dataValueFocus = "data-value";

const getDataValue = (value?: RowValue, dType?: string | null) => (dType == "date" ? new Date(value as string) : value);

const getValidDataNode = (datanode: DataNodeFull | DataNodeFull[]) =>
    datanode.length == DataNodeFullLength && typeof datanode[DataNodeFullProps.id] === "string"
        ? (datanode as DataNodeFull)
        : datanode.length == 1
        ? (datanode[0] as DataNodeFull)
        : undefined;

const invalidDatanode: DataNodeFull = [
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    -1,
    [null, null, null, null],
    false,
    "",
    "invalid",
    "invalid",
    false,
    "invalid",
    "invalid",
];

enum TabValues {
    Data,
    Properties,
    History,
}

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
        updateVars = "",
        updateDnVars = "",
        fileDownload = false,
        fileUpload = false,
        showOwnerLabel = false,
        coreChanged,
    } = props;

    const { state, dispatch } = useContext<Store>(Context);
    const module = useModule();
    const uniqId = useUniqueId(id);
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
        dnData,
        dnEditInProgress,
        dnEditorId,
        dnNotReadableReason,
        dnNotEditableReason,
        isFileBased,
        dnNotDownloadableReason,
        dnNotUploadableReason,
    ] = datanode;
    const dtType = dnData[DatanodeDataProps.type];
    const dtValue = dnData[DatanodeDataProps.value] ?? (dtType == "float" ? null : undefined);
    const dtTabular = dnData[DatanodeDataProps.tabular] ?? false;
    const dtError = dnData[DatanodeDataProps.error];

    // Tabs
    const [tabValue, setTabValue] = useState<TabValues>(TabValues.Data);
    const handleTabChange = useCallback(
        (_: SyntheticEvent, newValue: number) => {
            if (valid) {
                if (newValue == TabValues.History) {
                    setHistoryRequested((req) => {
                        if (!req) {
                            const idVar = getUpdateVar(updateDnVars, "history_id");
                            dispatch(
                                createRequestUpdateAction(
                                    id,
                                    module,
                                    getUpdateVarNames(updateVars, "history"),
                                    true,
                                    idVar ? { [idVar]: dnId } : undefined
                                )
                            );
                        }
                        return true;
                    });
                    setDataRequested(false);
                    setPropertiesRequested(false);
                } else if (newValue == TabValues.Data) {
                    setDataRequested((req) => {
                        if (!req && dtTabular) {
                            const idVar = getUpdateVar(updateDnVars, "data_id");
                            dispatch(
                                createRequestUpdateAction(
                                    id,
                                    module,
                                    getUpdateVarNames(updateVars, "tabularData", "tabularColumns"),
                                    true,
                                    idVar ? { [idVar]: dnId } : undefined
                                )
                            );
                        }
                        return true;
                    });
                    setHistoryRequested(false);
                    setPropertiesRequested(false);
                } else if (newValue == TabValues.Properties) {
                    setPropertiesRequested((req) => {
                        if (!req) {
                            const idVar = getUpdateVar(updateDnVars, "properties_id");
                            dispatch(
                                createRequestUpdateAction(
                                    id,
                                    module,
                                    getUpdateVarNames(updateVars, "dnProperties"),
                                    true,
                                    idVar ? { [idVar]: dnId } : undefined
                                )
                            );
                        }
                        return true;
                    });
                    setDataRequested(false);
                    setHistoryRequested(false);
                }
                setTabValue(newValue);
            }
        },
        [dnId, dispatch, id, valid, module, updateVars, updateDnVars, dtTabular]
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
            const newDnId = (dn || invalidDatanode)[DataNodeFullProps.id];
            const isNewDn = oldDn[DataNodeFullProps.id] !== newDnId;
            // clean lock on change
            if (oldDn[DataNodeFullProps.id] && isNewDn && editLock.current) {
                const oldId = oldDn[DataNodeFullProps.id];
                Promise.resolve().then(() =>
                    dispatch(
                        createSendActionNameAction(id, module, props.onLock, {
                            id: oldId,
                            lock: false,
                            error_id: getUpdateVar(updateDnVars, "error_id"),
                        })
                    )
                );
            }
            if (!dn || isNewDn) {
                setTabValue(showData ? TabValues.Data : TabValues.Properties);
            }
            if (!dn) {
                return invalidDatanode;
            }
            editLock.current = dn[DataNodeFullProps.editInProgress];
            setHistoryRequested((req) => {
                if (req && !isNewDn && tabValue == TabValues.History) {
                    const idVar = getUpdateVar(updateDnVars, "history_id");
                    const vars = getUpdateVarNames(updateVars, "history");
                    Promise.resolve().then(() =>
                        dispatch(
                            createRequestUpdateAction(id, module, vars, true, idVar ? { [idVar]: newDnId } : undefined)
                        )
                    );
                    return true;
                }
                return false;
            });
            setDataRequested(() => {
                if (showData && tabValue == TabValues.Data && dn[DataNodeFullProps.data][DatanodeDataProps.tabular]) {
                    const idVar = getUpdateVar(updateDnVars, "data_id");
                    const vars = getUpdateVarNames(updateVars, "tabularData", "tabularColumns");
                    Promise.resolve().then(() =>
                        dispatch(
                            createRequestUpdateAction(id, module, vars, true, idVar ? { [idVar]: newDnId } : undefined)
                        )
                    );
                    return true;
                }
                return false;
            });
            setPropertiesRequested((req) => {
                if ((req || !showData) && tabValue == TabValues.Properties) {
                    const idVar = getUpdateVar(updateDnVars, "properties_id");
                    const vars = getUpdateVarNames(updateVars, "properties");
                    Promise.resolve().then(() =>
                        dispatch(
                            createRequestUpdateAction(id, module, vars, true, idVar ? { [idVar]: newDnId } : undefined)
                        )
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
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [props.dataNode, props.defaultDataNode, showData, id, dispatch, module, props.onLock]);

    // clean lock on unmount
    useEffect(
        () => () => {
            dnId &&
                editLock.current &&
                dispatch(
                    createSendActionNameAction(id, module, props.onLock, {
                        id: dnId,
                        lock: false,
                        error_id: getUpdateVar(updateDnVars, "error_id"),
                    })
                );
        },
        [dnId, id, dispatch, module, props.onLock, updateDnVars]
    );

    const active = useDynamicProperty(props.active, props.defaultActive, true) && !dnNotReadableReason;
    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);

    // history & data
    const [historyRequested, setHistoryRequested] = useState(false);
    const [dataRequested, setDataRequested] = useState(false);
    const [propertiesRequested, setPropertiesRequested] = useState(false);

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
                dispatch(
                    createSendActionNameAction(id, module, props.onLock, {
                        id: dnId,
                        lock: true,
                        error_id: getUpdateVar(updateDnVars, "error_id"),
                    })
                );
                editLock.current = true;
            }
        },
        [dnId, props.onLock, id, dispatch, module, updateDnVars]
    );

    // Label
    const [label, setLabel] = useState<string>();
    const editLabel = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            if (valid) {
                dispatch(
                    createSendActionNameAction(id, module, props.onEdit, {
                        id: dnId,
                        name: label,
                        error_id: getUpdateVar(updateDnVars, "error_id"),
                    })
                );
                setFocusName("");
            }
        },
        [valid, props.onEdit, dnId, label, id, dispatch, module, updateDnVars]
    );
    const cancelLabel = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            setLabel(dnLabel);
            setFocusName("");
        },
        [dnLabel]
    );
    const onLabelChange = useCallback((e: ChangeEvent<HTMLInputElement>) => setLabel(e.target.value), []);

    // scenarios
    const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
    const scenarioUpdateVars = useMemo(() => getUpdateVarNames(updateVars, "scenario", "scenarios"), [updateVars]);
    const showScenarios = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            if (valid) {
                const ownerIdVar = getUpdateVar(updateDnVars, "owner_id");
                dispatch(
                    createRequestUpdateAction(
                        id,
                        module,
                        scenarioUpdateVars,
                        true,
                        ownerIdVar ? { [ownerIdVar]: dnOwnerId } : undefined
                    )
                );
                setAnchorEl(e.currentTarget);
            }
        },
        [dnOwnerId, valid, updateDnVars, scenarioUpdateVars, dispatch, id, module]
    );
    const handleClose = useCallback(() => setAnchorEl(null), []);

    const [comment, setComment] = useState("");
    const changeComment = useCallback((e: ChangeEvent<HTMLInputElement>) => setComment(e.currentTarget.value), []);

    // on datanode change
    useEffect(() => {
        setLabel(dnLabel);
        setUserExpanded(expanded && valid);
        setHistoryRequested(false);
        setDataRequested(showData);
        setPropertiesRequested(!showData);
        setViewType(TableViewType);
        setComment("");
    }, [dnId, dnLabel, valid, expanded, showData]);

    // Datanode data
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
                        error_id: getUpdateVar(updateDnVars, "error_id"),
                        data_id: getUpdateVar(updateDnVars, "data_id"),
                    })
                );
                setFocusName("");
            }
        },
        [valid, props.onDataValue, dnId, dataValue, dtType, id, dispatch, module, comment, updateDnVars]
    );
    const cancelDataValue = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            setDataValue(getDataValue(dtValue, dtType));
            setFocusName("");
            dispatch(
                createSendActionNameAction(id, module, props.onLock, {
                    id: dnId,
                    lock: false,
                    error_id: getUpdateVar(updateDnVars, "error_id"),
                })
            );
        },
        [dtValue, dtType, dnId, id, dispatch, module, props.onLock, updateDnVars]
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
                const idVar = getUpdateVar(updateDnVars, "chart_id");
                dispatch(
                    createRequestUpdateAction(
                        id,
                        module,
                        getUpdateVarNames(updateVars, "chartConfig"),
                        true,
                        idVar ? { [idVar]: dnId } : undefined
                    )
                );
                setViewType(value);
            }
        },
        [dnId, updateVars, updateDnVars, dispatch, id, module]
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

    // file action
    const onfileHandler = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            const { action = "import" } = e.currentTarget.dataset || {};
            if (action == "export") {
                dispatch(
                    createSendActionNameAction(id, module, props.onFileAction, {
                        id: dnId,
                        action: action,
                        type: "raw",
                        error_id: getUpdateVar(updateDnVars, "error_id"),
                    })
                );
            }
        },
        [props.onFileAction, dispatch, dnId, id, module, updateDnVars]
    );

    const uploadData = useMemo(
        () =>
            valid && isFileBased && fileUpload
                ? JSON.stringify({
                      id: dnId,
                      error_id: getUpdateVar(updateDnVars, "error_id"),
                      upload_check: props.uploadCheck,
                  })
                : undefined,
        [dnId, valid, isFileBased, fileUpload, props.uploadCheck, updateDnVars]
    );

    // Refresh on broadcast
    useEffect(() => {
        const ids = coreChanged?.datanode;
        if ((typeof ids === "string" && ids === dnId) || (Array.isArray(ids) && ids.includes(dnId))) {
            props.updateVarName &&
                dispatch(createRequestUpdateAction(id, module, [props.updateVarName], true));
        }
    }, [coreChanged, props.updateVarName, id, module, dispatch, dnId]);

    return (
        <>
            <Box sx={dnMainBoxSx} id={id} onClick={onFocus} className={`${className} ${getComponentClassName(props.children)}`}>
                <Accordion defaultExpanded={expanded} expanded={userExpanded} onChange={onExpand} disabled={!valid}>
                    <AccordionSummary
                        expandIcon={expandable ? <ArrowForwardIosSharp sx={AccordionIconSx} /> : null}
                        sx={AccordionSummarySx}
                    >
                        <Stack direction="row" spacing={1} alignItems="baseline">
                            {showOwnerLabel ? <Typography>{dnOwnerLabel} &gt;</Typography> : null}
                            <Typography>{dnLabel}</Typography>
                            <Typography fontSize="smaller">{dnType}</Typography>
                        </Stack>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Box sx={tabBoxSx}>
                            <Stack direction="row" justifyContent="space-between">
                                <Tabs value={tabValue} onChange={handleTabChange}>
                                    <Tab
                                        label={
                                            <Grid container alignItems="center">
                                                <Grid>Data</Grid>
                                                {dnEditInProgress ? (
                                                    <Grid>
                                                        <Tooltip
                                                            title={
                                                                "locked " + (dnEditorId === editorId ? "by you" : "")
                                                            }
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
                                        id={`${uniqId}-data`}
                                        aria-controls={`${uniqId}-dn-tabpanel-data`}
                                        style={showData ? undefined : noDisplay}
                                    />
                                    <Tab
                                        label="Properties"
                                        id={`${uniqId}-properties`}
                                        aria-controls={`${uniqId}-dn-tabpanel-properties`}
                                    />
                                    <Tab
                                        label="History"
                                        id={`${uniqId}-history`}
                                        aria-controls={`${uniqId}-dn-tabpanel-history`}
                                        style={showHistory ? undefined : noDisplay}
                                    />
                                </Tabs>
                                {valid && isFileBased && (fileDownload || fileUpload) ? (
                                    <Stack direction="row" spacing={1}>
                                        {fileDownload ? (
                                            <Tooltip
                                                title={dnNotDownloadableReason ? dnNotDownloadableReason : "Download"}
                                            >
                                                <span>
                                                    <Button
                                                        data-action="export"
                                                        onClick={onfileHandler}
                                                        sx={buttonSx}
                                                        disabled={!!dnNotDownloadableReason}
                                                    >
                                                        <Download />
                                                    </Button>
                                                </span>
                                            </Tooltip>
                                        ) : null}
                                        {fileUpload ? (
                                            <FileSelector
                                                hoverText={dnNotUploadableReason ? dnNotUploadableReason : "Upload"}
                                                icon={<Upload />}
                                                withBorder={false}
                                                onUploadAction={props.onFileAction}
                                                uploadData={uploadData}
                                                defaultActive={!dnNotUploadableReason}
                                            />
                                        ) : null}
                                    </Stack>
                                ) : null}
                            </Stack>
                        </Box>
                        <div
                            role="tabpanel"
                            hidden={tabValue !== TabValues.Properties}
                            id={`${uniqId}-dn-tabpanel-properties`}
                            aria-labelledby={`${uniqId}-properties`}
                        >
                            <Grid container rowSpacing={2} sx={gridSx}>
                                <Grid size={12} container justifyContent="space-between" spacing={1}>
                                    <Grid
                                        size={12}
                                        container
                                        justifyContent="space-between"
                                        data-focus="label"
                                        onClick={onFocus}
                                        sx={hoverSx}
                                    >
                                        {active && !dnNotEditableReason && focusName === "label" ? (
                                            <TextField
                                                label="Label"
                                                variant="outlined"
                                                fullWidth
                                                sx={FieldNoMaxWidth}
                                                value={label || ""}
                                                onChange={onLabelChange}
                                                slotProps={{
                                                    input: {
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
                                                    },
                                                }}
                                                disabled={!valid}
                                            />
                                        ) : (
                                            <>
                                                <Grid size={4}>
                                                    <Typography variant="subtitle2">Label</Typography>
                                                </Grid>
                                                <Grid size={8}>
                                                    <Typography variant="subtitle2">{dnLabel}</Typography>
                                                </Grid>
                                            </>
                                        )}
                                    </Grid>
                                </Grid>
                                {showEditDate ? (
                                    <Grid size={12} container justifyContent="space-between">
                                        <Grid size={4}>
                                            <Typography variant="subtitle2">Last edit date</Typography>
                                        </Grid>
                                        <Grid size={8}>
                                            <Typography variant="subtitle2">{dnEditDate}</Typography>
                                        </Grid>
                                    </Grid>
                                ) : null}
                                {showExpirationDate ? (
                                    <Grid size={12} container justifyContent="space-between">
                                        <Grid size={4}>
                                            <Typography variant="subtitle2">Expiration date</Typography>
                                        </Grid>
                                        <Grid size={8}>
                                            <Typography variant="subtitle2">{dnExpirationDate}</Typography>
                                        </Grid>
                                    </Grid>
                                ) : null}
                                {showConfig ? (
                                    <Grid size={12} container justifyContent="space-between">
                                        <Grid size={4} pb={2}>
                                            <Typography variant="subtitle2">Config ID</Typography>
                                        </Grid>
                                        <Grid size={8}>
                                            <Typography variant="subtitle2">{dnConfig}</Typography>
                                        </Grid>
                                    </Grid>
                                ) : null}
                                {showOwner ? (
                                    <Grid size={12} container justifyContent="space-between">
                                        <Grid size={4}>
                                            <Typography variant="subtitle2">Owner</Typography>
                                        </Grid>
                                        <Grid size={7} sx={iconLabelSx}>
                                            {dnOwnerType === NodeType.CYCLE ? (
                                                <CycleIcon fontSize="small" color="primary" />
                                            ) : dnOwnerType === NodeType.SCENARIO ? (
                                                <ScenarioIcon fontSize="small" color="primary" />
                                            ) : null}
                                            <Typography variant="subtitle2">{dnOwnerLabel}</Typography>
                                        </Grid>
                                        <Grid size={1}>
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
                                                            updateCoreVars=""
                                                            showSearch={false}
                                                        />
                                                    </Popover>
                                                </>
                                            ) : null}
                                        </Grid>
                                    </Grid>
                                ) : null}
                                <Grid size={12}>
                                    <Divider />
                                </Grid>
                                <PropertiesEditor
                                    entityId={dnId}
                                    active={!!active}
                                    isDefined={valid}
                                    entProperties={
                                        propertiesRequested && Array.isArray(props.dnProperties)
                                            ? props.dnProperties
                                            : []
                                    }
                                    show={showProperties}
                                    focusName={focusName}
                                    setFocusName={setFocusName}
                                    onFocus={onFocus}
                                    onEdit={props.onEdit}
                                    notEditableReason={dnNotEditableReason}
                                    updateVars={updateDnVars}
                                />
                            </Grid>
                        </div>
                        <div
                            role="tabpanel"
                            hidden={tabValue !== TabValues.History}
                            id={`${uniqId}-dn-tabpanel-history`}
                            aria-labelledby={`${uniqId}-history`}
                        >
                            {historyRequested && Array.isArray(props.history) ? (
                                <Grid container spacing={1}>
                                    {props.history.map((edit, idx) => (
                                        <Fragment key={`edit-${idx}`}>
                                            {idx != 0 ? (
                                                <Grid size={12}>
                                                    <Divider />
                                                </Grid>
                                            ) : null}
                                            <Grid container>
                                                <Grid size={0.4} sx={editSx}>
                                                    <Box>{(props.history || []).length - idx}</Box>
                                                </Grid>
                                                <Grid size={0.1}></Grid>
                                                <Grid container size={11.5}>
                                                    <Grid size={12}>
                                                        <Typography variant="subtitle1">
                                                            {edit[0]
                                                                ? format(new Date(edit[0]), editTimestampFormat)
                                                                : "no date"}
                                                        </Typography>
                                                    </Grid>
                                                    {edit[2] ? <Grid size={12}>{edit[2]}</Grid> : null}
                                                    {edit[1] ? (
                                                        <Grid size={12}>
                                                            <Typography fontSize="smaller">{edit[1]}</Typography>
                                                        </Grid>
                                                    ) : null}
                                                </Grid>
                                            </Grid>
                                        </Fragment>
                                    ))}
                                </Grid>
                            ) : (
                                "History will come here"
                            )}
                        </div>
                        <div
                            role="tabpanel"
                            hidden={tabValue !== TabValues.Data}
                            id={`${uniqId}-dn-tabpanel-data`}
                            aria-labelledby={`${uniqId}-data`}
                        >
                            {dtValue !== undefined ? (
                                <Grid container justifyContent="space-between" spacing={1}>
                                    <Grid
                                        container
                                        size={12}
                                        justifyContent="space-between"
                                        data-focus={dataValueFocus}
                                        onClick={onFocus}
                                        sx={hoverSx}
                                    >
                                        {active &&
                                        !dnNotEditableReason &&
                                        dnEditInProgress &&
                                        dnEditorId === editorId &&
                                        focusName === dataValueFocus ? (
                                            <>
                                                {typeof dtValue == "boolean" ? (
                                                    <>
                                                        <Grid size={10}>
                                                            <Switch
                                                                value={dataValue as boolean}
                                                                onChange={onDataValueChange}
                                                            />
                                                        </Grid>
                                                        <Grid size={2}>
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
                                                ) : dtType == "date" &&
                                                  (dataValue === null || dataValue instanceof Date) ? (
                                                    <LocalizationProvider dateAdapter={AdapterDateFns}>
                                                        <Grid size={10}>
                                                            <DateTimePicker
                                                                value={dataValue as Date}
                                                                onChange={onDataValueDateChange}
                                                                slotProps={textFieldProps}
                                                            />
                                                        </Grid>
                                                        <Grid size={2}>
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
                                                        type={
                                                            typeof dtValue == "number"
                                                                ? "number"
                                                                : dtType == "float" && dtValue === null
                                                                ? "number"
                                                                : undefined
                                                        }
                                                        slotProps={{
                                                            input: {
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
                                                            },
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
                                                <Grid size={4}>
                                                    <Typography variant="subtitle2">Value</Typography>
                                                </Grid>
                                                <Grid size={8}>
                                                    {typeof dtValue == "boolean" ? (
                                                        <Switch
                                                            defaultChecked={dtValue}
                                                            disabled={true}
                                                            title={`${dtValue}`}
                                                        />
                                                    ) : (
                                                        <Typography variant="subtitle2">
                                                            {dtType == "date"
                                                                ? (dataValue === null || dataValue instanceof Date) &&
                                                                  format(dataValue as Date, "yyyy/MM/dd HH:mm:ss")
                                                                : dtType == "float" && dtValue === null
                                                                ? "NaN"
                                                                : `${dtValue}`}
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
                                dataRequested ? (
                                    <>
                                        {viewType === TableViewType ? (
                                            <DataNodeTable
                                                active={!!active}
                                                uniqId={uniqId}
                                                columns={tabularColumns}
                                                data={props.tabularData}
                                                nodeId={dnId}
                                                configId={dnConfig}
                                                onViewTypeChange={onViewTypeChange}
                                                updateVarName={getUpdateVar(updateVars, "tabularData")}
                                                onEdit={props.onTabularDataEdit}
                                                onLock={props.onLock}
                                                editInProgress={dnEditInProgress && dnEditorId !== editorId}
                                                editLock={editLock}
                                                notEditableReason={dnNotEditableReason}
                                                updateDnVars={updateDnVars}
                                            />
                                        ) : (
                                            <DataNodeChart
                                                active={!!active}
                                                uniqId={uniqId}
                                                columns={tabularColumns}
                                                tabularData={props.tabularData}
                                                configId={dnConfig}
                                                defaultConfig={props.chartConfig}
                                                updateVarName={getUpdateVar(updateVars, "tabularData")}
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
                {props.error ? <Alert severity="error">{props.error}</Alert> : null}
            </Box>
            {props.children}
        </>
    );
};
export default DataNodeViewer;
