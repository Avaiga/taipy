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

import React, { useEffect, useState, useCallback, useMemo } from "react";
import Box from "@mui/material/Box";
import { DeleteOutline, StopCircleOutlined, Add } from "@mui/icons-material";
import { DeleteOutline, StopCircleOutlined } from "@mui/icons-material";
import {
    Button,
    Checkbox,
    Chip,
    FormControl,
    Grid,
    IconButton,
    InputLabel,
    ListItemText,
    MenuItem,
    Paper,
    Popover,
    Select,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Toolbar,
    Tooltip,
    Typography,
} from "@mui/material";

import { FilterList } from "@mui/icons-material";
import { Job, JobStatus, Jobs } from "./utils/types";
import {
    createRequestUpdateAction,
    createSendActionNameAction,
    getUpdateVar,
    useDispatch,
    useDispatchRequestUpdateOnFirstRender,
    useDynamicProperty,
    useModule,
} from "taipy-gui";
import { useFormik } from "formik";
import { useClassNames } from "./utils";

interface JobSelectorProps {
    updateVarName?: string;
    coreChanged?: Record<string, unknown>;
    error?: string;
    jobs: Jobs;
    onSelect?: string;
    updateVars: string;
    id?: string;
    className?: string;
    dynamicClassName?: string;
    height: string;
    displayJobId?: boolean;
    defaultDisplayJobId: boolean;
    displayEntityLabel?: boolean;
    defaultDisplayEntityLabel: boolean;
    displayEntityId?: boolean;
    defaultDisplayEntityId: boolean;
    displaySubmitId?: boolean;
    defaultDisplaySubmitId: boolean;
    displayDate?: boolean;
    defaultDisplayDate: boolean;
    onJobAction: string;
}

const selectedSx = { flex: "1 1 100%" };
const containerSx = { width: "100%", mb: 2 };
const selectSx = {
    height: 50,
};
const containerPopupSx = { width: "619px" };

const ChipStatus = ({ status }: { status: number }) => {
    const statusText = Object.keys(JobStatus)[Object.values(JobStatus).indexOf(status)];
    let colorFill: "warning" | "default" | "success" | "error" = "warning";

    if (status === JobStatus.COMPLETED || status === JobStatus.SKIPPED) {
        colorFill = "success";
    } else if (status === JobStatus.FAILED) {
        colorFill = "error";
    } else if (status === JobStatus.CANCELED || status === JobStatus.ABANDONED) {
        colorFill = "default";
    }

    const variant = status === JobStatus.FAILED || status === JobStatus.RUNNING ? "filled" : "outlined";

    return <Chip label={statusText} variant={variant} color={colorFill} />;
};

export type JobSelectorColumns = {
    id: string;
    primaryLabel: string;
    showPrimaryLabel?: boolean;
    secondaryLabel?: string;
    showSecondayLabel?: boolean;
    columnIndex: number;
};

export type FilterData = {
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
    const form = useFormik({
        initialValues: {
            filters: [],
            newData: null,
            newOperator: "is",
            newValue: "",
        },
        onSubmit: () => {
            applyFilter();
        },
    });

    const removeFilter = useCallback(
        (index: number) => {
            const newFilters = [...form.values.filters];
            newFilters && newFilters.splice(index, 1);
            form.setFieldValue("filters", newFilters);
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
        const filters = [...form.values.filters];
        handleApplyFilter(filters);
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
            anchorOrigin={{
                vertical: "bottom",
                horizontal: "left",
            }}
        >
            <form onSubmit={form.handleSubmit}>
                <Grid container p={3} sx={containerPopupSx}>
                    {form && form.values.filters && form.values.filters.length > 0
                        ? form.values.filters.map((filter, index) => {
                              return (
                                  <Grid item xs={12} container spacing={2} mb={1} key={index}>
                                      <Grid item xs={3}>
                                          <FormControl fullWidth>
                                              <InputLabel id="data">Data</InputLabel>
                                              <Select
                                                  labelId="data"
                                                  sx={selectSx}
                                                  label="Job Label"
                                                  {...form.getFieldProps(`filters.${index}.data`)}
                                              >
                                                  {columns
                                                      .filter((i) => i.showPrimaryLabel || i.showSecondayLabel)
                                                      .map((item, index) => {
                                                          return (
                                                              <MenuItem key={index} value={item.columnIndex}>
                                                                  {item.primaryLabel}
                                                              </MenuItem>
                                                          );
                                                      })}
                                              </Select>
                                          </FormControl>
                                      </Grid>
                                      <Grid item xs={3}>
                                          <FormControl fullWidth>
                                              <InputLabel id="operator">Operator</InputLabel>
                                              <Select
                                                  labelId="operator"
                                                  sx={selectSx}
                                                  label="Operator"
                                                  {...form.getFieldProps(`filters.${index}.operator`)}
                                              >
                                                  <MenuItem value={"is"}>is</MenuItem>
                                                  <MenuItem value={"isnot"}>is not</MenuItem>
                                              </Select>
                                          </FormControl>
                                      </Grid>
                                      <Grid item xs={5}>
                                          <TextField
                                              label="Value"
                                              variant="outlined"
                                              {...form.getFieldProps(`filters.${index}.value`)}
                                          />
                                      </Grid>
                                      <Grid item xs={1}>
                                          <IconButton onClick={() => removeFilter(index)}>
                                              <DeleteOutline />
                                          </IconButton>
                                      </Grid>
                                  </Grid>
                              );
                          })
                        : null}
                    <Grid item xs={12} container spacing={2} justifyContent="space-between">
                        <Grid item xs={3}>
                            <FormControl fullWidth>
                                <InputLabel id="data-new">Data</InputLabel>
                                <Select
                                    labelId="data-new"
                                    sx={selectSx}
                                    label="Job Label"
                                    {...form.getFieldProps(`newData`)}
                                >
                                    {columns
                                        .filter((i) => i.showPrimaryLabel || i.showSecondayLabel)
                                        .map((item, index) => {
                                            return (
                                                <MenuItem key={index} value={item.columnIndex}>
                                                    {item.primaryLabel}
                                                </MenuItem>
                                            );
                                        })}
                                </Select>
                            </FormControl>
                        </Grid>
                        <Grid item xs={3}>
                            <FormControl fullWidth>
                                <InputLabel id="operator-new">Operator</InputLabel>
                                <Select
                                    labelId="operator-new"
                                    sx={selectSx}
                                    label="Operator"
                                    {...form.getFieldProps(`newOperator`)}
                                >
                                    <MenuItem value={"is"}>is</MenuItem>
                                    <MenuItem value={"isnot"}>is not</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                        <Grid item xs={5}>
                            <TextField label="Value" variant="outlined" {...form.getFieldProps(`newValue`)} />
                        </Grid>
                        <Grid item xs={1}>
                            <IconButton onClick={addFilter}>
                                <Add color="primary" />
                            </IconButton>
                        </Grid>
                    </Grid>
                    <Grid item xs={12} container justifyContent="space-between" mt={2}>
                        <Button variant="outlined" color="inherit" onClick={removeAllFilter}>
                            REMOVE ALL FILTERS
                        </Button>
                        <Button variant="contained" type="submit">
                            APPLY FILTER
                        </Button>
                    </Grid>
                </Grid>
            </form>
        </Popover>
    );
};

interface JobSelectedTableHeadProps {
    selectAllTrue: boolean;
    handleSelectAllClick?: (event: React.ChangeEvent<HTMLInputElement>) => void;
    columns: JobSelectorColumns[];
}
function JobSelectedTableHead({ selectAllTrue, handleSelectAllClick, columns }: JobSelectedTableHeadProps) {
    return (
        <TableHead>
            <TableRow>
                <TableCell padding="checkbox">
                    <Checkbox color="primary" checked={selectAllTrue} onChange={handleSelectAllClick} />
                </TableCell>
                {columns
                    .filter((i) => i.showPrimaryLabel || i.showSecondayLabel)
                    .map((item, index) => {
                        return (
                            <TableCell key={index}>
                                {item.secondaryLabel ? (
                                    <ListItemText primary={item.primaryLabel} secondary={item.secondaryLabel} />
                                ) : (
                                    item.primaryLabel
                                )}
                            </TableCell>
                        );
                    })}
                <TableCell>Actions</TableCell>
            </TableRow>
        </TableHead>
    );
}

interface JobSelectedTableRowProps {
    row: Job;
    isItemSelected: boolean;
    handleCheckboxClick: (event: React.MouseEvent<HTMLElement>, name: string) => void;
    handleCancelJobs: (id: string[]) => void;
    handleDeleteJobs: (id: string[]) => void;
    displayJobId?: boolean;
    displayEntityLabel?: boolean;
    displayEntityId?: boolean;
    displaySubmitId?: boolean;
    displayDate?: boolean;
}
function JobSelectedTableRow({
    row,
    isItemSelected,
    handleCheckboxClick,
    handleCancelJobs,
    handleDeleteJobs,
    displayJobId,
    displayEntityLabel,
    displayEntityId,
    displaySubmitId,
    displayDate,
}: JobSelectedTableRowProps) {
    const [id, jobName, entityId, entityName, submitId, creationDate, status] = row;

    const doDeleteJob = useCallback(
        (id: string[]) => {
            handleDeleteJobs && handleDeleteJobs(id);
        },
        [handleDeleteJobs]
    );
    const doCancelJob = useCallback(
        (id: string[]) => {
            handleCancelJobs && handleCancelJobs(id);
        },
        [handleCancelJobs]
    );
    const doCheckboxClick = useCallback(
        (event: React.MouseEvent<HTMLElement>, name: string) => {
            handleCheckboxClick && handleCheckboxClick(event, name);
        },
        [handleCheckboxClick]
    );

    return (
        <TableRow hover role="checkbox" tabIndex={-1} key={id}>
            <TableCell padding="checkbox">
                <Checkbox color="primary" checked={isItemSelected} onClick={(event) => doCheckboxClick(event, id)} />
            </TableCell>
            {displayJobId ? (
                <TableCell component="th" id={id} scope="row" padding="none">
                    <ListItemText primary={jobName} secondary={id} />
                </TableCell>
            ) : null}
            {displaySubmitId ? <TableCell>{submitId}</TableCell> : null}
            {displayEntityLabel || displayEntityId ? (
                <TableCell>
                    {!displayEntityLabel && displayEntityId ? (
                        entityId
                    ) : !displayEntityId && displayEntityLabel ? (
                        entityName
                    ) : (
                        <ListItemText primary={entityName} secondary={entityId} />
                    )}
                </TableCell>
            ) : null}
            {displayDate ? <TableCell>{creationDate}</TableCell> : null}
            <TableCell>
                <ChipStatus status={status} />
            </TableCell>
            <TableCell>
                {status === JobStatus.RUNNING ? null : status === JobStatus.BLOCKED ||
                  status === JobStatus.PENDING ||
                  status === JobStatus.SUBMITTED ? (
                    <IconButton onClick={() => doCancelJob([id])}>
                        <StopCircleOutlined />
                    </IconButton>
                ) : (
                    <IconButton onClick={() => doDeleteJob([id])}>
                        <DeleteOutline color="primary" />
                    </IconButton>
                )}
            </TableCell>
        </TableRow>
    );
}

const JobSelector = (props: JobSelectorProps) => {
    const { id = "", jobs = [] } = props;
    const [selected, setSelected] = useState<string[]>([]);
    const [jobRows, setJobRows] = useState<Jobs>(jobs);
    const [filters, setFilters] = useState<FilterData[]>();
    const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(null);

    const isSelected = (name: string) => selected.indexOf(name) !== -1;

    const dispatch = useDispatch();
    const module = useModule();

    const className = useClassNames(props.className, props.dynamicClassName);

    useDispatchRequestUpdateOnFirstRender(dispatch, id, module, props.updateVars);

    const displayJobId = useDynamicProperty(props.displayJobId, props.defaultDisplayJobId, true);
    const displayEntityLabel = useDynamicProperty(props.displayEntityLabel, props.defaultDisplayEntityLabel, true);
    const displayEntityId = useDynamicProperty(props.displayEntityId, props.defaultDisplayEntityId, true);
    const displaySubmitId = useDynamicProperty(props.displaySubmitId, props.defaultDisplaySubmitId, true);
    const displayDate = useDynamicProperty(props.displayDate, props.defaultDisplayDate, true);

    const headerToolbarSx = useMemo(
        () => ({
            pl: { sm: 2 },
            pr: { xs: 1, sm: 1 },
            ...(selected.length > 0 && {
                bgcolor: "rgba(0, 0, 0, 0.05)",
            }),
        }),
        [selected]
    );

    const jobSelectorColumns: JobSelectorColumns[] = useMemo(
        () => [
            {
                id: "jobId",
                primaryLabel: "Job",
                showPrimaryLabel: displayJobId,
                secondaryLabel: "ID",
                showSecondayLabel: displayJobId,
                columnIndex: 0,
            },
            {
                id: "submitID",
                primaryLabel: "Submit ID",
                columnIndex: 4,
                showPrimaryLabel: displaySubmitId,
                showSecondayLabel: displaySubmitId,
            },
            {
                id: "submitEntity",
                primaryLabel: "Submitted entity",
                secondaryLabel: "ID",
                columnIndex: 3,
                showPrimaryLabel: displayEntityLabel,
                showSecondayLabel: displayEntityId,
            },
            {
                id: "createdDt",
                primaryLabel: "Creation date",
                columnIndex: 5,
                showPrimaryLabel: displayDate,
                showSecondayLabel: displayDate,
            },
            {
                id: "status",
                primaryLabel: "Status",
                columnIndex: 6,
                showPrimaryLabel: true,
                showSecondayLabel: true,
            },
        ],
        [displayDate, displayEntityId, displayEntityLabel, displayJobId, displaySubmitId]
    );

    const handleClick = useCallback(
        (event: React.MouseEvent<HTMLElement>, name: string) => {
            const selectedIndex = selected.indexOf(name);
            let newSelected: string[] = [];

            if (selectedIndex === -1) {
                newSelected = newSelected.concat(selected, name);
            } else if (selectedIndex === 0) {
                newSelected = newSelected.concat(selected.slice(1));
            } else if (selectedIndex === selected.length - 1) {
                newSelected = newSelected.concat(selected.slice(0, -1));
            } else if (selectedIndex > 0) {
                newSelected = newSelected.concat(selected.slice(0, selectedIndex), selected.slice(selectedIndex + 1));
            }
            setSelected([...newSelected]);
        },
        [selected]
    );

    const handleSelectAllClick = useCallback(
        (event: React.ChangeEvent<HTMLInputElement>) => {
            if (event.target.checked) {
                const newSelected = jobRows?.map((n) => n[0]);
                setSelected(newSelected || []);
                return;
            }
            setSelected([]);
        },
        [jobRows]
    );

    const handleCancelJobs = useCallback(
        (id: string[]) => {
            dispatch(createSendActionNameAction(props.id, module, props.onJobAction, id));
        },
        [dispatch, module, props.id, props.onJobAction]
    );
    const handleDeleteJobs = useCallback(
        (id: string[]) => {
            dispatch(createSendActionNameAction(props.id, module, props.onJobAction, id));
        },
        [dispatch, module, props.id, props.onJobAction]
    );

    const selectedAllowedCancelJobs = useMemo(
        () =>
            jobRows?.filter(
                (job) =>
                    selected.includes(job[0]) &&
                    (job[6] === JobStatus.SUBMITTED || job[6] === JobStatus.BLOCKED || job[6] === JobStatus.PENDING)
            ),
        [jobRows, selected]
    );

    const selectedAllowedDeleteJobs = useMemo(
        () =>
            jobRows?.filter(
                (job) =>
                    selected.includes(job[0]) &&
                    (job[6] === JobStatus.CANCELED ||
                        job[6] === JobStatus.FAILED ||
                        job[6] === JobStatus.SKIPPED ||
                        job[6] === JobStatus.ABANDONED)
            ),
        [jobRows, selected]
    );

    const handleApplyFilters = useCallback((filters: FilterData[]) => {
        setFilters(filters);
    }, []);

    const handleFilterOpen = useCallback((event: React.MouseEvent<HTMLButtonElement>) => {
        setAnchorEl(event.currentTarget);
    }, []);

    const handleFilterClose = useCallback(() => {
        setAnchorEl(null);
    }, []);

    useEffect(() => {
        if (filters) {
            let filteredJobRows = jobs ? [...jobs] : [];
            filters.forEach((filter) => {
                filteredJobRows = filteredJobRows?.filter((job) => {
                    let rowColumnValue = "";
                    if (filter.data === 6) {
                        rowColumnValue =
                            Object.keys(JobStatus)[Object.values(JobStatus).indexOf(job[6])]?.toLowerCase() || "";
                    } else if (filter.data === 0) {
                        rowColumnValue = `${job[0]?.toString()?.toLowerCase() || ""}${
                            job[1]?.toString()?.toLowerCase() || ""
                        }`;
                    } else if (filter.data === 3) {
                        rowColumnValue = `${job[2]?.toString()?.toLowerCase() || ""}${
                            job[3]?.toString()?.toLowerCase() || ""
                        }`;
                    } else {
                        rowColumnValue = job[filter.data]?.toString()?.toLowerCase() || "";
                    }
                    const includes = rowColumnValue.includes(filter.value.toLowerCase());
                    return filter.operator === "is" ? includes : !includes;
                });
            });
            setJobRows(filteredJobRows);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [filters]);

    useEffect(() => {
        setJobRows(jobs);
    }, [jobs]);

    useEffect(() => {
        if (props.coreChanged?.jobs) {
            const updateVar = getUpdateVar(props.updateVars, "jobs");
            updateVar && dispatch(createRequestUpdateAction(id, module, [updateVar], true));
        }
    }, [props.coreChanged, props.updateVars, module, dispatch, id]);

    const open = Boolean(anchorEl);

    const tableHeightSx = useMemo(() => ({ maxHeight: props.height || "50vh" }), [props.height]);

    const isSelected = (name: string) => selected.indexOf(name) !== -1;

    const headerToolbarSx = {
        pl: { sm: 2 },
        pr: { xs: 1, sm: 1 },
        ...(selected.length > 0 && {
            bgcolor: "rgba(0, 0, 0, 0.05)",
        }),
    };
    const selectedSx = { flex: "1 1 100%" };
    const containerSx = { width: "100%", mb: 2 };

    const handleClick = (event: React.MouseEvent<unknown>, name: string) => {
        const selectedIndex = selected.indexOf(name);
        let newSelected: readonly string[] = [];

        if (selectedIndex === -1) {
            newSelected = newSelected.concat(selected, name);
        } else if (selectedIndex === 0) {
            newSelected = newSelected.concat(selected.slice(1));
        } else if (selectedIndex === selected.length - 1) {
            newSelected = newSelected.concat(selected.slice(0, -1));
        } else if (selectedIndex > 0) {
            newSelected = newSelected.concat(selected.slice(0, selectedIndex), selected.slice(selectedIndex + 1));
        }
        setSelected(newSelected);
    };

    const handleSelectAllClick = useCallback(
        (event: React.ChangeEvent<HTMLInputElement>) => {
            if (event.target.checked) {
                const newSelected = jobs.map((n) => n[0]);
                setSelected(newSelected);
                return;
            }
            setSelected([]);
        },
        [jobs]
    );

    const handleRequestSort = (property: string, columnIndex: number) => {
        const isAsc = orderBy === property && order === "asc";
        setOrder(isAsc ? "desc" : "asc");
        setOrderBy(property);

        const sortedJobs = jobs.sort((a, b) => {
            return isAsc ? a[columnIndex].localeCompare(b[columnIndex]) : b[columnIndex].localeCompare(a[columnIndex]);
        });
        setJobRows(sortedJobs);
    };

    const handleDeleteJob = useCallback((id: string[]) => {
        //TODO: delete job
    }, []);
    const handleStopJob = useCallback((id: string[]) => {
        //TODO: stop job
    }, []);

    return (
        <Box className={className}>
            <Paper sx={containerSx}>
                <Toolbar sx={headerToolbarSx}>
                    <Tooltip title="Filter">
                        <IconButton onClick={handleFilterOpen}>
                            <FilterList />
                        </IconButton>
                    </Tooltip>
                    {selected.length > 0 ? (
                        <Typography sx={selectedSx} color="inherit" variant="subtitle1" component="div">
                            {selected.length} selected
                        </Typography>
                    ) : null}
                    {selected.length > 0 ? (
                        <>
                            <Tooltip title="Stop">
                                <IconButton
                                    disabled={!selectedAllowedCancelJobs || selectedAllowedCancelJobs.length == 0}
                                    onClick={() => handleCancelJobs(selected as string[])}
                                >
                                    <StopCircleOutlined />
                                </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete">
                                <IconButton
                                    disabled={!selectedAllowedDeleteJobs || selectedAllowedDeleteJobs.length == 0}
                                    onClick={() => handleDeleteJobs(selected as string[])}
                                >
                                    <DeleteOutline
                                        color={
                                            !selectedAllowedDeleteJobs || selectedAllowedDeleteJobs.length == 0
                                                ? "disabled"
                                                : "primary"
                                        }
                                    />
                                </IconButton>
                            </Tooltip>
                        </>
                    ) : null}

                    <Filter
                        open={open}
                        anchorEl={anchorEl}
                        handleFilterClose={handleFilterClose}
                        handleApplyFilter={handleApplyFilters}
                        columns={jobSelectorColumns}
                    />
                </Toolbar>
                <TableContainer sx={tableHeightSx}>
                    <Table sx={{ minWidth: 750 }} aria-labelledby="tableTitle" size="medium">
                        <JobSelectedTableHead
                            selectAllTrue={jobRows?.length === selected?.length}
                            handleSelectAllClick={handleSelectAllClick}
                            columns={jobSelectorColumns}
                        />
                        <TableBody>
                            {jobRows
                                ? jobRows.map((row, index) => {
                                      const isItemSelected = isSelected(row[0]);

                                      return (
                                          <JobSelectedTableRow
                                              handleCheckboxClick={handleClick}
                                              row={row}
                                              isItemSelected={isItemSelected}
                                              key={index}
                                              handleDeleteJobs={handleDeleteJobs}
                                              handleCancelJobs={handleCancelJobs}
                                              displaySubmitId={displaySubmitId}
                                              displayJobId={displayJobId}
                                              displayEntityLabel={displayEntityLabel}
                                              displayEntityId={displayEntityId}
                                              displayDate={displayDate}
                                          />
                                      );
                                  })
                                : null}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>
        </Box>
    );
};

export default JobSelector;
