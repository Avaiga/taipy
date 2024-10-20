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
    getUpdateVar,
    useDispatch,
    useDispatchRequestUpdateOnFirstRender,
    useModule,
} from "taipy-gui";

import { useClassNames, EllipsisSx, SecondaryEllipsisProps, CoreProps, calculateTimeDifference } from "./utils";
import StatusChip from "./StatusChip";

interface JobDetailsViewerProps extends CoreProps {
    job: JobDetail;
    showSubmitId?: boolean,
    showTaskLabel?: boolean,
    showSubmittedLabel?: boolean,
    showExecutionDuration?: boolean,
    showPendingDuration?: boolean,
    showBlockedDuration?: boolean,
    showSubmissionDuration?: boolean,
    showCancel?: boolean;
    showDelete?: boolean;
    showStackTrace?: boolean,
    onJobAction?: string;
    updateJbVars?: string;
    height?: string,
    width?: string;
}

// job id, creation date, status, submit id, job name, entity id, entity name, pending duration, blocked duration, finished at, not cancellable, not deletable, execution time, logs, 
export type JobDetail = [string, string, number, string, string, string, string, string, string, string, string, string, string, string[]];
const invalidJob: JobDetail = ["", "", 0,  "", "", "", "", "", "" , "", "", "", "", []];

const JobDetailsViewer = (props: JobDetailsViewerProps) => {
    const { 
        updateVarName = "", 
        id = "", 
        updateJbVars = "", 
        height = "50vh",
        width = "50vw", 
        coreChanged
    } = props;

    const [
        jobId,
        creationDate,
        status,
        submitId,
        jobName,
        entityId,
        entityName,
        pendingDuration,
        blockedDuration,
        finishedAt,
        notCancellable,
        notDeletable,
        executionDuration,
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
                    createSendActionNameAction(props.id, module, props.onJobAction, {
                        id: jobId,
                        action: "delete",
                        error_id: getUpdateVar(updateJbVars, "error_id"),
                    })
                );
            } catch (e) {
                console.warn("Error parsing id for delete.", e);
            }
        },
        [jobId, dispatch, module, props.id, props.onJobAction, updateJbVars]
    );

    const handleCancelJob = useCallback(
        (event: React.MouseEvent<HTMLElement>) => {
            event.stopPropagation();
            try {
                dispatch(
                    createSendActionNameAction(props.id, module, props.onJobAction, {
                        id: jobId,
                        action: "cancel",
                        error_id: getUpdateVar(updateJbVars, "error_id"),
                    })
                );
            } catch (e) {
                console.warn("Error parsing id for cancel.", e);
            }
        },
        [jobId, dispatch, module, props.id, props.onJobAction, updateJbVars]
    )

    useEffect(() => {
        if (coreChanged?.job  == jobId) {
            updateVarName && dispatch(createRequestUpdateAction(id, module, [updateVarName], true));
        }
    }, [coreChanged, updateVarName, jobId, module, dispatch, id]);

    return (
        <Grid container className={className} sx={{ maxWidth: width, maxHeight: height }}>
            <Grid size={4}>
                <Typography>Job Id</Typography>
            </Grid>
            <Grid size={8}>
                <Tooltip title={jobId}>
                    <Typography sx={EllipsisSx}>{jobId}</Typography>
                </Tooltip>
            </Grid>
            <Grid size={4}>
                <Typography>Creation date</Typography>
            </Grid>
            <Grid size={8}>
                <Typography>{creationDate ? new Date(creationDate).toLocaleString() : ""}</Typography>
            </Grid>
            <Grid size={4}>
                <Typography>Status</Typography>
            </Grid>
            <Grid size={8}>
                <StatusChip status={status} />
            </Grid>
            {props.showSubmitId && (
                <Grid>
                    <Grid size={4}>
                        <Typography>Submit Id</Typography>
                    </Grid>
                    <Grid size={8}>
                        <Tooltip title={submitId}>
                            <Typography sx={EllipsisSx}>{submitId}</Typography>
                        </Tooltip>
                    </Grid>
                </Grid>
                
            )}
            {props.showTaskLabel && (
                <Grid>
                    <Grid size={4}>
                        <Typography>Task label</Typography>
                    </Grid>
                    <Grid size={8}>
                        <Tooltip title={jobName}>
                            <Typography sx={EllipsisSx}>{jobName}</Typography>
                        </Tooltip>
                    </Grid>
                </Grid>
            )}
            {props.showSubmittedLabel && (
                <Grid>
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
                </Grid>
            )}
            {props.showExecutionDuration && (
                <Grid>
                    <Grid size={4}>
                        <Typography>Execution Duration</Typography>
                    </Grid>
                    <Grid size={8}>
                        <Typography>{executionDuration}</Typography>
                    </Grid>
                </Grid>
            )}
            {props.showPendingDuration && (
                <Grid>
                    <Grid size={4}>
                        <Typography>Pending time</Typography>
                    </Grid>
                    <Grid size={8}>
                        <Typography>{pendingDuration}</Typography>
                    </Grid>
                </Grid>
            )}
            {props.showBlockedDuration && (
                <Grid>
                    <Grid size={4}>
                        <Typography>Blocked time</Typography>
                    </Grid>
                    <Grid size={8}>
                        <Typography>{blockedDuration}</Typography>
                    </Grid>
                </Grid>
            )}
            {props.showSubmissionDuration && (
                <Grid>
                    <Grid size={4}>
                        <Typography>Submission duration</Typography>
                    </Grid>
                    <Grid size={8}>
                        <Typography>{(creationDate && finishedAt) ? calculateTimeDifference(new Date(creationDate), new Date(finishedAt)) : ""}</Typography>
                    </Grid>
                </Grid>
            )}
            <Divider />
            {props.showStackTrace && (
                <Grid>
                    <Grid size={12}>
                        <Typography>Stack Trace</Typography>
                </Grid>
                <Grid size={12}>
                    <Typography variant="caption" component="pre" overflow="auto" maxHeight="50vh">
                        {stacktrace.join("<br/>")}
                    </Typography>
                </Grid>
                </Grid>
            )}
            {props.showCancel ? (
                <>
                    <Divider />
                    <Grid size={6}>
                        <Tooltip title={notCancellable}>
                            <span>
                                <Button variant="outlined" onClick={handleCancelJob} disabled={!!notCancellable}>
                                    Cancel
                                </Button>
                            </span>
                        </Tooltip>
                    </Grid>
                </>
            ) : null}
            {props.showDelete ? (
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
        </Grid>
    );
};

export default JobDetailsViewer;
