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

interface JobSelectorProps {
    id?: string;
    updateVarName?: string;
    coreChanged?: Record<string, unknown>;
    updateVars?: string;
    onDataNodeSelect?: string;
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
                "JOB_5643_5764_6876_5662",
                "SUBMIT_5643_5764_6876_5662",
                "SCENARIO_5643_5764_6876_5662",
                "2023/02/05, 14:43:43",
                "Completed",
            ],
            [
                "JOB_5643_5764_6876_5662",
                "SUBMIT_5643_5764_6876_5662",
                "SCENARIO_5643_5764_6876_5662",
                "2023/02/05, 14:43:43",
                "Submitted",
            ],
            [
                "JOB_5643_5764_6876_5662",
                "SUBMIT_5643_5764_6876_5662",
                "SCENARIO_5643_5764_6876_5662",
                "2023/02/05, 14:43:43",
                "Blocked",
            ],
            [
                "JOB_5643_5764_6876_5662",
                "SUBMIT_5643_5764_6876_5662",
                "SCENARIO_5643_5764_6876_5662",
                "2023/02/05, 14:43:43",
                "Pending",
            ],
            [
                "JOB_5643_5764_6876_5662",
                "SUBMIT_5643_5764_6876_5662",
                "SCENARIO_5643_5764_6876_5662",
                "2023/02/05, 14:43:43",
                "Running",
            ],
            [
                "JOB_5643_5764_6876_5662",
                "SUBMIT_5643_5764_6876_5662",
                "SCENARIO_5643_5764_6876_5662",
                "2023/02/05, 14:43:43",
                "Canceled",
            ],
            [
                "JOB_5643_5764_6876_5662",
                "SUBMIT_5643_5764_6876_5662",
                "SCENARIO_5643_5764_6876_5662",
                "2023/02/05, 14:43:43",
                "Failed",
            ],
            [
                "JOB_5643_5764_6876_5662",
                "SUBMIT_5643_5764_6876_5662",
                "SCENARIO_5643_5764_6876_5662",
                "2023/02/05, 14:43:43",
                "Skipped",
            ],
            [
                "JOB_5643_5764_6876_5662",
                "SUBMIT_5643_5764_6876_5662",
                "SCENARIO_5643_5764_6876_5662",
                "2023/02/05, 14:43:43",
                "Abandoned",
            ],
        ],
    } = props;

    const dispatch = useDispatch();
    const module = useModule();

    const [order, setOrder] = useState<string>("asc");
    const [orderBy, setOrderBy] = useState<string>("calories");
    const [selected, setSelected] = useState<readonly string[]>([]);

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
                        <Tooltip title="Delete">
                            <IconButton>
                                <DeleteOutline />
                            </IconButton>
                        </Tooltip>
                    ) : (
                        <Tooltip title="Filter list">
                            <IconButton>{/* <FilterListIcon /> */}</IconButton>
                        </Tooltip>
                    )}
                </Toolbar>
                <TableContainer>
                    <Table sx={{ minWidth: 750 }} aria-labelledby="tableTitle" size="medium">
                        <TableHead>
                            <TableRow>
                                <TableCell padding="checkbox">
                                    <Checkbox
                                        color="primary"
                                        // indeterminate={numSelected > 0 && numSelected < rowCount}
                                        // checked={rowCount > 0 && numSelected === rowCount}
                                        // onChange={onSelectAllClick}
                                        inputProps={{
                                            "aria-label": "select all desserts",
                                        }}
                                    />
                                </TableCell>
                                <TableCell
                                    align={"left"}
                                    padding={"normal"}
                                    // sortDirection={orderBy === headCell.id ? order : false}
                                >
                                    <TableSortLabel
                                    // active={orderBy === headCell.id}
                                    // direction={orderBy === headCell.id ? order : "asc"}
                                    >
                                        <ListItemText primary="Job" secondary="ID" />
                                        {/* {orderBy === headCell.id ? (
                                            <Box component="span" sx={visuallyHidden}>
                                                {order === "desc" ? "sorted descending" : "sorted ascending"}
                                            </Box>
                                        ) : null} */}
                                    </TableSortLabel>
                                </TableCell>
                                <TableCell>Submit ID</TableCell>
                                <TableCell>
                                    <ListItemText primary="Submitted entity" secondary="ID" />
                                </TableCell>
                                <TableCell>Creation date</TableCell>
                                <TableCell>Status</TableCell>
                                <TableCell>Actions</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {jobs
                                ? jobs.map((row, index) => {
                                      const [id, submitID, entity, createdDt, status] = row;
                                      const isItemSelected = false;
                                      const labelId = `enhanced-table-checkbox-${index}`;

                                      return (
                                          <TableRow
                                              hover
                                              // onClick={(event) => handleClick(event, row.name)}
                                              role="checkbox"
                                              aria-checked={isItemSelected}
                                              tabIndex={-1}
                                              key={row.name}
                                              selected={isItemSelected}
                                              sx={{ cursor: "pointer" }}
                                          >
                                              <TableCell padding="checkbox">
                                                  <Checkbox
                                                      color="primary"
                                                      checked={isItemSelected}
                                                      inputProps={{
                                                          "aria-labelledby": labelId,
                                                      }}
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
                            {/* {emptyRows > 0 && (
                                <TableRow
                                    style={{
                                        height: (dense ? 33 : 53) * emptyRows,
                                    }}
                                >
                                    <TableCell colSpan={6} />
                                </TableRow>
                            )}*/}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>
        </Box>
    );
};

export default JobSelector;
