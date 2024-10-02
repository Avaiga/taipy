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

import React, { useEffect, useCallback } from "react";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid2";
import ListItemText from "@mui/material/ListItemText";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";

import {
    createRequestUpdateAction,
    createSendActionNameAction,
    createUnBroadcastAction,
    getUpdateVar,
    useDispatch,
    useDispatchRequestUpdateOnFirstRender,
    useModule,
} from "taipy-gui";

import { useClassNames, EllipsisSx, SecondaryEllipsisProps, CoreProps } from "./utils";
import StatusChip from "./StatusChip";

interface JobViewerProps extends CoreProps {
    job: JobDetail;
    onDelete?: string;
    updateJbVars?: string;
    inDialog?: boolean;
    width?: string;
}

// job id, job name, entity id, entity name, submit id, creation date, status, not deletable, execution time, logs
export type JobDetail = [string, string, string, string, string, string, number, string, string, string[]];
const invalidJob: JobDetail = ["", "", "", "", "", "", 0, "", "", []];

const JobViewer = (props: JobViewerProps) => {
    const { updateVarName = "", id = "", updateJbVars = "", inDialog = false, width = "50vw", coreChanged } = props;

    const [
        jobId,
        jobName,
        entityId,
        entityName,
        submissionId,
        creationDate,
        status,
        notDeletable,
        executionTime,
        stacktrace,
    ] = props.job || invalidJob;

    const dispatch = useDispatch();
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);

    useDispatchRequestUpdateOnFirstRender(dispatch, id, module, undefined, updateVarName);

    const handleDeleteJob = useCallback(
        (event: React.MouseEvent<HTMLElement>) => {
            event.stopPropagation();
            try {
                dispatch(
                    createSendActionNameAction(props.id, module, props.onDelete, {
                        id: jobId,
                        action: "delete",
                        error_id: getUpdateVar(updateJbVars, "error_id"),
                    })
                );
            } catch (e) {
                console.warn("Error parsing ids for delete.", e);
            }
        },
        [jobId, dispatch, module, props.id, props.onDelete, updateJbVars]
    );

    useEffect(() => {
        if (coreChanged?.name) {
            const toRemove = [...coreChanged.stack]
                .map((bc) => {
                    if ((bc as Record<string, unknown>).job  == jobId) {
                        updateVarName && dispatch(createRequestUpdateAction(id, module, [updateVarName], true));
                        return bc;
                    }
                    return undefined;
                })
                .filter((v) => v);
            toRemove.length && dispatch(createUnBroadcastAction(coreChanged.name, ...toRemove));
        }
    }, [coreChanged, updateVarName, jobId, module, dispatch, id]);

    return (
        <Grid container className={className} sx={{ maxWidth: width }}>
            {inDialog ? null : (
                <>
                    <Grid size={4}>
                        <Typography>Job Name</Typography>
                    </Grid>
                    <Grid size={8}>
                        <Typography>{jobName}</Typography>
                    </Grid>
                    <Divider />
                </>
            )}
            <Grid size={4}>
                <Typography>Job Id</Typography>
            </Grid>
            <Grid size={8}>
                <Tooltip title={jobId}>
                    <Typography sx={EllipsisSx}>{jobId}</Typography>
                </Tooltip>
            </Grid>
            <Grid size={4}>
                <Typography>Submission Id</Typography>
            </Grid>
            <Grid size={8}>
                <Tooltip title={submissionId}>
                    <Typography sx={EllipsisSx}>{submissionId}</Typography>
                </Tooltip>
            </Grid>
            <Grid size={4}>
                <Typography>Submitted entity</Typography>
            </Grid>
            <Grid size={8}>
                <Tooltip title={entityId}>
                    <ListItemText
                        primary={entityName}
                        secondary={entityId}
                        secondaryTypographyProps={SecondaryEllipsisProps}
                    />
                </Tooltip>
            </Grid>
            <Grid size={4}>
                <Typography>Execution time</Typography>
            </Grid>
            <Grid size={8}>
                <Typography>{executionTime}</Typography>
            </Grid>
            <Grid size={4}>
                <Typography>Status</Typography>
            </Grid>
            <Grid size={8}>
                <StatusChip status={status} />
            </Grid>
            <Grid size={4}>
                <Typography>Creation date</Typography>
            </Grid>
            <Grid size={8}>
                <Typography>{creationDate ? new Date(creationDate).toLocaleString() : ""}</Typography>
            </Grid>
            <Divider />
            <Grid size={12}>
                <Typography>Stack Trace</Typography>
            </Grid>
            <Grid size={12}>
                <Typography variant="caption" component="pre" overflow="auto" maxHeight="50vh">
                    {stacktrace.join("<br/>")}
                </Typography>
            </Grid>
            {props.onDelete ? (
                <>
                    <Divider />
                    <Grid size={6}>
                        <Tooltip title={notDeletable}>
                            <span>
                                <Button variant="outlined" onClick={handleDeleteJob} disabled={!!notDeletable}>
                                    Delete
                                </Button>
                            </span>
                        </Tooltip>
                    </Grid>
                </>
            ) : null}
            {props.children}
        </Grid>
    );
};

export default JobViewer;
