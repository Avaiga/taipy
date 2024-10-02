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

import React, { useEffect, useState, useCallback, useMemo, MouseEvent, useRef } from "react";

import Add from "@mui/icons-material/Add";
import CloseIcon from "@mui/icons-material/Close";
import DeleteOutline from "@mui/icons-material/DeleteOutline";
import DescriptionOutlinedIcon from "@mui/icons-material/DescriptionOutlined";
import FilterList from "@mui/icons-material/FilterList";
import StopCircleOutlined from "@mui/icons-material/StopCircleOutlined";

import { Theme } from "@mui/material";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material//DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import FormControl from "@mui/material/FormControl";
import Grid from "@mui/material/Grid2";
import IconButton from "@mui/material/IconButton";
import InputLabel from "@mui/material/InputLabel";
import ListItemText from "@mui/material/ListItemText";
import MenuItem from "@mui/material/MenuItem";
import Paper from "@mui/material/Paper";
import Popover from "@mui/material/Popover";
import Select from "@mui/material/Select";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Toolbar from "@mui/material/Toolbar";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";

import { useFormik } from "formik";

import {
    createRequestUpdateAction,
    createSendActionNameAction,
    createSendUpdateAction,
    createUnBroadcastAction,
    getUpdateVar,
    useDispatch,
    useDispatchRequestUpdateOnFirstRender,
    useModule,
} from "taipy-gui";

import {
    disableColor,
    getUpdateVarNames,
    popoverOrigin,
    useClassNames,
    EllipsisSx,
    SecondaryEllipsisProps,
    CoreProps,
} from "./utils";
import StatusChip, { Status } from "./StatusChip";
import JobViewer, { JobDetail } from "./JobViewer";

const CloseDialogSx = {
    position: "absolute",
    right: 8,
    top: 8,
    color: (theme: Theme) => theme.palette.grey[500],
};

const RightButtonSx = { marginLeft: "auto !important" };

interface JobSelectorProps extends CoreProps {
    jobs: Jobs;
    onSelect?: string;
    height: string;
    showId?: boolean;
    showSubmittedLabel?: boolean;
    showSubmittedId?: boolean;
    showSubmissionId?: boolean;
    showDate?: boolean;
    showCancel?: boolean;
    showDelete?: boolean;
    onJobAction: string;
    onChange?: string;
    value?: string;
    defaultValue?: string;
    updateJbVars?: string;
    details?: JobDetail;
    onDetails?: string | boolean;
}

// job id, job name, empty list, entity id, entity name, submit id, creation date, status, not deletable, not readable, not editable
type Job = [string, string, [], string, string, string, string, number, string, string, string];
type Jobs = Array<Job>;

enum JobProps {
    id,
    name,
    _,
    submitted_id,
    submitted_label,
    submission_id,
    creation_date,
    status,
    not_deletable,
    not_readable,
    not_editable,
}
const JobLength = Object.keys(JobProps).length / 2;

const containerSx = { width: "100%", mb: 2 };
const selectSx = { height: 50 };
const containerPopupSx = { width: "619px" };
const tableWidthSx = { minWidth: 750 };

type JobSelectorColumns = {
    id: string;
    primaryLabel: string;
    showPrimaryLabel?: boolean;
    secondaryLabel?: string;
    showSecondayLabel?: boolean;
    columnIndex: number;
};

type FilterData = {
    data: number;
    operator: string;
    value: string;
};

interface FilterProps {
    open: boolean;
    anchorEl: HTMLButtonElement | null;
    handleFilterClose: () => void;
    handleApplyFilter: (filters: FilterData[]) => void;
    columns: JobSelectorColumns[];
}
const Filter = ({ open, anchorEl, handleFilterClose, handleApplyFilter, columns }: FilterProps) => {
    const form = useFormik<{
        filters: FilterData[];
        newData: "" | number;
        newOperator: "is" | "isnot";
        newValue: string;
    }>({
        initialValues: {
            filters: [],
            newData: "",
            newOperator: "is",
            newValue: "",
        },
        onSubmit: () => {
            applyFilter();
        },
    });

    const removeFilter = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            const { idx } = e.currentTarget.dataset || {};
            form.setFieldValue(
                "filters",
                form.values.filters.filter((_, i) => "" + i !== idx)
            );
        },
        [form]
    );

    const addFilter = useCallback(() => {
        const newFilters = [
            ...form.values.filters,
            {
                data: form.values.newData,
                operator: form.values.newOperator,
                value: form.values.newValue,
            },
        ];
        form.setFieldValue("filters", newFilters);
        form.setFieldValue("newData", "");
        form.setFieldValue("newOperator", "");
        form.setFieldValue("newValue", "");
    }, [form]);

    const applyFilter = useCallback(() => {
        handleApplyFilter([...form.values.filters]);
        handleFilterClose();
    }, [form, handleApplyFilter, handleFilterClose]);

    const removeAllFilter = useCallback(() => {
        const filters: FilterData[] = [];
        form.setFieldValue("filters", filters);
        handleApplyFilter(filters);
        handleFilterClose();
    }, [form, handleApplyFilter, handleFilterClose]);

    return (
        <Popover
            id="filter-container"
            open={open}
            anchorEl={anchorEl}
            onClose={handleFilterClose}
            anchorOrigin={popoverOrigin}
        >
            <form onSubmit={form.handleSubmit}>
                <Grid container p={3} sx={containerPopupSx}>
                    {form && form.values.filters && form.values.filters.length > 0
                        ? form.values.filters.map((filter, index) => {
                              return (
                                  <Grid size={12} container spacing={2} mb={1} key={index}>
                                      <Grid size={3}>
                                          <FormControl fullWidth>
                                              <InputLabel id="data">Column</InputLabel>
                                              <Select
                                                  labelId="data"
                                                  sx={selectSx}
                                                  label="Column"
                                                  {...form.getFieldProps(`filters.${index}.data`)}
                                              >
                                                  {columns
                                                      .filter(
                                                          (item) =>
                                                              item.columnIndex >= 0 &&
                                                              (item.showPrimaryLabel || item.showSecondayLabel)
                                                      )
                                                      .map((item) => (
                                                          <MenuItem key={item.id} value={item.columnIndex}>
                                                              {item.primaryLabel}
                                                          </MenuItem>
                                                      ))}
                                              </Select>
                                          </FormControl>
                                      </Grid>
                                      <Grid size={3}>
                                          <FormControl fullWidth>
                                              <InputLabel id="operator">Operator</InputLabel>
                                              <Select
                                                  labelId="operator"
                                                  sx={selectSx}
                                                  label="Operator"
                                                  {...form.getFieldProps(`filters.${index}.operator`)}
                                              >
                                                  <MenuItem value="is">is</MenuItem>
                                                  <MenuItem value="isnot">is not</MenuItem>
                                              </Select>
                                          </FormControl>
                                      </Grid>
                                      <Grid size={5}>
                                          <TextField
                                              label="Value"
                                              variant="outlined"
                                              {...form.getFieldProps(`filters.${index}.value`)}
                                          />
                                      </Grid>
                                      <Grid size={1}>
                                          <Tooltip title="Delete Filter">
                                              <IconButton data-idx={index} onClick={removeFilter}>
                                                  <DeleteOutline />
                                              </IconButton>
                                          </Tooltip>
                                      </Grid>
                                  </Grid>
                              );
                          })
                        : null}
                    <Grid size={12} container spacing={2} justifyContent="space-between">
                        <Grid size={3}>
                            <FormControl fullWidth>
                                <InputLabel id="data-new">Column</InputLabel>
                                <Select
                                    labelId="data-new"
                                    sx={selectSx}
                                    label="Column"
                                    {...form.getFieldProps(`newData`)}
                                >
                                    {columns
                                        .filter(
                                            (item) =>
                                                item.columnIndex >= 0 &&
                                                (item.showPrimaryLabel || item.showSecondayLabel)
                                        )
                                        .map((item) => (
                                            <MenuItem key={item.id} value={item.columnIndex}>
                                                {item.primaryLabel}
                                            </MenuItem>
                                        ))}
                                </Select>
                            </FormControl>
                        </Grid>
                        <Grid size={3}>
                            <FormControl fullWidth>
                                <InputLabel id="operator-new">Operator</InputLabel>
                                <Select
                                    labelId="operator-new"
                                    sx={selectSx}
                                    label="Operator"
                                    {...form.getFieldProps(`newOperator`)}
                                >
                                    <MenuItem value="is">is</MenuItem>
                                    <MenuItem value="isnot">is not</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                        <Grid size={5}>
                            <TextField label="Value" variant="outlined" {...form.getFieldProps(`newValue`)} />
                        </Grid>
                        <Grid size={1}>
                            <Tooltip
                                title={typeof form.values.newData === "string" ? "Cannot Add Filter" : "Add Filter"}
                            >
                                <IconButton onClick={addFilter} disabled={typeof form.values.newData === "string"}>
                                    <Add color={disableColor("primary", typeof form.values.newData === "string")} />
                                </IconButton>
                            </Tooltip>
                        </Grid>
                    </Grid>
                    <Grid size={12} container justifyContent="space-between" mt={2}>
                        <Button
                            variant="outlined"
                            color="inherit"
                            onClick={removeAllFilter}
                            disabled={!form.values.filters.length}
                        >
                            Remove all filters
                        </Button>
                        <Button variant="contained" type="submit">
                            Apply {form.values.filters.length} filter{form.values.filters.length > 1 ? "s" : ""}
                        </Button>
                    </Grid>
                </Grid>
            </form>
        </Popover>
    );
};

interface JobSelectedTableHeadProps {
    jobs: number;
    selected: number;
    handleSelectAllClick?: (event: React.ChangeEvent<HTMLInputElement>) => void;
    columns: JobSelectorColumns[];
}
const JobSelectedTableHead = ({ jobs, selected, handleSelectAllClick, columns }: JobSelectedTableHeadProps) => (
    <TableHead>
        <TableRow>
            <TableCell padding="checkbox">
                <Checkbox
                    color="primary"
                    checked={!!jobs && jobs == selected}
                    indeterminate={!!jobs && !!selected && jobs != selected}
                    onChange={handleSelectAllClick}
                />
            </TableCell>
            {columns
                .filter((c) => c.showPrimaryLabel || c.showSecondayLabel)
                .map((col) => (
                    <TableCell key={col.id}>
                        {col.secondaryLabel ? (
                            <ListItemText primary={col.primaryLabel} secondary={col.secondaryLabel} />
                        ) : (
                            col.primaryLabel
                        )}
                    </TableCell>
                ))}
        </TableRow>
    </TableHead>
);

interface JobSelectedTableRowProps {
    row: Job;
    isSelected: boolean;
    isItemSelected: boolean;
    handleSelection: (event: React.MouseEvent<HTMLElement>) => void;
    handleCheckboxClick: (event: React.MouseEvent<HTMLElement>) => void;
    handleCancelJobs: (event: React.MouseEvent<HTMLElement>) => void;
    handleDeleteJobs: (event: React.MouseEvent<HTMLElement>) => void;
    handleShowDetails: false | ((event: React.MouseEvent<HTMLElement>) => void);
    showId?: boolean;
    showSubmittedLabel?: boolean;
    showSubmittedId?: boolean;
    showSubmissionId?: boolean;
    showDate?: boolean;
    showCancel?: boolean;
    showDelete?: boolean;
}
const JobSelectedTableRow = ({
    row,
    isSelected,
    isItemSelected,
    handleSelection,
    handleCheckboxClick,
    handleCancelJobs,
    handleDeleteJobs,
    handleShowDetails,
    showId,
    showSubmittedLabel,
    showSubmittedId,
    showSubmissionId,
    showDate,
    showCancel,
    showDelete,
}: JobSelectedTableRowProps) => {
    const [id, jobName, , entityId, entityName, submitId, creationDate, status] = row;

    return (
        <TableRow
            hover
            role="checkbox"
            tabIndex={-1}
            key={id}
            data-id={id}
            onClick={handleSelection}
            selected={isSelected}
        >
            <TableCell padding="checkbox">
                <Checkbox color="primary" checked={isItemSelected} data-id={id} onClick={handleCheckboxClick} />
            </TableCell>
            {showId ? (
                <TableCell component="th" scope="row" padding="none">
                    <ListItemText primary={jobName} secondary={id} secondaryTypographyProps={SecondaryEllipsisProps} />
                </TableCell>
            ) : null}
            {showSubmissionId ? <TableCell>{submitId}</TableCell> : null}
            {showSubmittedLabel || showSubmittedId ? (
                <TableCell>
                    {!showSubmittedLabel && showSubmittedId ? (
                        <Typography sx={EllipsisSx}>{entityId}</Typography>
                    ) : !showSubmittedId && showSubmittedLabel ? (
                        <Typography>{entityName}</Typography>
                    ) : (
                        <ListItemText
                            primary={entityName}
                            secondary={entityId}
                            secondaryTypographyProps={SecondaryEllipsisProps}
                        />
                    )}
                </TableCell>
            ) : null}
            {showDate ? <TableCell>{creationDate ? new Date(creationDate).toLocaleString() : ""}</TableCell> : null}
            <TableCell>
                <StatusChip status={status} />
            </TableCell>
            {showCancel || showDelete || handleShowDetails ? (
                <TableCell>
                    {handleShowDetails ? (
                        <Tooltip title="Show details">
                            <IconButton data-id={id} onClick={handleShowDetails}>
                                <DescriptionOutlinedIcon />
                            </IconButton>
                        </Tooltip>
                    ) : null}
                    {status === Status.RUNNING ? null : status === Status.BLOCKED ||
                      status === Status.PENDING ||
                      status === Status.SUBMITTED ? (
                        showCancel ? (
                            <Tooltip title="Cancel Job">
                                <IconButton data-id={id} onClick={handleCancelJobs}>
                                    <StopCircleOutlined />
                                </IconButton>
                            </Tooltip>
                        ) : null
                    ) : showDelete ? (
                        <Tooltip title="Delete Job">
                            <IconButton data-id={id} onClick={handleDeleteJobs}>
                                <DeleteOutline color="primary" />
                            </IconButton>
                        </Tooltip>
                    ) : null}
                </TableCell>
            ) : null}
        </TableRow>
    );
};

const JobSelector = (props: JobSelectorProps) => {
    const {
        id = "",
        showId = true,
        showSubmittedLabel = true,
        showSubmittedId = true,
        showSubmissionId = true,
        showDate = true,
        showCancel = true,
        showDelete = true,
        propagate = true,
        updateJbVars = "",
        coreChanged,
    } = props;
    const [checked, setChecked] = useState<string[]>([]);
    const [selected, setSelected] = useState<string[]>([]);
    const [jobRows, setJobRows] = useState<Jobs>([]);
    const [filters, setFilters] = useState<FilterData[]>();
    const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
    const [showDetails, setShowDetails] = useState(false);
    const detailId = useRef<string>();

    const dispatch = useDispatch();
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);

    useDispatchRequestUpdateOnFirstRender(dispatch, id, module, props.updateVars);

    const headerToolbarSx = useMemo(
        () => ({
            pl: { sm: 2 },
            pr: { xs: 1, sm: 1 },
            ...(checked.length > 0
                ? {
                      bgcolor: "rgba(0, 0, 0, 0.05)",
                  }
                : {}),
        }),
        [checked]
    );

    const jobSelectorColumns: JobSelectorColumns[] = useMemo(
        () => [
            {
                id: "jobId",
                primaryLabel: "Job",
                showPrimaryLabel: showId,
                secondaryLabel: "ID",
                showSecondayLabel: showId,
                columnIndex: JobProps.id,
            },
            {
                id: "submitID",
                primaryLabel: "Submission ID",
                columnIndex: JobProps.submission_id,
                showPrimaryLabel: showSubmissionId,
                showSecondayLabel: showSubmissionId,
            },
            {
                id: "submitEntity",
                primaryLabel: "Submitted entity",
                secondaryLabel: "ID",
                columnIndex: JobProps.submitted_id,
                showPrimaryLabel: showSubmittedLabel,
                showSecondayLabel: showSubmittedId,
            },
            {
                id: "createdDt",
                primaryLabel: "Creation date",
                columnIndex: JobProps.creation_date,
                showPrimaryLabel: showDate,
                showSecondayLabel: showDate,
            },
            {
                id: "status",
                primaryLabel: "Status",
                columnIndex: JobProps.status,
                showPrimaryLabel: true,
                showSecondayLabel: true,
            },
            {
                id: "actions",
                columnIndex: -1,
                primaryLabel: "Actions",
                showPrimaryLabel: showCancel,
                showSecondayLabel: showDelete,
            },
        ],
        [showDate, showSubmittedId, showSubmittedLabel, showId, showSubmissionId, showCancel, showDelete]
    );

    const handleClick = useCallback((event: React.MouseEvent<HTMLElement>) => {
        event.stopPropagation();
        const { id = "" } = event.currentTarget?.dataset || {};
        setChecked((oldChecked) => {
            const newChecked = [...oldChecked];
            const checkedIndex = newChecked.indexOf(id);

            if (checkedIndex === -1) {
                newChecked.push(id);
            } else {
                newChecked.splice(checkedIndex, 1);
            }
            return newChecked;
        });
    }, []);

    const handleSelection = useCallback(
        (event: React.MouseEvent<HTMLElement>) => {
            const { id = "" } = event.currentTarget?.dataset || {};
            setSelected((oldSelected) => {
                const newSelected = [...oldSelected];
                const selectedIndex = newSelected.indexOf(id);

                if (selectedIndex === -1) {
                    newSelected.push(id);
                } else {
                    newSelected.splice(selectedIndex, 1);
                }
                const jobsVar = getUpdateVar(props.updateVars, "jobs");
                dispatch(
                    createSendUpdateAction(props.updateVarName, newSelected, module, props.onChange, propagate, jobsVar)
                );
                return newSelected;
            });
        },
        [dispatch, module, props.onChange, props.updateVars, props.updateVarName, propagate]
    );

    const handleCheckAllClick = useCallback(
        (event: React.ChangeEvent<HTMLInputElement>) =>
            setChecked(event.target.checked ? jobRows.map((n) => n[JobProps.id]) : []),
        [jobRows]
    );

    const handleCancelJobs = useCallback(
        (event: React.MouseEvent<HTMLElement>) => {
            event.stopPropagation();
            const { id = "", multiple = false } = event.currentTarget?.dataset || {};
            try {
                dispatch(
                    createSendActionNameAction(props.id, module, props.onJobAction, {
                        id: multiple === false ? [id] : JSON.parse(id),
                        action: "cancel",
                        error_id: getUpdateVar(updateJbVars, "error_id"),
                    })
                );
            } catch (e) {
                console.warn("Error parsing ids for cancel.", e);
            }
        },
        [dispatch, module, props.id, props.onJobAction, updateJbVars]
    );

    const handleDeleteJobs = useCallback(
        (event: React.MouseEvent<HTMLElement>) => {
            event.stopPropagation();
            const { id = "", multiple = false } = event.currentTarget?.dataset || {};
            try {
                dispatch(
                    createSendActionNameAction(props.id, module, props.onJobAction, {
                        id: multiple === false ? [id] : JSON.parse(id),
                        action: "delete",
                        error_id: getUpdateVar(updateJbVars, "error_id"),
                    })
                );
            } catch (e) {
                console.warn("Error parsing ids for delete.", e);
            }
        },
        [dispatch, module, props.id, props.onJobAction, updateJbVars]
    );

    const deleteJob = useCallback(
        (event: React.MouseEvent<HTMLElement>) => {
            handleDeleteJobs(event);
            setShowDetails(false);
        },
        [handleDeleteJobs]
    );

    const handleShowDetails = useCallback(
        (event: React.MouseEvent<HTMLElement>) => {
            event.stopPropagation();
            const { id = "" } = event.currentTarget?.dataset || {};
            if (props.onDetails) {
                dispatch(createSendActionNameAction(props.id, module, props.onDetails, id));
            } else {
                const idVar = getUpdateVar(updateJbVars, "detail_id");
                detailId.current = id;
                dispatch(
                    createRequestUpdateAction(
                        id,
                        module,
                        getUpdateVarNames(props.updateVars, "details"),
                        true,
                        idVar ? { [idVar]: id } : undefined
                    )
                );
            }
        },
        [dispatch, module, props.id, props.onDetails, props.updateVars, updateJbVars]
    );

    const closeDetails = useCallback(() => setShowDetails(false), []);

    const allowCancelJobs = useMemo(
        () =>
            !!checked.length &&
            jobRows
                .filter((job) => checked.includes(job[JobProps.id]))
                .every(
                    (job) =>
                        job[JobProps.status] === Status.SUBMITTED ||
                        job[JobProps.status] === Status.BLOCKED ||
                        job[JobProps.status] === Status.PENDING
                ),
        [jobRows, checked]
    );

    const allowDeleteJobs = useMemo(
        () =>
            !!checked.length &&
            jobRows
                .filter((job) => checked.includes(job[JobProps.id]))
                .every(
                    (job) =>
                        job[JobProps.status] === Status.CANCELED ||
                        job[JobProps.status] === Status.FAILED ||
                        job[JobProps.status] === Status.COMPLETED ||
                        job[JobProps.status] === Status.SKIPPED ||
                        job[JobProps.status] === Status.ABANDONED
                ),
        [jobRows, checked]
    );

    const handleFilterOpen = useCallback((event: React.MouseEvent<HTMLButtonElement>) => {
        setAnchorEl(event.currentTarget);
    }, []);

    const handleFilterClose = useCallback(() => {
        setAnchorEl(null);
    }, []);

    useEffect(() => {
        if (props.details && props.details[0] == detailId.current) {
            // show Dialog
            setShowDetails(true);
        }
    }, [props.details]);

    useEffect(() => {
        let filteredJobRows = [...(props.jobs || [])];
        filteredJobRows.length &&
            filters &&
            filters
                .filter((filter) => filter.data && filter.operator)
                .forEach((filter) => {
                    filteredJobRows = filteredJobRows.filter((job) => {
                        let rowColumnValue = "";
                        if (filter.data === JobProps.status) {
                            rowColumnValue = Status[job[JobProps.status]].toLowerCase();
                        } else if (filter.data === JobProps.id) {
                            rowColumnValue = `${job[JobProps.id].toLowerCase()}${job[JobProps.name].toLowerCase()}`;
                        } else if (filter.data === JobProps.submitted_id) {
                            rowColumnValue = `${job[JobProps.submitted_id].toLowerCase()}${job[
                                JobProps.submitted_label
                            ].toLowerCase()}`;
                        } else if (filter.data === JobProps.creation_date) {
                            rowColumnValue = new Date(job[JobProps.creation_date]).toLocaleString();
                        } else if (filter.data < JobLength) {
                            rowColumnValue = job[filter.data].toString().toLowerCase();
                        }
                        const includes = rowColumnValue.includes(filter.value.toLowerCase());
                        return filter.operator === "is" ? includes : !includes;
                    });
                });
        setJobRows(filteredJobRows);
        const jobIds = filteredJobRows.map((j) => j[JobProps.id]);
        setChecked((ids) => ids.filter((id) => jobIds.includes(id)));
    }, [filters, props.jobs]);

    useEffect(() => {
        if (props.value) {
            setSelected(Array.isArray(props.value) ? props.value : [props.value]);
        } else if (props.defaultValue) {
            try {
                const val = JSON.parse(props.defaultValue);
                setSelected(Array.isArray(val) ? val : [val]);
            } catch (e) {
                console.warn("Error parsing jobs default value", e);
            }
        }
    }, [props.value, props.defaultValue]);

    useEffect(() => {
        if (coreChanged?.name) {
            const toRemove = [...coreChanged.stack]
                .map((bc) => {
                    if ((bc as Record<string, unknown>).jobs) {
                        const updateVar = getUpdateVar(props.updateVars, "jobs");
                        updateVar && dispatch(createRequestUpdateAction(id, module, [updateVar], true));
                        return bc;
                    }
                    return undefined;
                })
                .filter((v) => v);
            toRemove.length && dispatch(createUnBroadcastAction(coreChanged.name, ...toRemove));
        }
    }, [coreChanged, props.updateVars, module, dispatch, id]);

    const tableHeightSx = useMemo(() => ({ maxHeight: props.height || "50vh" }), [props.height]);

    return (
        <Box className={className}>
            {showDetails && props.details ? (
                <Dialog open={true} onClose={closeDetails} scroll="paper" fullWidth>
                    <DialogTitle>{props.details[1]}</DialogTitle>
                    <IconButton aria-label="close" onClick={closeDetails} sx={CloseDialogSx}>
                        <CloseIcon />
                    </IconButton>
                    <DialogContent dividers>
                        <JobViewer job={props.details} inDialog={true} updateVars=""></JobViewer>
                    </DialogContent>
                    <DialogActions>
                        <Button variant="outlined" color="primary" onClick={deleteJob} data-id={props.details[0]}>
                            Delete
                        </Button>
                        <Button variant="outlined" color="secondary" onClick={closeDetails} sx={RightButtonSx}>
                            Close
                        </Button>
                    </DialogActions>
                </Dialog>
            ) : null}
            <Paper sx={containerSx}>
                <Toolbar sx={headerToolbarSx}>
                    <Stack direction="row" justifyContent="space-between" width="100%" marginRight={4}>
                        <Tooltip title="Filter">
                            <IconButton onClick={handleFilterOpen}>
                                <FilterList />
                            </IconButton>
                        </Tooltip>
                        {filters && filters.length ? (
                            <Typography component="div">
                                {filters.length} filter{filters.length > 1 ? "s" : ""}
                            </Typography>
                        ) : null}
                        {checked.length ? (
                            <Stack direction="row" alignItems="center">
                                <Typography variant="subtitle1">{checked.length} selected</Typography>
                                {showCancel ? (
                                    <Tooltip title="Cancel Jobs">
                                        <span>
                                            <IconButton
                                                disabled={!allowCancelJobs}
                                                data-id={JSON.stringify(checked)}
                                                data-multiple
                                                onClick={handleCancelJobs}
                                            >
                                                <StopCircleOutlined color={disableColor("inherit", !allowCancelJobs)} />
                                            </IconButton>
                                        </span>
                                    </Tooltip>
                                ) : null}
                                {showDelete ? (
                                    <Tooltip title="Delete Jobs">
                                        <span>
                                            <IconButton
                                                disabled={!allowDeleteJobs}
                                                data-id={JSON.stringify(checked)}
                                                data-multiple
                                                onClick={handleDeleteJobs}
                                            >
                                                <DeleteOutline color={disableColor("primary", !allowDeleteJobs)} />
                                            </IconButton>
                                        </span>
                                    </Tooltip>
                                ) : null}
                            </Stack>
                        ) : null}
                    </Stack>
                    <Filter
                        open={!!anchorEl}
                        anchorEl={anchorEl}
                        handleFilterClose={handleFilterClose}
                        handleApplyFilter={setFilters}
                        columns={jobSelectorColumns}
                    />
                </Toolbar>
                <TableContainer sx={tableHeightSx}>
                    <Table sx={tableWidthSx} aria-labelledby="tableTitle" size="medium">
                        <JobSelectedTableHead
                            jobs={jobRows.length}
                            selected={checked.length}
                            handleSelectAllClick={handleCheckAllClick}
                            columns={jobSelectorColumns}
                        />
                        <TableBody>
                            {jobRows.map((row) => (
                                <JobSelectedTableRow
                                    handleSelection={handleSelection}
                                    handleCheckboxClick={handleClick}
                                    row={row}
                                    isSelected={selected.includes(row[JobProps.id])}
                                    isItemSelected={checked.includes(row[JobProps.id])}
                                    key={row[JobProps.id]}
                                    handleDeleteJobs={handleDeleteJobs}
                                    handleCancelJobs={handleCancelJobs}
                                    handleShowDetails={props.onDetails === false ? false : handleShowDetails}
                                    showSubmissionId={showSubmissionId}
                                    showId={showId}
                                    showSubmittedLabel={showSubmittedLabel}
                                    showSubmittedId={showSubmittedId}
                                    showDate={showDate}
                                    showCancel={showCancel}
                                    showDelete={showDelete}
                                />
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>
            {props.children}
        </Box>
    );
};

export default JobSelector;
