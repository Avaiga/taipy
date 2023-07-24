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
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import Popover from "@mui/material/Popover";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { CheckCircle, Cancel, ArrowForwardIosSharp, Launch } from "@mui/icons-material";

import {
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
import { Tab, Tabs } from "@mui/material";

const tabBoxSx = { borderBottom: 1, borderColor: "divider" };
const noDisplay = { display: "none" };
const gridSx = { mt: 0 };

type DanaNodeFull = [string, string, string, string, string, string, string, string, number, Array<[string, string]>];

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

interface DataNodeViewerProps {
    id?: string;
    expandable?: boolean;
    expanded?: boolean;
    updateVarName?: string;
    updateVars: string;
    defaultDataNode?: string;
    dataNode?: DanaNodeFull | Array<DanaNodeFull>;
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
    chartConfig?: string;
    libClassName?: string;
    className?: string;
    dynamicClassName?: string;
    scenarios?: Scenarios;
    history?: Array<Array<[string, string]>>;
    data?: Record<string, unknown>;
}

const getValidDataNode = (datanode: DanaNodeFull | DanaNodeFull[]) =>
    datanode.length == DataNodeFullLength && typeof datanode[DataNodeFullProps.id] === "string"
        ? (datanode as DanaNodeFull)
        : datanode.length == 1
        ? (datanode[0] as DanaNodeFull)
        : undefined;

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
        let dn: DanaNodeFull | undefined = undefined;
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
    }, [dnLabel, isDataNode, expanded]);

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
                                    id={`${id}-properties`}
                                    aria-controls="dn-tabpanel-properties"
                                />
                                <Tab
                                    label="History"
                                    id={`${id}-history`}
                                    aria-controls="dn-tabpanel-history"
                                    style={showHistory ? undefined : noDisplay}
                                />
                                <Tab
                                    label="Data"
                                    id={`${id}-data`}
                                    aria-controls="dn-tabpanel-data"
                                    style={showData ? undefined : noDisplay}
                                />
                            </Tabs>
                        </Box>
                        <div
                            role="tabpanel"
                            hidden={tabValue !== 0}
                            id="dn-tabpanel-properties"
                            aria-labelledby={`${id}-properties`}
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
                                                id={id}
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
                            id="dn-tabpanel-history"
                            aria-labelledby={`${id}-history`}
                        >
                            {historyRequested && Array.isArray(props.history) ? (
                                <table>
                                    {props.history.map((edit, idx) =>
                                        edit.map((v, idx2) => (
                                            <tr key={`edit-${idx}-${idx2}`}>
                                                {idx2 == 0 ? (
                                                    <td rowSpan={edit.length}>
                                                        {}`edit-${idx}`
                                                    </td>
                                                ) : null}
                                                <td>v[0]</td>
                                                <td>v[1]</td>
                                            </tr>
                                        ))
                                    )}
                                </table>
                            ) : (
                                "History will come here"
                            )}
                        </div>
                        <div
                            role="tabpanel"
                            hidden={tabValue !== 2}
                            id="dn-tabpanel-data"
                            aria-labelledby={`${id}-data`}
                        >
                            {dataRequested ? "show data" : "Data shall be shown here"}
                        </div>
                    </AccordionDetails>
                </Accordion>
                <Box>{props.error}</Box>
            </Box>
        </>
    );
};
export default DataNodeViewer;
