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

import React, { useEffect, useState, useCallback } from "react";
import Box from "@mui/material/Box";
import { DeleteOutline, StopCircleOutlined } from "@mui/icons-material";
import {
    Checkbox,
    Chip,
    IconButton,
    ListItemText,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TableSortLabel,
    Toolbar,
    Tooltip,
    Typography,
} from "@mui/material";

import { FilterList } from "@mui/icons-material";

interface JobSelectorProps {
    updateVarName?: string;
    coreChanged?: Record<string, unknown>;
    updateVars?: string;
    error?: string;
    jobs?: any[];
    onSelect?: string;
}

export enum JobStatus {
    COMPLETED = "Completed",
    SUBMITTED = "Submitted",
    BLOCKED = "Blocked",
    PENDING = "Pending",
    RUNNING = "Running",
    CANCELED = "Canceled",
    FAILED = "Failed",
    SKIPPED = "Skipped",
    ABANDONED = "Abandoned",
}

const ChipStatus = ({ status, label }: { status: JobStatus; label: string }) => {
    let colorFill: "warning" | "default" | "success" | "error" = "warning";
    if (status === JobStatus.COMPLETED || status === JobStatus.SKIPPED) {
        colorFill = "success";
    } else if (status === JobStatus.FAILED) {
        colorFill = "error";
    } else if (status === JobStatus.CANCELED || status === JobStatus.ABANDONED) {
        colorFill = "default";
    }

    const variant = status === JobStatus.FAILED || status === JobStatus.RUNNING ? "filled" : "outlined";

    return <Chip label={label} variant={variant} color={colorFill} />;
};

const JobSelectorColumns = [
    {
        id: "jobId",
        primaryLabel: "Job",
        secondaryLabel: "ID",
    },
    {
        id: "submitID",
        primaryLabel: "Submit ID",
    },
    {
        id: "submitEntity",
        primaryLabel: "Submitted entity",
        secondaryLabel: "ID",
    },
    {
        id: "createdDt",
        primaryLabel: "Creation date",
    },
    {
        id: "status",
        primaryLabel: "Status",
    },
];

interface JobSelectedTableHeadProps {
    selectAllTrue: boolean;
    order?: "asc" | "desc";
    orderBy?: string;
    handleSelectAllClick?: (event: React.ChangeEvent<HTMLInputElement>) => void;
    handleRequestSort: (id: string, columnIndex: number) => void;
}
function JobSelectedTableHead({
    selectAllTrue,
    order,
    orderBy,
    handleSelectAllClick,
    handleRequestSort,
}: JobSelectedTableHeadProps) {
    return (
        <TableHead>
            <TableRow>
                <TableCell padding="checkbox">
                    <Checkbox color="primary" checked={selectAllTrue} onChange={handleSelectAllClick} />
                </TableCell>
                {JobSelectorColumns.map((item, index) => {
                    return (
                        <TableCell sortDirection={orderBy === item.id ? order : false} key={index}>
                            <TableSortLabel
                                direction={orderBy === item.id ? order : "desc"}
                                IconComponent={FilterList}
                                onClick={() => handleRequestSort(item.id, index)}
                            >
                                {item.secondaryLabel ? (
                                    <ListItemText primary={item.primaryLabel} secondary={item.secondaryLabel} />
                                ) : (
                                    item.primaryLabel
                                )}
                            </TableSortLabel>
                        </TableCell>
                    );
                })}
                <TableCell>Actions</TableCell>
            </TableRow>
        </TableHead>
    );
}

interface JobSelectedTableRowProps {
    row: any[];
    isItemSelected: boolean;
    handleCheckboxClick: (event: React.MouseEvent<unknown>, name: string) => void;
    handleStopJob: (id: string[]) => void;
    handleDeleteJob: (id: string[]) => void;
}
function JobSelectedTableRow({
    row,
    isItemSelected,
    handleCheckboxClick,
    handleStopJob,
    handleDeleteJob,
}: JobSelectedTableRowProps) {
    const [id, submitID, entity, createdDt, status] = row;
    return (
        <TableRow hover role="checkbox" tabIndex={-1} key={id}>
            <TableCell padding="checkbox">
                <Checkbox
                    color="primary"
                    checked={isItemSelected}
                    onClick={(event) => handleCheckboxClick(event, id)}
                />
            </TableCell>
            <TableCell component="th" id={id} scope="row" padding="none">
                <ListItemText primary="Preprocess" secondary={id} />
            </TableCell>
            <TableCell>{submitID}</TableCell>
            <TableCell>
                <ListItemText primary="Pipeline alpha" secondary={entity} />
            </TableCell>
            <TableCell>{createdDt}</TableCell>
            <TableCell>
                <ChipStatus label={status} status={status} />
            </TableCell>
            <TableCell>
                {status === JobStatus.RUNNING ? null : status === JobStatus.BLOCKED ||
                  status === JobStatus.PENDING ||
                  status === JobStatus.SUBMITTED ? (
                    <IconButton onClick={() => handleStopJob([id])}>
                        <StopCircleOutlined />
                    </IconButton>
                ) : (
                    <IconButton onClick={() => handleDeleteJob([id])}>
                        <DeleteOutline color="primary" />
                    </IconButton>
                )}
            </TableCell>
        </TableRow>
    );
}

const JobSelector = (props: JobSelectorProps) => {
    const { jobs } = props;

    const [order, setOrder] = React.useState<"asc" | "desc">("asc");
    const [orderBy, setOrderBy] = useState<string>("");
    const [selected, setSelected] = useState<readonly string[]>([]);
    const [jobRows, setJobRows] = useState<any[]>(jobs);

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
        <Box>
            <Paper sx={containerSx}>
                <Toolbar sx={headerToolbarSx}>
                    {selected.length > 0 ? (
                        <Typography sx={selectedSx} color="inherit" variant="subtitle1" component="div">
                            {selected.length} selected
                        </Typography>
                    ) : null}
                    {selected.length > 0 ? (
                        <>
                            <Tooltip title="Stop">
                                <IconButton onClick={() => handleDeleteJob(selected as string[])}>
                                    <StopCircleOutlined />
                                </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete">
                                <IconButton onClick={() => handleDeleteJob(selected as string[])}>
                                    <DeleteOutline color="primary" />
                                </IconButton>
                            </Tooltip>
                        </>
                    ) : null}
                </Toolbar>
                <TableContainer>
                    <Table sx={{ minWidth: 750 }} aria-labelledby="tableTitle" size="medium">
                        <JobSelectedTableHead
                            selectAllTrue={jobs?.length === selected?.length}
                            order={order}
                            orderBy={orderBy}
                            handleSelectAllClick={handleSelectAllClick}
                            handleRequestSort={handleRequestSort}
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
                                              handleDeleteJob={handleDeleteJob}
                                              handleStopJob={handleStopJob}
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
