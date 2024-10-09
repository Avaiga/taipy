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

import React, { useState, useCallback, useEffect, ChangeEvent, SyntheticEvent, MouseEvent, KeyboardEvent } from "react";
import Accordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
import Autocomplete from "@mui/material/Autocomplete";
import Chip from "@mui/material/Chip";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid2";
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";

import Add from "@mui/icons-material/Add";
import ArrowForwardIosSharp from "@mui/icons-material/ArrowForwardIosSharp";
import Cancel from "@mui/icons-material/Cancel";
import CheckCircle from "@mui/icons-material/CheckCircle";
import DeleteOutline from "@mui/icons-material/DeleteOutline";
import FlagOutlined from "@mui/icons-material/FlagOutlined";
import Send from "@mui/icons-material/Send";
import deepEqual from "fast-deep-equal/es6";

import {
    createRequestUpdateAction,
    createSendActionNameAction,
    getComponentClassName,
    getUpdateVar,
    useDispatch,
    useDynamicProperty,
    useModule,
} from "taipy-gui";

import {
    AccordionIconSx,
    AccordionSummarySx,
    CoreProps,
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
import StatusChip, { Status } from "./StatusChip";

interface ScenarioViewerProps extends CoreProps {
    expandable?: boolean;
    expanded?: boolean;
    defaultScenario?: string;
    scenario?: ScenarioFull | Array<ScenarioFull>;
    onSubmit?: string;
    onEdit?: string;
    onDelete?: string;
    showConfig?: boolean;
    showCreationDate?: boolean;
    showCycle?: boolean;
    showDelete?: boolean;
    showSequences?: boolean;
    showProperties?: boolean;
    showSubmit?: boolean;
    showSubmitSequences?: boolean;
    showTags?: boolean;
    onSubmissionChange?: string;
    updateScVars?: string;
}

interface SequencesRowProps {
    active: boolean;
    number: number;
    label: string;
    taskIds: string[];
    tasks: Record<string, string>;
    enableScenarioFields: boolean;
    submitEntity: (label: string) => void;
    submit: boolean;
    editSequence: (sLabel: string, label: string, taskIds: string[], del?: boolean) => void;
    onFocus: (e: MouseEvent<HTMLElement>) => void;
    focusName: string;
    setFocusName: (name: string) => void;
    notSubmittableReason: string;
    notEditableReason: string;
    isValid: (sLabel: string, label: string) => boolean;
}

const ChipSx = { ml: 1 };

const tagsAutocompleteSx = {
    "& .MuiOutlinedInput-root": {
        padding: "3px 15px 3px 3px !important",
    },
    maxWidth: "none",
};

type SequenceFull = [string, string[], string, string];
// enum SeFProps {
//     label,
//     tasks,
//     notSubmittableReason,
//     notEditablereason,
// }

const SequenceRow = ({
    active,
    number,
    label: pLabel,
    taskIds: pTaskIds,
    tasks,
    submitEntity,
    enableScenarioFields,
    submit,
    editSequence,
    onFocus,
    focusName,
    setFocusName,
    notSubmittableReason,
    notEditableReason,
    isValid,
}: SequencesRowProps) => {
    const [label, setLabel] = useState("");
    const [taskIds, setTaskIds] = useState<string[]>([]);
    const [valid, setValid] = useState(false);

    const onChange = useCallback((e: ChangeEvent<HTMLInputElement>) => setLabel(e.currentTarget.value), []);

    const onSaveSequence = useCallback(
        (e?: MouseEvent<Element>) => {
            e && e.stopPropagation();
            if (isValid(pLabel, label)) {
                editSequence(pLabel, label, taskIds);
            } else {
                setValid(false);
            }
        },
        [pLabel, label, taskIds, editSequence, isValid]
    );
    const onCancelSequence = useCallback(
        (e?: MouseEvent<Element>) => {
            e && e.stopPropagation();
            setLabel(pLabel);
            setTaskIds(pTaskIds);
            setFocusName("");
        },
        [pLabel, pTaskIds, setFocusName]
    );
    const onSubmitSequence = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            submitEntity(pLabel);
        },
        [submitEntity, pLabel]
    );
    const onDeleteSequence = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            editSequence(pLabel, "", [], true);
        },
        [editSequence, pLabel]
    );

    useEffect(() => setValid(isValid(pLabel, label)), [pLabel, label, isValid]);

    // Tasks
    const onChangeTasks = useCallback((_: SyntheticEvent, taskIds: string[]) => setTaskIds(taskIds), []);
    const getTaskLabel = useCallback((id: string) => tasks[id], [tasks]);

    useEffect(() => {
        setLabel(pLabel);
        setTaskIds(pTaskIds);
    }, [pLabel, pTaskIds]);

    const name = `sequence${number}`;
    const disabled = !enableScenarioFields || !active;
    const disabledSubmit = disabled || !!notSubmittableReason;

    return (
        <Grid size={12} container justifyContent="space-between" data-focus={name} onClick={onFocus} sx={hoverSx}>
            {active && !notEditableReason && focusName === name ? (
                <>
                    <Grid size={4}>
                        <TextField
                            label={`Sequence ${number + 1}`}
                            variant="outlined"
                            value={label}
                            onChange={onChange}
                            sx={FieldNoMaxWidth}
                            disabled={disabled}
                            fullWidth
                            error={!valid}
                            helperText={valid ? "" : label ? "This name is already used." : "Cannot be empty."}
                        />
                    </Grid>
                    <Grid size={4}>
                        <Autocomplete
                            multiple
                            options={Object.keys(tasks)}
                            getOptionLabel={getTaskLabel}
                            renderTags={(values: readonly string[], getTagProps) =>
                                values.map((id: string, index: number) => {
                                    return (
                                        // eslint-disable-next-line react/jsx-key
                                        <Chip
                                            variant="outlined"
                                            label={tasks[id]}
                                            sx={IconPaddingSx}
                                            {...getTagProps({ index })}
                                        />
                                    );
                                })
                            }
                            value={taskIds}
                            onChange={onChangeTasks}
                            fullWidth
                            renderInput={(params) => (
                                <TextField
                                    {...params}
                                    variant="outlined"
                                    label="Tasks"
                                    sx={tagsAutocompleteSx}
                                    fullWidth
                                />
                            )}
                            disabled={disabled}
                        />
                    </Grid>
                    <Grid size={2} container alignContent="center" alignItems="center" justifyContent="center">
                        <Tooltip title="Apply">
                            <IconButton sx={IconPaddingSx} onClick={onSaveSequence} size="small" disabled={!valid}>
                                <CheckCircle color={disableColor("primary", !valid)} />
                            </IconButton>
                        </Tooltip>
                        <Tooltip title="Cancel">
                            <IconButton sx={IconPaddingSx} onClick={onCancelSequence} size="small">
                                <Cancel color="inherit" />
                            </IconButton>
                        </Tooltip>
                    </Grid>
                </>
            ) : (
                <>
                    <Grid size={5}>
                        <Typography variant="subtitle2">{label || "New Sequence"}</Typography>
                    </Grid>
                    <Grid size={5}>
                        {taskIds.map((id) =>
                            tasks[id] ? <Chip key={id} label={tasks[id]} variant="outlined" /> : null
                        )}
                    </Grid>
                    <Grid size={1} alignContent="center" alignItems="center" justifyContent="center">
                        <Tooltip title={`Delete Sequence '${label}'`}>
                            <span>
                                <IconButton size="small" onClick={onDeleteSequence} disabled={disabled}>
                                    <DeleteOutline color={disableColor("primary", disabled)} />
                                </IconButton>
                            </span>
                        </Tooltip>
                    </Grid>
                    <Grid size={1} alignContent="center" alignItems="center" justifyContent="center">
                        {pLabel && submit ? (
                            <Tooltip
                                title={
                                    disabledSubmit
                                        ? notSubmittableReason || `Cannot submit Sequence '${label}'`
                                        : `Submit Sequence '${label}'`
                                }
                            >
                                <span>
                                    <IconButton size="small" onClick={onSubmitSequence} disabled={disabledSubmit}>
                                        <Send color={disableColor("info", disabledSubmit)} />
                                    </IconButton>
                                </span>
                            </Tooltip>
                        ) : null}
                    </Grid>
                </>
            )}
        </Grid>
    );
};

const getValidScenario = (scenar: ScenarioFull | ScenarioFull[]) =>
    scenar.length == ScenarioFullLength && typeof scenar[ScFProps.id] === "string"
        ? (scenar as ScenarioFull)
        : scenar.length == 1
        ? (scenar[0] as ScenarioFull)
        : undefined;

const invalidScenario: ScenarioFull = [
    "",
    false,
    "",
    "",
    "",
    "",
    [],
    [],
    [],
    {},
    [],
    "invalid",
    "invalid",
    "invalid",
    "invalid",
    "invalid",
];

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
        updateScVars = "",
        coreChanged,
    } = props;

    const dispatch = useDispatch();
    const module = useModule();

    const [scenario, setScenario] = useState<ScenarioFull>(invalidScenario);
    const [valid, setValid] = useState(false);

    useEffect(() => {
        let sc: ScenarioFull | undefined = undefined;
        if (Array.isArray(props.scenario)) {
            sc = getValidScenario(props.scenario);
        } else if (props.scenario !== null && props.defaultScenario) {
            try {
                sc = getValidScenario(JSON.parse(props.defaultScenario));
            } catch {
                // DO nothing
            }
        }
        setValid(!!sc);
        setScenario((oldSc) => {
            if (oldSc === sc || (sc && deepEqual(oldSc, sc))) {
                return oldSc;
            }
            setSubmissionStatus(-1);
            return sc || invalidScenario;
        });
    }, [props.scenario, props.defaultScenario]);

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
        scTasks,
        scAuthorizedTags,
        scDeletableReason,
        scPromotableReason,
        scNotSubmittableReason,
        scNotReadableReason,
        scNotEditableReason,
    ] = scenario || invalidScenario;

    const active = useDynamicProperty(props.active, props.defaultActive, true) && !scNotReadableReason;
    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);

    const [deleteDialog, setDeleteDialogOpen] = useState(false);
    const openDeleteDialog = useCallback(() => setDeleteDialogOpen(true), []);
    const closeDeleteDialog = useCallback(() => setDeleteDialogOpen(false), []);
    const onDeleteScenario = useCallback(() => {
        setDeleteDialogOpen(false);
        if (valid) {
            dispatch(
                createSendActionNameAction(
                    id,
                    module,
                    { action: props.onDelete, error_id: getUpdateVar(updateScVars, "error_id") },
                    undefined,
                    undefined,
                    true,
                    true,
                    { id: scId }
                )
            );
        }
    }, [valid, props.onDelete, scId, id, dispatch, module, updateScVars]);

    const [primaryDialog, setPrimaryDialog] = useState(false);
    const openPrimaryDialog = useCallback(() => setPrimaryDialog(true), []);
    const closePrimaryDialog = useCallback(() => setPrimaryDialog(false), []);
    const onPromote = useCallback(() => {
        setPrimaryDialog(false);
        if (valid) {
            dispatch(
                createSendActionNameAction(id, module, props.onEdit, {
                    id: scId,
                    primary: true,
                    error_id: getUpdateVar(updateScVars, "error_id"),
                })
            );
        }
    }, [valid, props.onEdit, scId, id, dispatch, module, updateScVars]);

    // userExpanded
    const [userExpanded, setUserExpanded] = useState(valid && expanded);
    const onExpand = useCallback(
        (e: SyntheticEvent, expand: boolean) => expandable && setUserExpanded(expand),
        [expandable]
    );

    // Submission status
    const [submissionStatus, setSubmissionStatus] = useState(-1);

    // submits
    const submitSequence = useCallback(
        (label: string) => {
            label &&
                dispatch(
                    createSendActionNameAction(id, module, props.onSubmit, {
                        id: scId,
                        sequence: label,
                        on_submission_change: props.onSubmissionChange,
                        error_id: getUpdateVar(updateScVars, "error_id"),
                    })
                );
        },
        [scId, props.onSubmit, props.onSubmissionChange, id, dispatch, module, updateScVars]
    );

    const submitScenario = useCallback(
        (e: React.MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            if (valid) {
                dispatch(
                    createSendActionNameAction(id, module, props.onSubmit, {
                        id: scId,
                        on_submission_change: props.onSubmissionChange,
                        error_id: getUpdateVar(updateScVars, "error_id"),
                    })
                );
                setSubmissionStatus(Status.SUBMITTED);
            }
        },
        [valid, props.onSubmit, props.onSubmissionChange, id, scId, dispatch, module, updateScVars]
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
            if (valid) {
                dispatch(
                    createSendActionNameAction(id, module, props.onEdit, {
                        id: scId,
                        name: label,
                        error_id: getUpdateVar(updateScVars, "error_id"),
                    })
                );
                setFocusName("");
            }
        },
        [valid, props.onEdit, scId, label, id, dispatch, module, updateScVars]
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
        (e: KeyboardEvent<HTMLInputElement>) => {
            if (!e.shiftKey && !e.ctrlKey && !e.altKey) {
                if (e.key == "Enter") {
                    editLabel();
                    e.preventDefault();
                    e.stopPropagation();
                } else if (e.key == "Escape") {
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
        (e?: MouseEvent<HTMLElement>) => {
            e && e.stopPropagation();
            if (valid) {
                dispatch(
                    createSendActionNameAction(id, module, props.onEdit, {
                        id: scId,
                        tags: tags,
                        error_id: getUpdateVar(updateScVars, "error_id"),
                    })
                );
                setFocusName("");
            }
        },
        [valid, props.onEdit, scId, tags, id, dispatch, module, updateScVars]
    );
    const cancelTags = useCallback(
        (e?: MouseEvent<HTMLElement>) => {
            e && e.stopPropagation();
            setTags(scTags);
            setFocusName("");
        },
        [scTags]
    );
    const onChangeTags = useCallback((_: SyntheticEvent, tags: string[]) => setTags(tags), []);
    const onTagsKeyDown = useCallback(
        (e: KeyboardEvent<HTMLInputElement>) => {
            if (!e.shiftKey && !e.ctrlKey && !e.altKey && e.key == "Escape") {
                cancelTags();
                e.preventDefault();
                e.stopPropagation();
            }
        },
        [cancelTags]
    );

    // sequences
    const [sequences, setSequences] = useState<SequenceFull[]>([]);
    const editSequence = useCallback(
        (seqLabel: string, label: string, taskIds: string[], del?: boolean) => {
            if (valid) {
                if (del || label) {
                    dispatch(
                        createSendActionNameAction(id, module, props.onEdit, {
                            id: scId,
                            sequence: seqLabel,
                            name: label,
                            task_ids: taskIds,
                            del: !!del,
                            error_id: getUpdateVar(updateScVars, "error_id"),
                        })
                    );
                } else {
                    setSequences((seqs) => seqs.filter((seq) => seq[0]));
                }
                setFocusName("");
            }
        },
        [valid, id, scId, props.onEdit, dispatch, module, updateScVars]
    );
    const isValidSequence = useCallback(
        (sLabel: string, label: string) => !!label && (sLabel == label || !sequences.find((seq) => seq[0] === label)),
        [sequences]
    );

    const addSequenceHandler = useCallback(() => setSequences((seq) => [...seq, ["", [], "", ""]]), []);

    // on scenario change
    useEffect(() => {
        showTags && setTags(scTags);
        setLabel(scLabel);
        showSequences && setSequences(scSequences);
        setUserExpanded(expanded && valid);
        setFocusName("");
    }, [scTags, scLabel, scSequences, valid, showTags, showSequences, expanded]);

    // Refresh on broadcast
    useEffect(() => {
        const ids = coreChanged?.scenario;
        if (typeof ids === "string" ? ids === scId : Array.isArray(ids) ? ids.includes(scId) : ids) {
            const submission = coreChanged?.submission;
            if (typeof submission === "number") {
                setSubmissionStatus(submission as number);
            }
            props.updateVarName && dispatch(createRequestUpdateAction(id, module, [props.updateVarName], true));
        }
    }, [coreChanged, props.updateVarName, id, module, dispatch, scId]);

    const disabled = !valid || !active || !!scNotSubmittableReason;

    return (
        <>
            <Box sx={MainBoxSx} id={id} onClick={onFocus} className={`${className} ${getComponentClassName(props.children)}`}>
                <Accordion defaultExpanded={expanded} expanded={userExpanded} onChange={onExpand} disabled={!valid}>
                    <AccordionSummary
                        expandIcon={expandable ? <ArrowForwardIosSharp sx={AccordionIconSx} /> : null}
                        sx={AccordionSummarySx}
                    >
                        <Stack direction="row" justifyContent="space-between" width="100%" alignItems="baseline">
                            <Stack direction="row" spacing={1}>
                                <Typography>{scLabel}</Typography>
                                {scPrimary ? (
                                    <Chip
                                        color="primary"
                                        label={<FlagOutlined sx={FlagSx} />}
                                        size="small"
                                        sx={ChipSx}
                                    />
                                ) : null}
                                {submissionStatus > -1 ? <StatusChip status={submissionStatus} sx={ChipSx} /> : null}
                            </Stack>
                            {showSubmit ? (
                                <Tooltip
                                    title={
                                        disabled
                                            ? scNotSubmittableReason || "Cannot submit Scenario"
                                            : "Submit Scenario"
                                    }
                                >
                                    <span>
                                        <Button
                                            onClick={submitScenario}
                                            disabled={disabled}
                                            endIcon={<Send fontSize="medium" color={disableColor("info", disabled)} />}
                                        >
                                            Submit
                                        </Button>
                                    </span>
                                </Tooltip>
                            ) : null}
                        </Stack>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Grid container rowSpacing={2}>
                            {showConfig ? (
                                <Grid size={12} container justifyContent="space-between">
                                    <Grid size={4} pb={2}>
                                        <Typography variant="subtitle2">Config ID</Typography>
                                    </Grid>
                                    <Grid size={8}>
                                        <Typography variant="subtitle2">{scConfig}</Typography>
                                    </Grid>
                                </Grid>
                            ) : null}
                            {showCreationDate ? (
                                <Grid size={12} container justifyContent="space-between">
                                    <Grid size={4}>
                                        <Typography variant="subtitle2">Creation Date</Typography>
                                    </Grid>
                                    <Grid size={8}>
                                        <Typography variant="subtitle2">{scCreationDate}</Typography>
                                    </Grid>
                                </Grid>
                            ) : null}
                            {showCycle ? (
                                <Grid size={12} container justifyContent="space-between">
                                    <Grid size={4}>
                                        <Typography variant="subtitle2">Cycle / Frequency</Typography>
                                    </Grid>
                                    <Grid size={8}>
                                        <Typography variant="subtitle2">{scCycle}</Typography>
                                    </Grid>
                                </Grid>
                            ) : null}
                            <Grid size={12} container justifyContent="space-between" spacing={1}>
                                <Grid
                                    size={12}
                                    container
                                    justifyContent="space-between"
                                    data-focus="label"
                                    onClick={onFocus}
                                    sx={hoverSx}
                                >
                                    {active && !scNotEditableReason && focusName === "label" ? (
                                        <TextField
                                            label="Label"
                                            variant="outlined"
                                            fullWidth
                                            sx={FieldNoMaxWidth}
                                            value={label || ""}
                                            onChange={onLabelChange}
                                            slotProps={{
                                                input: {
                                                    onKeyDown: onLabelKeyDown,
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
                                                <Typography variant="subtitle2">{scLabel}</Typography>
                                            </Grid>
                                        </>
                                    )}
                                </Grid>
                                {showTags ? (
                                    <Grid
                                        size={12}
                                        container
                                        justifyContent="space-between"
                                        data-focus="tags"
                                        onClick={onFocus}
                                        sx={hoverSx}
                                    >
                                        {active && !scNotEditableReason && focusName === "tags" ? (
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
                                                        slotProps={{
                                                            input: {
                                                                ...params.InputProps,
                                                                onKeyDown: onTagsKeyDown,
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
                                                            },
                                                        }}
                                                    />
                                                )}
                                                disabled={!valid}
                                            />
                                        ) : (
                                            <>
                                                <Grid size={4}>
                                                    <Typography variant="subtitle2">Tags</Typography>
                                                </Grid>
                                                <Grid size={8}>
                                                    {tags.map((tag, index) => (
                                                        <Chip key={index} label={tag} variant="outlined" />
                                                    ))}
                                                </Grid>
                                            </>
                                        )}
                                    </Grid>
                                ) : null}
                            </Grid>

                            <Grid size={12}>
                                <Divider />
                            </Grid>
                            <PropertiesEditor
                                entityId={scId}
                                active={active}
                                isDefined={valid}
                                entProperties={scProperties}
                                show={showProperties}
                                focusName={focusName}
                                setFocusName={setFocusName}
                                onFocus={onFocus}
                                onEdit={props.onEdit}
                                notEditableReason={scNotEditableReason}
                                updateVars={updateScVars}
                            />
                            {showSequences ? (
                                <>
                                    <Grid size={12} container justifyContent="space-between">
                                        <Grid size={9}>
                                            <Typography variant="h6">Sequences</Typography>
                                        </Grid>
                                        <Grid size={3} sx={{ ml: "auto" }}>
                                            <Button onClick={addSequenceHandler} endIcon={<Add />}>
                                                Add
                                            </Button>
                                        </Grid>
                                    </Grid>

                                    {sequences.map((item, index) => {
                                        const [label, taskIds, notSubmittableReason, notEditableReason] = item;
                                        return (
                                            <SequenceRow
                                                active={!!active}
                                                number={index}
                                                label={label}
                                                taskIds={taskIds}
                                                tasks={scTasks}
                                                key={label}
                                                submitEntity={submitSequence}
                                                enableScenarioFields={valid}
                                                submit={showSubmitSequences}
                                                editSequence={editSequence}
                                                onFocus={onFocus}
                                                focusName={focusName}
                                                setFocusName={setFocusName}
                                                notSubmittableReason={notSubmittableReason}
                                                notEditableReason={notEditableReason}
                                                isValid={isValidSequence}
                                            />
                                        );
                                    })}

                                    <Grid size={12}>
                                        <Divider />
                                    </Grid>
                                </>
                            ) : null}
                            <Grid size={12} container justifyContent="space-between">
                                {showDelete ? (
                                    <Tooltip title={scDeletableReason}>
                                        <span>
                                            <Button
                                                variant="outlined"
                                                color="primary"
                                                disabled={!active || !valid || !!scDeletableReason}
                                                onClick={openDeleteDialog}
                                            >
                                                DELETE
                                            </Button>
                                        </span>
                                    </Tooltip>
                                ) : null}
                                <Tooltip title={scPromotableReason}>
                                    <span>
                                        <Button
                                            variant="outlined"
                                            color="primary"
                                            disabled={!active || !valid || scPrimary || !!scPromotableReason}
                                            onClick={openPrimaryDialog}
                                        >
                                            PROMOTE TO PRIMARY
                                        </Button>
                                    </span>
                                </Tooltip>
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
            {props.children}
        </>
    );
};
export default ScenarioViewer;
