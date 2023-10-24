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

import React, {
    useState,
    useCallback,
    useEffect,
    useMemo,
    ChangeEvent,
    SyntheticEvent,
    MouseEvent,
    KeyboardEvent,
} from "react";
import Accordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
import Autocomplete from "@mui/material/Autocomplete";
import Chip from "@mui/material/Chip";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import { FlagOutlined, Send, CheckCircle, Cancel, ArrowForwardIosSharp } from "@mui/icons-material";

import {
    createRequestUpdateAction,
    createSendActionNameAction,
    useDispatch,
    useDynamicProperty,
    useModule,
} from "taipy-gui";

import {
    AccordionIconSx,
    AccordionSummarySx,
    FieldNoMaxWidth,
    FlagSx,
    IconPaddingSx,
    MainBoxSx,
    ScFProps,
    ScenarioFull,
    ScenarioFullLength,
    disableColor,
    hoverSx,
    useClassNames,
} from "./utils";
import ConfirmDialog from "./utils/ConfirmDialog";
import PropertiesEditor from "./PropertiesEditor";

interface ScenarioViewerProps {
    id?: string;
    expandable?: boolean;
    expanded?: boolean;
    updateVarName?: string;
    defaultScenario?: string;
    scenario?: ScenarioFull | Array<ScenarioFull>;
    onSubmit?: string;
    onEdit?: string;
    onDelete?: string;
    error?: string;
    coreChanged?: Record<string, unknown>;
    defaultActive: boolean;
    active: boolean;
    showConfig?: boolean;
    showCreationDate?: boolean;
    showCycle?: boolean;
    showDelete?: boolean;
    showSequences?: boolean;
    showProperties?: boolean;
    showSubmit?: boolean;
    showSubmitSequences?: boolean;
    showTags?: boolean;
    libClassName?: string;
    className?: string;
    dynamicClassName?: string;
    onSubmissionChange?: string;
}

interface SequencesRowProps {
    active: boolean;
    number: number;
    id: string;
    label: string;
    enableScenarioFields: boolean;
    submitEntity: (id: string) => void;
    submit: boolean;
    editLabel: (id: string, label: string) => void;
    onFocus: (e: MouseEvent<HTMLElement>) => void;
    focusName: string;
    setFocusName: (name: string) => void;
    submittable: boolean;
    editable: boolean;
}

const ChipSx = { ml: 1 };

const tagsAutocompleteSx = {
    "& .MuiOutlinedInput-root": {
        padding: "3px 15px 3px 3px !important",
    },
    maxWidth: "none",
};

const SequenceRow = ({
    active,
    number,
    id,
    label,
    submitEntity,
    enableScenarioFields,
    submit,
    editLabel,
    onFocus,
    focusName,
    setFocusName,
    submittable,
    editable,
}: SequencesRowProps) => {
    const [sequence, setSequence] = useState<string>(label);

    const onChange = useCallback((e: ChangeEvent<HTMLInputElement>) => setSequence(e.currentTarget.value), []);
    const onSaveField = useCallback(
        (e?: MouseEvent<Element>) => {
            e && e.stopPropagation();
            editLabel(id, sequence);
        },
        [id, sequence, editLabel]
    );
    const onCancelField = useCallback(
        (e?: MouseEvent<Element>) => {
            e && e.stopPropagation();
            setSequence(label);
            setFocusName("");
        },
        [label, setFocusName]
    );
    const onSubmitSequence = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            submitEntity(id);
        },
        [submitEntity, id]
    );
    const onKeyDown = useCallback(
        (e: KeyboardEvent<HTMLDivElement>) => {
            if (!e.shiftKey && !e.ctrlKey && !e.altKey) {
                if (e.key == "Enter") {
                    onSaveField();
                    e.preventDefault();
                    e.stopPropagation();
                } else if (e.key == "Esc") {
                    onCancelField();
                    e.preventDefault();
                    e.stopPropagation();
                }
            }
        },
        [onSaveField, onCancelField]
    );

    useEffect(() => setSequence(label), [label]);

    const name = `sequence${number}`;
    const disabled = !enableScenarioFields || !active || !submittable;

    return (
        <Grid item xs={12} container justifyContent="space-between" data-focus={name} onClick={onFocus} sx={hoverSx}>
            <Grid item container xs={10}>
                {active && editable && focusName === name ? (
                    <TextField
                        label={`Sequence ${number + 1}`}
                        variant="outlined"
                        value={sequence}
                        onChange={onChange}
                        onKeyDown={onKeyDown}
                        sx={FieldNoMaxWidth}
                        disabled={!enableScenarioFields || !active}
                        fullWidth
                        InputProps={{
                            endAdornment: (
                                <InputAdornment position="end">
                                    <Tooltip title="Apply">
                                        <IconButton sx={IconPaddingSx} onClick={onSaveField} size="small">
                                            <CheckCircle color="primary" />
                                        </IconButton>
                                    </Tooltip>
                                    <Tooltip title="Cancel">
                                        <IconButton sx={IconPaddingSx} onClick={onCancelField} size="small">
                                            <Cancel color="inherit" />
                                        </IconButton>
                                    </Tooltip>
                                </InputAdornment>
                            ),
                        }}
                    />
                ) : (
                    <Typography variant="subtitle2">{sequence}</Typography>
                )}
            </Grid>
            <Grid item xs={2} container alignContent="center" alignItems="center" justifyContent="center">
                {submit ? (
                    <Tooltip title={disabled ? "Cannot submit Sequence" : "Submit Sequence"}>
                        <span>
                            <IconButton size="small" onClick={onSubmitSequence} disabled={disabled}>
                                <Send color={disableColor("info", disabled)} />
                            </IconButton>
                        </span>
                    </Tooltip>
                ) : null}
            </Grid>
        </Grid>
    );
};

const getValidScenario = (scenar: ScenarioFull | ScenarioFull[]) =>
    scenar.length == ScenarioFullLength && typeof scenar[ScFProps.id] === "string"
        ? (scenar as ScenarioFull)
        : scenar.length == 1
        ? (scenar[0] as ScenarioFull)
        : undefined;

const ScenarioViewer = (props: ScenarioViewerProps) => {
    const {
        id = "",
        expandable = true,
        expanded = true,
        showConfig = false,
        showCreationDate = false,
        showCycle = false,
        showDelete = true,
        showProperties = true,
        showSequences = true,
        showSubmit = true,
        showSubmitSequences = true,
        showTags = true,
    } = props;

    const dispatch = useDispatch();
    const module = useModule();

    const [
        scId,
        scPrimary,
        scConfig,
        scCreationDate,
        scCycle,
        scLabel,
        scTags,
        scProperties,
        scSequences,
        scAuthorizedTags,
        scDeletable,
        scPromotable,
        scSubmittable,
        scReadable,
        scEditable,
        isScenario,
    ] = useMemo(() => {
        let sc: ScenarioFull | undefined = undefined;
        if (Array.isArray(props.scenario)) {
            sc = getValidScenario(props.scenario);
        } else if (props.defaultScenario) {
            try {
                sc = getValidScenario(JSON.parse(props.defaultScenario));
            } catch {
                // DO nothing
            }
        }
        return sc
            ? [...sc, true]
            : ["", false, "", "", "", "", [], [], [], [], false, false, false, false, false, false];
    }, [props.scenario, props.defaultScenario]);

    const active = useDynamicProperty(props.active, props.defaultActive, true) && scReadable;
    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);

    const [deleteDialog, setDeleteDialogOpen] = useState(false);
    const openDeleteDialog = useCallback(() => setDeleteDialogOpen(true), []);
    const closeDeleteDialog = useCallback(() => setDeleteDialogOpen(false), []);
    const onDeleteScenario = useCallback(() => {
        setDeleteDialogOpen(false);
        if (isScenario) {
            dispatch(createSendActionNameAction(id, module, props.onDelete, true, true, { id: scId }));
        }
    }, [isScenario, props.onDelete, scId, id, dispatch, module]);

    const [primaryDialog, setPrimaryDialog] = useState(false);
    const openPrimaryDialog = useCallback(() => setPrimaryDialog(true), []);
    const closePrimaryDialog = useCallback(() => setPrimaryDialog(false), []);
    const onPromote = useCallback(() => {
        setPrimaryDialog(false);
        if (isScenario) {
            dispatch(createSendActionNameAction(id, module, props.onEdit, { id: scId, primary: true }));
        }
    }, [isScenario, props.onEdit, scId, id, dispatch, module]);

    // userExpanded
    const [userExpanded, setUserExpanded] = useState(isScenario && expanded);
    const onExpand = useCallback(
        (e: SyntheticEvent, expand: boolean) => expandable && setUserExpanded(expand),
        [expandable]
    );

    // submits
    const submitSequence = useCallback(
        (sequenceId: string) => {
            dispatch(
                createSendActionNameAction(id, module, props.onSubmit, {
                    id: sequenceId,
                    on_submission_change: props.onSubmissionChange,
                    type: "Sequence",
                })
            );
        },
        [props.onSubmit, props.onSubmissionChange, id, dispatch, module]
    );

    const submitScenario = useCallback(
        (e: React.MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            if (isScenario) {
                dispatch(
                    createSendActionNameAction(id, module, props.onSubmit, {
                        id: scId,
                        on_submission_change: props.onSubmissionChange,
                    })
                );
            }
        },
        [isScenario, props.onSubmit, props.onSubmissionChange, id, scId, dispatch, module]
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
        (e?: MouseEvent<HTMLElement>) => {
            e && e.stopPropagation();
            if (isScenario) {
                dispatch(createSendActionNameAction(id, module, props.onEdit, { id: scId, name: label }));
                setFocusName("");
            }
        },
        [isScenario, props.onEdit, scId, label, id, dispatch, module]
    );
    const cancelLabel = useCallback(
        (e?: MouseEvent<HTMLElement>) => {
            e && e.stopPropagation();
            setLabel(scLabel);
            setFocusName("");
        },
        [scLabel, setLabel, setFocusName]
    );
    const onLabelChange = useCallback((e: ChangeEvent<HTMLInputElement>) => setLabel(e.target.value), []);
    const onLabelKeyDown = useCallback(
        (e: KeyboardEvent<HTMLDivElement>) => {
            if (!e.shiftKey && !e.ctrlKey && !e.altKey) {
                if (e.key == "Enter") {
                    editLabel();
                    e.preventDefault();
                    e.stopPropagation();
                } else if (e.key == "Esc") {
                    cancelLabel();
                    e.preventDefault();
                    e.stopPropagation();
                }
            }
        },
        [editLabel, cancelLabel]
    );

    // tags
    const [tags, setTags] = useState<string[]>([]);
    const editTags = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            if (isScenario) {
                dispatch(createSendActionNameAction(id, module, props.onEdit, { id: scId, tags: tags }));
                setFocusName("");
            }
        },
        [isScenario, props.onEdit, scId, tags, id, dispatch, module]
    );
    const cancelTags = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            setTags(scTags);
            setFocusName("");
        },
        [scTags]
    );
    const onChangeTags = useCallback((_: SyntheticEvent, tags: string[]) => setTags(tags), []);

    // sequences
    const editSequence = useCallback(
        (id: string, label: string) => {
            if (isScenario) {
                dispatch(
                    createSendActionNameAction(id, module, props.onEdit, { id: id, name: label, type: "Sequence" })
                );
                setFocusName("");
            }
        },
        [isScenario, props.onEdit, dispatch, module]
    );

    // on scenario change
    useEffect(() => {
        showTags && setTags(scTags);
        setLabel(scLabel);
        setUserExpanded(expanded && isScenario);
    }, [scTags, scLabel, isScenario, showTags, expanded]);

    // Refresh on broadcast
    useEffect(() => {
        const ids = props.coreChanged?.scenario;
        if (typeof ids === "string" ? ids === scId : Array.isArray(ids) ? ids.includes(scId) : ids) {
            props.updateVarName && dispatch(createRequestUpdateAction(id, module, [props.updateVarName], true));
        }
    }, [props.coreChanged, props.updateVarName, id, module, dispatch, scId]);

    const disabled = !isScenario || !active || !scSubmittable;

    return (
        <>
            <Box sx={MainBoxSx} id={id} onClick={onFocus} className={className}>
                <Accordion
                    defaultExpanded={expanded}
                    expanded={userExpanded}
                    onChange={onExpand}
                    disabled={!isScenario}
                >
                    <AccordionSummary
                        expandIcon={expandable ? <ArrowForwardIosSharp sx={AccordionIconSx} /> : null}
                        sx={AccordionSummarySx}
                    >
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
                                {scPrimary ? (
                                    <Chip
                                        color="primary"
                                        label={<FlagOutlined sx={FlagSx} />}
                                        size="small"
                                        sx={ChipSx}
                                    />
                                ) : null}
                            </Grid>
                            <Grid item>
                                {showSubmit ? (
                                    <Tooltip title={disabled ? "Cannot submit Scenario" : "Submit Scenario"}>
                                        <span>
                                            <IconButton sx={IconPaddingSx} onClick={submitScenario} disabled={disabled}>
                                                <Send fontSize="medium" color={disableColor("info", disabled)} />
                                            </IconButton>
                                        </span>
                                    </Tooltip>
                                ) : null}
                            </Grid>
                        </Grid>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Grid container rowSpacing={2}>
                            {showConfig ? (
                                <Grid item xs={12} container justifyContent="space-between">
                                    <Grid item xs={4} pb={2}>
                                        <Typography variant="subtitle2">Config ID</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        <Typography variant="subtitle2">{scConfig}</Typography>
                                    </Grid>
                                </Grid>
                            ) : null}
                            {showCreationDate ? (
                                <Grid item xs={12} container justifyContent="space-between">
                                    <Grid item xs={4}>
                                        <Typography variant="subtitle2">Creation Date</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        <Typography variant="subtitle2">{scCreationDate}</Typography>
                                    </Grid>
                                </Grid>
                            ) : null}
                            {showCycle ? (
                                <Grid item xs={12} container justifyContent="space-between">
                                    <Grid item xs={4}>
                                        <Typography variant="subtitle2">Cycle / Frequency</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        <Typography variant="subtitle2">{scCycle}</Typography>
                                    </Grid>
                                </Grid>
                            ) : null}
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
                                    {active && scEditable && focusName === "label" ? (
                                        <TextField
                                            label="Label"
                                            variant="outlined"
                                            fullWidth
                                            sx={FieldNoMaxWidth}
                                            value={label || ""}
                                            onChange={onLabelChange}
                                            onKeyDown={onLabelKeyDown}
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
                                            disabled={!isScenario}
                                        />
                                    ) : (
                                        <>
                                            <Grid item xs={4}>
                                                <Typography variant="subtitle2">Label</Typography>
                                            </Grid>
                                            <Grid item xs={8}>
                                                <Typography variant="subtitle2">{scLabel}</Typography>
                                            </Grid>
                                        </>
                                    )}
                                </Grid>
                                {showTags ? (
                                    <Grid
                                        item
                                        xs={12}
                                        container
                                        justifyContent="space-between"
                                        data-focus="tags"
                                        onClick={onFocus}
                                        sx={hoverSx}
                                    >
                                        {active && scEditable && focusName === "tags" ? (
                                            <Autocomplete
                                                multiple
                                                options={scAuthorizedTags}
                                                freeSolo={!scAuthorizedTags.length}
                                                renderTags={(value: readonly string[], getTagProps) =>
                                                    value.map((option: string, index: number) => {
                                                        return (
                                                            // eslint-disable-next-line react/jsx-key
                                                            <Chip
                                                                variant="outlined"
                                                                label={option}
                                                                sx={IconPaddingSx}
                                                                {...getTagProps({ index })}
                                                            />
                                                        );
                                                    })
                                                }
                                                value={tags}
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
                                                            endAdornment: (
                                                                <>
                                                                    <Tooltip title="Apply">
                                                                        <IconButton
                                                                            sx={IconPaddingSx}
                                                                            onClick={editTags}
                                                                            size="small"
                                                                        >
                                                                            <CheckCircle color="primary" />
                                                                        </IconButton>
                                                                    </Tooltip>
                                                                    <Tooltip title="Cancel">
                                                                        <IconButton
                                                                            sx={IconPaddingSx}
                                                                            onClick={cancelTags}
                                                                            size="small"
                                                                        >
                                                                            <Cancel color="inherit" />
                                                                        </IconButton>
                                                                    </Tooltip>
                                                                </>
                                                            ),
                                                        }}
                                                    />
                                                )}
                                                disabled={!isScenario}
                                            />
                                        ) : (
                                            <>
                                                <Grid item xs={4}>
                                                    <Typography variant="subtitle2">Tags</Typography>
                                                </Grid>
                                                <Grid item xs={8}>
                                                    {tags.map((tag, index) => (
                                                        <Chip key={index} label={tag} variant="outlined" />
                                                    ))}
                                                </Grid>
                                            </>
                                        )}
                                    </Grid>
                                ) : null}
                            </Grid>

                            <Grid item xs={12}>
                                <Divider />
                            </Grid>
                            <PropertiesEditor
                                entityId={scId}
                                active={active}
                                isDefined={isScenario}
                                entProperties={scProperties}
                                show={showProperties}
                                focusName={focusName}
                                setFocusName={setFocusName}
                                onFocus={onFocus}
                                onEdit={props.onEdit}
                                editable={scEditable}
                            />
                            {showSequences ? (
                                <>
                                    <Grid item xs={12} container justifyContent="space-between">
                                        <Typography variant="h6">Sequences</Typography>
                                    </Grid>

                                    {scSequences &&
                                        scSequences.map((item, index) => {
                                            const [key, value, submittable, editable] = item;
                                            return (
                                                <SequenceRow
                                                    active={active}
                                                    number={index}
                                                    id={key}
                                                    label={value}
                                                    key={key}
                                                    submitEntity={submitSequence}
                                                    enableScenarioFields={isScenario}
                                                    submit={showSubmitSequences}
                                                    editLabel={editSequence}
                                                    onFocus={onFocus}
                                                    focusName={focusName}
                                                    setFocusName={setFocusName}
                                                    submittable={submittable}
                                                    editable={editable}
                                                />
                                            );
                                        })}

                                    <Grid item xs={12}>
                                        <Divider />
                                    </Grid>
                                </>
                            ) : null}
                            <Grid item xs={12} container justifyContent="space-between">
                                {showDelete ? (
                                    <Button
                                        variant="outlined"
                                        color="primary"
                                        disabled={!active || !isScenario || !scDeletable}
                                        onClick={openDeleteDialog}
                                    >
                                        DELETE
                                    </Button>
                                ) : null}
                                <Button
                                    variant="outlined"
                                    color="primary"
                                    disabled={!active || !isScenario || scPrimary || !scPromotable}
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
