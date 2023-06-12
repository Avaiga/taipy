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
import { ChevronRight, ExpandMore } from "@mui/icons-material";
import TreeItem from "@mui/lab/TreeItem";
import TreeView from "@mui/lab/TreeView";
import { useDispatch, useModule, createSendActionNameAction } from "taipy-gui";
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
    TablePagination,
    TableRow,
    TableSortLabel,
    Toolbar,
    Tooltip,
    Typography,
    alpha,
} from "@mui/material";

import { FilterList } from "@mui/icons-material";

interface JobSelectorProps {
    id?: string;
    updateVarName?: string;
    coreChanged?: Record<string, unknown>;
    updateVars?: string;
    error?: string;
    jobs?: any[];
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

const JobSelector = (props: JobSelectorProps) => {
    const {
        id = "",
        jobs = [
            [
                "JOB_5643_5764_6876_56621",
                "SUBMIT_5643_5764_6876_5662",
                "SCENARIO_5643_5764_6876_5662",
                "2023/02/05, 14:43:43",
                "Completed",
            ],
            [
                "JOB_5643_5764_6876_56622",
                "SUBMIT_5643_5764_6876_5662",
                "SCENARIO_5643_5764_6876_5662",
                "2023/02/05, 14:43:43",
                "Submitted",
            ],
            [
                "JOB_5643_5764_6876_56623",
                "SUBMIT_5643_5764_6876_5662",
                "SCENARIO_5643_5764_6876_5662",
                "2023/02/05, 14:43:43",
                "Blocked",
            ],
            [
                "JOB_5643_5764_6876_56624",
                "SUBMIT_5643_5764_6876_5662",
                "SCENARIO_5643_5764_6876_5662",
                "2023/02/05, 14:43:43",
                "Pending",
            ],
            [
                "JOB_5643_5764_6876_56625",
                "SUBMIT_5643_5764_6876_5662",
                "SCENARIO_5643_5764_6876_5662",
                "2023/02/05, 14:43:43",
                "Running",
            ],
            [
                "JOB_5643_5764_6876_56626",
                "SUBMIT_5643_5764_6876_5662",
                "SCENARIO_5643_5764_6876_5662",
                "2023/02/05, 14:43:43",
                "Canceled",
            ],
            [
                "JOB_5643_5764_6876_56627",
                "SUBMIT_5643_5764_6876_5662",
                "SCENARIO_5643_5764_6876_5662",
                "2023/02/05, 14:43:43",
                "Failed",
            ],
            [
                "JOB_5643_5764_6876_56628",
                "SUBMIT_5643_5764_6876_5662",
                "SCENARIO_5643_5764_6876_5662",
                "2023/02/05, 14:43:43",
                "Skipped",
            ],
            [
                "JOB_5643_5764_6876_56629",
                "SUBMIT_5643_5764_6876_5662",
                "SCENARIO_5643_5764_6876_5662",
                "2023/02/05, 14:43:43",
                "Abandoned",
            ],
        ],
    } = props;

    const dispatch = useDispatch();
    const module = useModule();

    const [order, setOrder] = React.useState<"asc" | "desc">("asc");
    const [orderBy, setOrderBy] = useState<string>("calories");
    const [selected, setSelected] = useState<readonly string[]>([]);

    const isSelected = (name: string) => selected.indexOf(name) !== -1;

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

    const handleSelectAllClick = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.checked) {
            const newSelected = jobs.map((n) => n[0]);
            setSelected(newSelected);
            return;
        }
        setSelected([]);
    };

    const handleRequestSort = (property: string) => {
        const isAsc = orderBy === property && order === "asc";
        setOrder(isAsc ? "desc" : "asc");
        setOrderBy(property);
    };

    return (
        <Box>
            <Paper sx={{ width: "100%", mb: 2 }}>
                <Toolbar
                    sx={{
                        pl: { sm: 2 },
                        pr: { xs: 1, sm: 1 },
                        ...(selected.length > 0 && {
                            bgcolor: (theme) =>
                                alpha(theme.palette.primary.main, theme.palette.action.activatedOpacity),
                        }),
                    }}
                >
                    {selected.length > 0 ? (
                        <Typography sx={{ flex: "1 1 100%" }} color="inherit" variant="subtitle1" component="div">
                            {selected.length} selected
                        </Typography>
                    ) : null}
                    {selected.length > 0 ? (
                        <>
                            <Tooltip title="Stop">
                                <IconButton>
                                    <StopCircleOutlined />
                                </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete">
                                <IconButton>
                                    <DeleteOutline />
                                </IconButton>
                            </Tooltip>
                        </>
                    ) : null}
                </Toolbar>
                <TableContainer>
                    <Table sx={{ minWidth: 750 }} aria-labelledby="tableTitle" size="medium">
                        <TableHead>
                            <TableRow>
                                <TableCell padding="checkbox">
                                    <Checkbox
                                        color="primary"
                                        checked={jobs?.length === selected?.length}
                                        onChange={handleSelectAllClick}
                                    />
                                </TableCell>
                                <TableCell sortDirection={orderBy === "jobId" ? order : false}>
                                    <TableSortLabel
                                        direction={orderBy === "jobId" ? order : "desc"}
                                        IconComponent={FilterList}
                                        onClick={() => handleRequestSort("jobId")}
                                    >
                                        <ListItemText primary="Job" secondary="ID" />
                                    </TableSortLabel>
                                </TableCell>
                                <TableCell sortDirection={orderBy === "submitID" ? order : false}>
                                    <TableSortLabel
                                        IconComponent={FilterList}
                                        direction={orderBy === "submitID" ? order : "desc"}
                                        onClick={() => handleRequestSort("submitID")}
                                    >
                                        Submit ID
                                    </TableSortLabel>
                                </TableCell>
                                <TableCell sortDirection={orderBy === "submitEntity" ? order : false}>
                                    <TableSortLabel
                                        IconComponent={FilterList}
                                        direction={orderBy === "submitEntity" ? order : "desc"}
                                        onClick={() => handleRequestSort("submitEntity")}
                                    >
                                        <ListItemText primary="Submitted entity" secondary="ID" />
                                    </TableSortLabel>
                                </TableCell>
                                <TableCell sortDirection={orderBy === "createdDt" ? order : false}>
                                    <TableSortLabel
                                        IconComponent={FilterList}
                                        direction={orderBy === "createdDt" ? order : "desc"}
                                        onClick={() => handleRequestSort("createdDt")}
                                    >
                                        Creation date
                                    </TableSortLabel>
                                </TableCell>
                                <TableCell sortDirection={orderBy === "status" ? order : false}>
                                    <TableSortLabel
                                        IconComponent={FilterList}
                                        direction={orderBy === "status" ? order : "desc"}
                                        onClick={() => handleRequestSort("status")}
                                    >
                                        Status
                                    </TableSortLabel>
                                </TableCell>
                                <TableCell>Actions</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {jobs
                                ? jobs.map((row, index) => {
                                      const [id, submitID, entity, createdDt, status] = row;
                                      const isItemSelected = isSelected(id);

                                      return (
                                          <TableRow hover role="checkbox" tabIndex={-1} key={id}>
                                              <TableCell padding="checkbox">
                                                  <Checkbox
                                                      color="primary"
                                                      checked={isItemSelected}
                                                      onClick={(event) => handleClick(event, id)}
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
                                                      <StopCircleOutlined />
                                                  ) : (
                                                      <DeleteOutline color="primary" />
                                                  )}
                                              </TableCell>
                                          </TableRow>
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
