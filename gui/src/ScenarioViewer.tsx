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

import React, { useState, useCallback, useEffect, useMemo, ChangeEvent, SyntheticEvent } from "react";
import Accordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary, { AccordionSummaryProps } from "@mui/material/AccordionSummary";
import Autocomplete, { AutocompleteChangeReason, AutocompleteChangeDetails } from "@mui/material/Autocomplete";
import Chip from "@mui/material/Chip";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { styled } from "@mui/material";
import { FlagOutlined, DeleteOutline, Add, Send, CheckCircle, Cancel, ArrowForwardIosSharp } from "@mui/icons-material";

import {
    createRequestUpdateAction,
    createSendActionNameAction,
    useDispatch,
    useDynamicProperty,
    useModule,
} from "taipy-gui";

import { FlagSx, Property, ScenarioFull } from "./utils";
import ConfirmDialog from "./utils/ConfirmDialog";

interface ScenarioViewerProps {
    id?: string;
    expandable?: boolean;
    expanded?: boolean;
    defaultExpanded?: boolean;
    submit?: boolean;
    delete?: boolean;
    submitPipelines?: boolean;
    tags?: boolean;
    properties?: boolean;
    pipelines?: boolean;
    updateVarName?: string;
    scenario?: ScenarioFull | Array<ScenarioFull>;
    onSubmit?: string;
    onEdit?: string;
    onDelete?: string;
    error?: string;
    coreChanged?: Record<string, unknown>;
    defaultActive: boolean;
    active: boolean;
    config?: boolean;
    cycle?: boolean;
}

interface PipelinesRowProps {
    active: boolean;
    number: number;
    pipelineId: string;
    value: string;
    enableScenarioFields: boolean;
    submitEntity: (id: string) => void;
    submit: boolean;
}

const MainBoxSx = {
    overflowY: "auto",
};

const FieldNoMaxWidth = {
    maxWidth: "none",
};

const AccordionSummarySx = { fontSize: "0.9rem" };
const ChipSx = { ml: 1 };
const IconPaddingSx = { padding: 0 };
const DeleteIconSx = { height: 50, width: 50, p: 0 };

const tagsAutocompleteSx = {
    "& .MuiOutlinedInput-root": {
        padding: "3px 15px 3px 3px !important",
    },
    maxWidth: "none",
};

const PipelineRow = ({
    active,
    number,
    pipelineId,
    value,
    submitEntity,
    enableScenarioFields,
    submit,
}: PipelinesRowProps) => {
    const [pipeline, setPipeline] = useState<string>(value);
    const [focus, setFocus] = useState(false);

    const onPipelineBlur = useCallback((e: React.FocusEvent<HTMLInputElement>) => {
        setPipeline(e.currentTarget.value);
        setFocus(false);
    }, []);

    const onPipelineFocus = useCallback(() => setFocus(true), []);

    const onSaveField = useCallback((e: React.MouseEvent<HTMLElement>) => {
        //TODO: save field
    }, []);

    const onCancelField = useCallback((e: any) => {
        //TODO: cancel field
    }, []);

    const onSubmitPipeline = useCallback(() => {
        submitEntity(pipelineId);
    }, []);

    const index = number + 1;
    return (
        <Grid item xs={12} container justifyContent="space-between">
            <Grid item container xs={10}>
                {active ? (
                    <TextField
                        data-name={`pipe${index}`}
                        label={"Pipeline " + index}
                        variant="outlined"
                        name={`pipeline${index}`}
                        value={pipeline}
                        onBlur={onPipelineBlur}
                        sx={FieldNoMaxWidth}
                        onFocus={onPipelineFocus}
                        disabled={!enableScenarioFields}
                        fullWidth
                        InputProps={{
                            endAdornment: focus ? (
                                <>
                                    <IconButton sx={IconPaddingSx} onClick={onSaveField}>
                                        <CheckCircle color="primary" />
                                    </IconButton>
                                    <IconButton sx={IconPaddingSx} onClick={onCancelField}>
                                        <Cancel color="inherit" />
                                    </IconButton>
                                </>
                            ) : null,
                        }}
                    />
                ) : (
                    <Typography variant="subtitle2">{pipeline}</Typography>
                )}
            </Grid>
            <Grid item xs={2} container alignContent="center" alignItems="center" justifyContent="center">
                {submit ? (
                    <IconButton
                        component="label"
                        size="small"
                        onClick={onSubmitPipeline}
                        disabled={!enableScenarioFields}
                    >
                        <Send color="info" />
                    </IconButton>
                ) : null}
            </Grid>
        </Grid>
    );
};

const MuiAccordionSummary = styled((props: AccordionSummaryProps) => (
    <AccordionSummary expandIcon={<ArrowForwardIosSharp sx={AccordionSummarySx} />} {...props} />
))(({ theme }) => ({
    flexDirection: "row-reverse",
    "& .MuiAccordionSummary-expandIconWrapper.Mui-expanded": {
        transform: "rotate(90deg)",
        marginRight: theme.spacing(1),
    },
    "& .MuiAccordionSummary-content": {
        marginLeft: theme.spacing(1),
    },
}));

const ScenarioViewer = (props: ScenarioViewerProps) => {
    const {
        id = "",
        delete: deleteSc = true,
        submit = true,
        expandable = true,
        tags = false,
        properties = true,
        pipelines = true,
        submitPipelines = true,
        config = false,
        cycle = false,
    } = props;

    const dispatch = useDispatch();
    const module = useModule();

    const [
        scenarioId = "",
        primary = false,
        scConfig = "",
        date = "",
        scLabel = "",
        scenarioTags = [],
        scenarioProperties = [],
        scPipelines = [],
        authorizedTags = [],
        isScenario = false,
    ] = useMemo(() => {
        const sc = Array.isArray(props.scenario)
            ? props.scenario.length == 9 && typeof props.scenario[0] === "string"
                ? (props.scenario as ScenarioFull)
                : props.scenario.length == 1
                ? (props.scenario[0] as ScenarioFull)
                : undefined
            : undefined;
        return sc ? [...sc, true] : [];
    }, [props.scenario]);

    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const expanded = useDynamicProperty(props.expanded, props.defaultExpanded, false);

    const [deleteDialog, setDeleteDialogOpen] = useState(false);
    const openDeleteDialog = useCallback(() => setDeleteDialogOpen(true), []);
    const closeDeleteDialog = useCallback(() => setDeleteDialogOpen(false), []);
    const onDeleteScenario = useCallback(() => {
        setDeleteDialogOpen(false);
        if (isScenario) {
            dispatch(createSendActionNameAction(id, module, props.onDelete, true, true, { id: scenarioId }));
        }
    }, [isScenario, props.onDelete, scenarioId]);

    const [primaryDialog, setPrimaryDialog] = useState(false);
    const openPrimaryDialog = useCallback(() => setPrimaryDialog(true), []);
    const closePrimaryDialog = useCallback(() => setPrimaryDialog(false), []);
    const onPromote = useCallback(() => {
        setPrimaryDialog(false);
        if (isScenario) {
            dispatch(createSendActionNameAction(id, module, props.onEdit, { id: scenarioId, primary: true }));
        }
    }, [isScenario, props.onEdit, scenarioId]);

    const [scProperties, setProperties] = useState<Property[]>([]);
    const [newProp, setNewProp] = useState<Property>({
        id: "",
        key: "",
        value: "",
    });

    // submits
    const submitPipeline = useCallback((pipelineId: string) => {
        dispatch(createSendActionNameAction(id, module, props.onSubmit, { id: pipelineId }));
    }, []);

    const submitScenario = useCallback((e: React.MouseEvent<HTMLElement>) => {
        e.stopPropagation();
        if (isScenario) {
            dispatch(createSendActionNameAction(id, module, props.onSubmit, { id: scenarioId }));
        }
    }, []);

    // Label
    const [label, setLabel] = useState<string>();
    const [labelFocus, setLabelFocus] = useState(false);
    const editLabel = useCallback(() => {
        if (isScenario) {
            dispatch(
                createSendActionNameAction(id, module, props.onEdit, { id: scenarioId, name: "name", value: label })
            );
        }
    }, [isScenario, props.onEdit, scenarioId, label]);
    const cancelLabel = useCallback(() => setLabel(scLabel), [scLabel]);
    const onLabelChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => setLabel(e.target.value), []);

    // tags
    const [scTags, setTags] = useState<string[]>([]);
    const [tagsFocus, setTagsFocus] = useState(false);
    const editTags = useCallback(() => {
        if (isScenario) {
            dispatch(
                createSendActionNameAction(id, module, props.onEdit, { id: scenarioId, name: "tags", value: tags })
            );
        }
    }, [isScenario, props.onEdit, scenarioId, tags]);
    const cancelTags = useCallback(() => setTags(scenarioTags), [scenarioTags]);
    const onChangeTags = useCallback(
        (
            e: SyntheticEvent,
            tags: string[],
            reason: AutocompleteChangeReason,
            details?: AutocompleteChangeDetails<string>
        ) => setTags(tags),
        []
    );

    const updatePropertyField = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const { id = "", name = "" } = e.currentTarget.parentElement?.parentElement?.dataset || {};
        if (name) {
            if (id) {
                setProperties((props) =>
                    props.map((p) => {
                        if (id == p.id) {
                            p[name as keyof Property] = e.target.value;
                        }
                        return p;
                    })
                );
            } else {
                setNewProp((np) => ({ ...np, [name]: e.target.value }));
            }
        }
    }, []);

    const propertyDelete = useCallback((e: React.MouseEvent<HTMLElement>) => {
        const { id = "-1" } = e.currentTarget.dataset;
        setProperties((props) => props.filter((item) => item.id !== id));
    }, []);

    const propertyAdd = () => {
        setProperties((props) => [...props, { ...newProp, id: props.length + 1 + "" }]);
        setNewProp({ id: "", key: "", value: "" });
    };

    // on scenario change
    useEffect(() => {
        tags && setTags(scenarioTags);
        properties &&
            setProperties(
                scenarioProperties.map(([k, v], i) => ({
                    id: i + "",
                    key: k,
                    value: v,
                }))
            );
        setLabel(scLabel);
    }, [scenarioTags, scenarioProperties, scLabel]);

    // Refresh on broadcast
    useEffect(() => {
        if (props.coreChanged?.scenario) {
            setTags([]);
            setProperties([]);
            props.updateVarName && dispatch(createRequestUpdateAction(id, module, [props.updateVarName], true));
        }
    }, [props.coreChanged, props.updateVarName, module, dispatch]);

    return (
        <>
            <Box sx={MainBoxSx} id={id}>
                <Accordion defaultExpanded={expandable ? expanded : isScenario} disabled={!isScenario}>
                    <MuiAccordionSummary>
                        <Grid
                            container
                            alignItems="center"
                            direction="row"
                            flexWrap="nowrap"
                            justifyContent="space-between"
                            spacing={1}
                        >
                            <Grid item>
                                {scLabel}
                                {primary && (
                                    <Chip
                                        color="primary"
                                        label={<FlagOutlined sx={FlagSx} />}
                                        size="small"
                                        sx={ChipSx}
                                    />
                                )}
                            </Grid>
                            <Grid item>
                                {submit ? (
                                    <IconButton
                                        sx={IconPaddingSx}
                                        onClick={submitScenario}
                                        disabled={!isScenario || !active}
                                    >
                                        <Send fontSize="medium" color={isScenario && active ? "info" : "disabled"} />
                                    </IconButton>
                                ) : null}
                            </Grid>
                        </Grid>
                    </MuiAccordionSummary>
                    <AccordionDetails>
                        <Grid container rowSpacing={2}>
                            {config ? (
                                <Grid item xs={12} container justifyContent="space-between">
                                    <Grid item xs={4} pb={2}>
                                        <Typography variant="subtitle2">Config ID</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        <Typography variant="subtitle2">{scConfig}</Typography>
                                    </Grid>
                                </Grid>
                            ) : null}
                            {cycle ? (
                                <Grid item xs={12} container justifyContent="space-between">
                                    <Grid item xs={4}>
                                        <Typography variant="subtitle2">Cycle / Frequency</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        <Typography variant="subtitle2">{date}</Typography>
                                    </Grid>
                                </Grid>
                            ) : null}
                            {active ? (
                                <Grid item xs={11} container justifyContent="space-between" spacing={1}>
                                    <Grid item xs={12} container justifyContent="space-between">
                                        <TextField
                                            label="Label"
                                            variant="outlined"
                                            fullWidth
                                            sx={FieldNoMaxWidth}
                                            value={label}
                                            onChange={onLabelChange}
                                            onFocus={(e) => setLabelFocus(true)}
                                            onBlur={(e) => setLabelFocus(false)}
                                            InputProps={{
                                                endAdornment: labelFocus && (
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
                                            disabled={!isScenario}
                                        />
                                    </Grid>
                                    {tags ? (
                                        <Grid item xs={12} container justifyContent="space-between">
                                            <Autocomplete
                                                multiple
                                                options={authorizedTags}
                                                freeSolo={!authorizedTags.length}
                                                renderTags={(value: readonly string[], getTagProps) =>
                                                    value.map((option: string, index: number) => (
                                                        <Chip
                                                            variant="outlined"
                                                            label={option}
                                                            sx={IconPaddingSx}
                                                            {...getTagProps({ index })}
                                                        />
                                                    ))
                                                }
                                                onFocus={(e) => setTagsFocus(true)}
                                                onBlur={(e) => setTagsFocus(false)}
                                                value={scTags}
                                                onChange={onChangeTags}
                                                fullWidth
                                                renderInput={(params) => (
                                                    <TextField
                                                        {...params}
                                                        variant="outlined"
                                                        label="Tags"
                                                        sx={tagsAutocompleteSx}
                                                        fullWidth
                                                        InputProps={{
                                                            ...params.InputProps,
                                                            endAdornment: tagsFocus && (
                                                                <>
                                                                    <IconButton sx={IconPaddingSx} onClick={editTags}>
                                                                        <CheckCircle color="primary" />
                                                                    </IconButton>
                                                                    <IconButton sx={IconPaddingSx} onClick={cancelTags}>
                                                                        <Cancel color="inherit" />
                                                                    </IconButton>
                                                                </>
                                                            ),
                                                        }}
                                                    />
                                                )}
                                                disabled={!isScenario}
                                            />
                                        </Grid>
                                    ) : null}
                                </Grid>
                            ) : (
                                <Grid item xs={12}>
                                    <Grid item xs={12} container justifyContent="space-between">
                                        <Grid item xs={4}>
                                            <Typography variant="subtitle2">Label</Typography>
                                        </Grid>
                                        <Grid item xs={8}>
                                            <Typography variant="subtitle2">{scLabel}</Typography>
                                        </Grid>
                                    </Grid>
                                    {tags ? (
                                        <Grid item xs={12} container justifyContent="space-between">
                                            <Grid item xs={4}>
                                                <Typography variant="subtitle2">Tags</Typography>
                                            </Grid>
                                            <Grid item xs={8}>
                                                {scTags.map((tag, index) => (
                                                    <Chip key={index} label={tag} variant="outlined" />
                                                ))}
                                            </Grid>
                                        </Grid>
                                    ) : null}
                                </Grid>
                            )}
                            <Grid item xs={12}>
                                <Divider />
                            </Grid>
                            {properties ? (
                                <>
                                    <Grid item xs={12} container justifyContent="space-between">
                                        <Typography variant="h6">Custom Properties</Typography>
                                    </Grid>
                                    {scProperties
                                        ? scProperties.map((property, index) => {
                                              return (
                                                  <Grid
                                                      item
                                                      xs={12}
                                                      spacing={1}
                                                      container
                                                      justifyContent="space-between"
                                                      key={property.key}
                                                  >
                                                      <Grid item xs={5}>
                                                          {active ? (
                                                              <TextField
                                                                  label="Key"
                                                                  variant="outlined"
                                                                  value={property.key}
                                                                  sx={FieldNoMaxWidth}
                                                                  disabled={!isScenario}
                                                                  data-name="key"
                                                                  data-id={property.id}
                                                                  onChange={updatePropertyField}
                                                              />
                                                          ) : (
                                                              <Typography variant="subtitle2">
                                                                  {property.key}
                                                              </Typography>
                                                          )}
                                                      </Grid>
                                                      <Grid item xs={5}>
                                                          {active ? (
                                                              <TextField
                                                                  label="Value"
                                                                  variant="outlined"
                                                                  value={property.value}
                                                                  sx={FieldNoMaxWidth}
                                                                  disabled={!isScenario}
                                                                  data-name="value"
                                                                  data-id={property.id}
                                                                  onChange={updatePropertyField}
                                                              />
                                                          ) : (
                                                              <Typography variant="subtitle2">
                                                                  {property.value}
                                                              </Typography>
                                                          )}
                                                      </Grid>
                                                      <Grid
                                                          item
                                                          xs={2}
                                                          container
                                                          alignContent="center"
                                                          alignItems="center"
                                                          justifyContent="center"
                                                      >
                                                          {active ? (
                                                              <IconButton
                                                                  sx={DeleteIconSx}
                                                                  data-id={property.id}
                                                                  onClick={propertyDelete}
                                                                  disabled={!isScenario}
                                                              >
                                                                  <DeleteOutline
                                                                      fontSize="small"
                                                                      color={isScenario ? "primary" : "disabled"}
                                                                  />
                                                              </IconButton>
                                                          ) : null}
                                                      </Grid>
                                                  </Grid>
                                              );
                                          })
                                        : null}
                                    {active ? (
                                        <Grid item xs={12} spacing={1} container justifyContent="space-between">
                                            <Grid item xs={5}>
                                                <TextField
                                                    value={newProp.key}
                                                    data-name="key"
                                                    onChange={updatePropertyField}
                                                    label="Key"
                                                    variant="outlined"
                                                    sx={FieldNoMaxWidth}
                                                    disabled={!isScenario}
                                                />
                                            </Grid>
                                            <Grid item xs={5}>
                                                <TextField
                                                    value={newProp.value}
                                                    data-name="value"
                                                    onChange={updatePropertyField}
                                                    label="Value"
                                                    variant="outlined"
                                                    sx={FieldNoMaxWidth}
                                                    disabled={!isScenario}
                                                />
                                            </Grid>
                                            <Grid
                                                item
                                                xs={2}
                                                container
                                                alignContent="center"
                                                alignItems="center"
                                                justifyContent="center"
                                            >
                                                <IconButton
                                                    onClick={propertyAdd}
                                                    disabled={!newProp.key || !newProp.value || !isScenario}
                                                >
                                                    <Add color={isScenario ? "primary" : "disabled"} />
                                                </IconButton>
                                            </Grid>
                                        </Grid>
                                    ) : null}

                                    <Grid item xs={12}>
                                        <Divider />
                                    </Grid>
                                </>
                            ) : null}
                            {pipelines ? (
                                <>
                                    <Grid item xs={12} container justifyContent="space-between">
                                        <Typography variant="h6">Pipelines</Typography>
                                    </Grid>

                                    {scPipelines &&
                                        scPipelines.map((item, index) => {
                                            const [key, value] = item;
                                            return (
                                                <PipelineRow
                                                    active={active}
                                                    number={index}
                                                    pipelineId={key}
                                                    value={value}
                                                    key={key}
                                                    submitEntity={submitPipeline}
                                                    enableScenarioFields={isScenario}
                                                    submit={submitPipelines}
                                                />
                                            );
                                        })}

                                    <Grid item xs={12}>
                                        <Divider />
                                    </Grid>
                                </>
                            ) : null}
                            <Grid item xs={12} container justifyContent="space-between">
                                {deleteSc ? (
                                    <Button
                                        variant="outlined"
                                        color="primary"
                                        disabled={!active || !isScenario}
                                        onClick={openDeleteDialog}
                                    >
                                        DELETE
                                    </Button>
                                ) : null}
                                <Button
                                    variant="outlined"
                                    color="primary"
                                    disabled={!active || !isScenario || primary}
                                    onClick={openPrimaryDialog}
                                >
                                    PROMOTE TO PRIMARY
                                </Button>
                            </Grid>
                        </Grid>
                    </AccordionDetails>
                </Accordion>
                <Box>{props.error}</Box>
            </Box>

            <ConfirmDialog
                title="Delete Scenario"
                message="Are you sure you want to delete this scenario?"
                confirm="Delete"
                open={deleteDialog}
                onClose={closeDeleteDialog}
                onConfirm={onDeleteScenario}
            />
            <ConfirmDialog
                title="Promote Scenario"
                message="Are you sure you want to promote this scenario?"
                confirm="Promote"
                open={primaryDialog}
                onClose={closePrimaryDialog}
                onConfirm={onPromote}
            />
        </>
    );
};
export default ScenarioViewer;
