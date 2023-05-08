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
import Button from "@mui/material/Button";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import Dialog from "@mui/material/Dialog";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import {
  ChevronRight,
  ExpandMore,
  FlagOutlined,
  Close,
  DeleteOutline,
  Add,
  Send,
  CheckCircle,
  Cancel,
} from "@mui/icons-material";
import TreeItem from "@mui/lab/TreeItem";
import TreeView from "@mui/lab/TreeView";

import {
  useDynamicProperty,
  useDispatch,
  useModule,
  createRequestUpdateAction,
  getUpdateVar,
  createSendActionNameAction,
  useDispatchRequestUpdateOnFirstRender,
  createSendUpdateAction,
} from "taipy-gui";
import { Autocomplete, Chip, Divider, InputAdornment } from "@mui/material";

type Property = {
  id: string;
  key: string;
  value: string;
};

type Scenario = [string, string, undefined, number, boolean];
type Scenarios = Array<Scenario>;
type Cycles = Array<[string, string, Scenarios, number, boolean]>;

// id, is_primary, config_id, creation_date, label, tags, properties(key, value), pipelines(id, label), authorized_tags
type ScenarioFull = [
  string,
  boolean,
  string,
  string,
  string,
  string[],
  Array<[string, string]>,
  Array<[string, string]>,
  string[]
];
interface ScenarioDict {
  config: string;
  name: string;
  date: string;
  properties: Array<[string, string]>;
}

interface ScenarioVisualizerProps {
  id?: string;
  expandable?: boolean;
  expanded?: boolean;
  label?: string;
  buttonToSubmitScenario?: boolean;
  buttonToDeleteScenario?: boolean;
  primary?: boolean;
  configIdNotEditable?: boolean;
  frequencyNotEditable?: boolean;
  cycleNotEditable?: boolean;
  updateVarName?: string;
  tags?: Array<string>;
  scenarios?: Cycles | Scenarios;
  onSubmit: string;
  error?: string;
}

interface ScenarioNodesContentProps {
  scenarioId?: string;
  label?: string;
  primary?: boolean;
  sendScenario: (e: React.MouseEvent<HTMLElement>) => void;
}

interface PipelinesRowProps {
  action: string;
}

const FlagSx = {
  color: "#FFFFFF",
  fontSize: "11px",
};

const MainBoxSx = {
  maxWidth: 600,
  overflowY: "auto",
};

const TreeViewSx = {
  mb: 2,
};

const IconButtonSx = {
  p: 0,
};

const tagsAutocompleteSx = {
  "& .MuiOutlinedInput-root": {
    padding: "3px 15px 3px 3px !important",
  },
  maxWidth: "none",
};

const PipelinesRow = ({ action }: PipelinesRowProps) => {
  const [pipeline, setPipeline] = useState<string>();

  return (
    <Grid item xs={12} container justifyContent="space-between">
      <Grid item container xs={9}>
        {action === "EDIT" && (
          <TextField
            data-name="pipe"
            label="Pipeline 1"
            variant="outlined"
            name="pipeline"
            sx={{
              maxWidth: "none",
            }}
            value={pipeline}
            onBlur={(e: any) => {
              setPipeline(e.target.value);
            }}
            fullWidth
            InputProps={{
              endAdornment: (
                <>
                  {pipeline && (
                    <IconButton sx={{ padding: 0 }}>
                      <CheckCircle color="primary" />
                    </IconButton>
                  )}
                  {!pipeline && (
                    <IconButton sx={{ padding: 0 }}>
                      <Cancel color="inherit" />
                    </IconButton>
                  )}
                </>
              ),
            }}
          />
        )}
        {action !== "EDIT" && (
          <Typography variant="subtitle2">Training Pipeline</Typography>
        )}
      </Grid>
      <Grid item xs={2}>
        <Button variant="outlined" component="label" size="small" disabled>
          <Send color="info" />
        </Button>
      </Grid>
    </Grid>
  );
};

const ScenarioNodesContent = ({
  scenarioId,
  label,
  primary,
  sendScenario,
}: ScenarioNodesContentProps) => {
  return (
    <Grid
      container
      alignItems="center"
      direction="row"
      flexWrap="nowrap"
      justifyContent="space-between"
      spacing={1}
      sx={{ pt: 1, pb: 1 }}
    >
      <Grid item>
        {label}
        {primary && (
          <Chip
            color="primary"
            label={<FlagOutlined sx={FlagSx} />}
            size="small"
            sx={{ ml: 1 }}
          />
        )}
      </Grid>
      <Grid item>
        <IconButton
          data-id={scenarioId}
          sx={{ padding: 0 }}
          onClick={sendScenario}
        >
          <Send fontSize="small" color="info" />
        </IconButton>
      </Grid>
    </Grid>
  );
};

const ScenarioVisualizer = (props: ScenarioVisualizerProps) => {
  const {
    id = "",
    scenarios = [
      [
        "SCENARIO1_scenario_daily_cfg_29dfe360-3136-4a7a-94ab-fb2a7e2dc5c2",
        "1",
        [],
        1,
        true,
      ],
    ],
  } = props;

  const dispatch = useDispatch();
  const module = useModule();

  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [properties, setProperties] = useState<Property[]>([]);
  const [action, setAction] = useState<string>("EDIT");
  const [tags, setTags] = useState<string[]>(["tag1"]);
  const [newProp, setNewProp] = useState<Property>({
    id: "",
    key: "",
    value: "",
  });
  const [label, setLabel] = useState<string>();

  const onSelect = useCallback(
    (e: React.SyntheticEvent, nodeIds: Array<string> | string) => {},
    []
  );

  const sendScenario = useCallback((e: React.MouseEvent<HTMLElement>) => {},
  []);

  const updatePropertyField = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const { idx = "", name = "" } =
        e.currentTarget.parentElement?.parentElement?.dataset || {};
      if (name) {
        if (idx) {
          setProperties((props) =>
            props.map((p, i) => {
              if (idx == i + "") {
                p[name as keyof Property] = e.target.value;
              }
              return p;
            })
          );
        } else {
          setNewProp((np) => ({ ...np, [name]: e.target.value }));
        }
      }
    },
    []
  );

  const propertyDelete = useCallback((e: React.MouseEvent<HTMLElement>) => {
    const { id = "-1" } = e.currentTarget.dataset;
    setProperties((props) => props.filter((item) => item.id !== id));
  }, []);

  const propertyAdd = () => {
    setProperties((props) => [
      ...props,
      { ...newProp, id: props.length + 1 + "" },
    ]);
    setNewProp({ id: "", key: "", value: "" });
  };

  const onDeleteScenario = useCallback(() => {
    setConfirmDialogOpen(false);
    close();
  }, [close]);

  const onConfirmDialogOpen = useCallback(() => setConfirmDialogOpen(true), []);

  const onConfirmDialogClose = useCallback(
    () => setConfirmDialogOpen(false),
    []
  );

  return (
    <div>
      <Box sx={MainBoxSx}>
        <TreeView
          defaultCollapseIcon={<ExpandMore />}
          defaultExpandIcon={<ChevronRight />}
          sx={TreeViewSx}
          onNodeSelect={onSelect}
        >
          {scenarios
            ? scenarios.map((item) => {
                const [id, label, _, nodeType, primary] = item;
                return (
                  <TreeItem
                    key={id}
                    nodeId={id}
                    label={
                      <ScenarioNodesContent
                        scenarioId={id}
                        label={label}
                        primary={primary}
                        sendScenario={sendScenario}
                      />
                    }
                  >
                    <Grid container rowSpacing={2} sx={{ mt: 2 }}>
                      <Grid
                        item
                        xs={12}
                        container
                        justifyContent="space-between"
                      >
                        <Grid item xs={4}>
                          <Typography variant="subtitle2">Config ID</Typography>
                        </Grid>
                        <Grid item xs={8}>
                          <Typography variant="subtitle2">
                            LoremIpsum
                          </Typography>
                        </Grid>
                      </Grid>
                      <Grid
                        item
                        xs={12}
                        container
                        justifyContent="space-between"
                      >
                        <Grid item xs={4}>
                          <Typography variant="subtitle2">
                            Cycle / Frequency
                          </Typography>
                        </Grid>
                        <Grid item xs={8}>
                          <Typography variant="subtitle2">
                            Thursday 2023-02-05 / Daily
                          </Typography>
                        </Grid>
                      </Grid>
                      {action === "EDIT" && (
                        <Grid
                          item
                          xs={11}
                          container
                          justifyContent="space-between"
                        >
                          <TextField
                            label="Label"
                            variant="outlined"
                            fullWidth
                            sx={{
                              maxWidth: "none",
                            }}
                            value={label}
                            onChange={(
                              e: React.ChangeEvent<HTMLInputElement>
                            ) => {
                              setLabel(e.target.value);
                            }}
                            InputProps={{
                              endAdornment: (
                                <>
                                  {label ? (
                                    <IconButton sx={{ padding: 0 }}>
                                      <CheckCircle color="primary" />
                                    </IconButton>
                                  ) : (
                                    <IconButton sx={{ padding: 0 }}>
                                      <Cancel color="inherit" />
                                    </IconButton>
                                  )}
                                </>
                              ),
                            }}
                          />
                        </Grid>
                      )}
                      {action !== "EDIT" && (
                        <Grid
                          item
                          xs={12}
                          container
                          justifyContent="space-between"
                        >
                          <Grid item xs={4}>
                            <Typography variant="subtitle2">Label</Typography>
                          </Grid>
                          <Grid item xs={8}>
                            <Typography variant="subtitle2">
                              Scenario 3
                            </Typography>
                          </Grid>
                        </Grid>
                      )}
                      {action !== "EDIT" && (
                        <Grid
                          item
                          xs={12}
                          container
                          justifyContent="space-between"
                        >
                          <Grid item xs={4}>
                            <Typography variant="subtitle2">Tags</Typography>
                          </Grid>
                          <Grid item xs={8}>
                            <Chip label="Tag1" variant="outlined" />
                            <Chip label="Tag2" variant="outlined" />
                            <Chip label="Tag3" variant="outlined" />
                          </Grid>
                        </Grid>
                      )}
                      {action === "EDIT" && (
                        <Grid
                          item
                          xs={11}
                          container
                          justifyContent="space-between"
                        >
                          <Autocomplete
                            multiple
                            id="tags-filled"
                            options={tags.map((tag) => tag)}
                            defaultValue={[tags[0]]}
                            freeSolo
                            renderTags={(
                              value: readonly string[],
                              getTagProps
                            ) =>
                              value.map((option: string, index: number) => (
                                <Chip
                                  variant="outlined"
                                  label={option}
                                  sx={{ padding: 0 }}
                                  {...getTagProps({ index })}
                                />
                              ))
                            }
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
                                      {tags && tags.length > 0 ? (
                                        <IconButton sx={{ padding: 0 }}>
                                          <CheckCircle color="primary" />
                                        </IconButton>
                                      ) : (
                                        <IconButton sx={{ padding: 0 }}>
                                          <Cancel color="inherit" />
                                        </IconButton>
                                      )}
                                    </>
                                  ),
                                }}
                              />
                            )}
                          />
                        </Grid>
                      )}
                      <Grid item xs={12}>
                        <Divider />
                      </Grid>
                      <Grid
                        item
                        xs={12}
                        container
                        justifyContent="space-between"
                      >
                        <Typography variant="h6">Custom Properties</Typography>
                      </Grid>

                      {properties
                        ? properties.map((item, index) => (
                            <Grid
                              item
                              xs={12}
                              container
                              justifyContent="space-between"
                            >
                              <Grid item xs={4}>
                                {action !== "EDIT" && (
                                  <Typography variant="subtitle2">
                                    {item.key}
                                  </Typography>
                                )}
                                {action === "EDIT" && (
                                  <TextField
                                    label="Key"
                                    variant="outlined"
                                    value={item.key}
                                  />
                                )}
                              </Grid>
                              <Grid item xs={5}>
                                {action !== "EDIT" && (
                                  <Typography variant="subtitle2">
                                    {item.value}
                                  </Typography>
                                )}
                                {action === "EDIT" && (
                                  <TextField
                                    label="Value"
                                    variant="outlined"
                                    value={item.value}
                                  />
                                )}
                              </Grid>
                              <Grid item xs={2}>
                                {action !== "VIEW" && (
                                  <Button
                                    variant="outlined"
                                    component="label"
                                    sx={{ height: 50, width: 50, p: 0 }}
                                    color="inherit"
                                    data-id={item.id}
                                    onClick={propertyDelete}
                                  >
                                    <DeleteOutline
                                      fontSize="small"
                                      color="inherit"
                                    />
                                  </Button>
                                )}
                              </Grid>
                            </Grid>
                          ))
                        : null}
                      {action !== "VIEW" && (
                        <Grid
                          item
                          xs={12}
                          container
                          justifyContent="space-between"
                        >
                          <Grid item xs={4}>
                            <TextField
                              value={newProp.key}
                              data-name="key"
                              onChange={updatePropertyField}
                              label="Key"
                              variant="outlined"
                            />
                          </Grid>
                          <Grid item xs={5}>
                            <TextField
                              value={newProp.value}
                              data-name="value"
                              onChange={updatePropertyField}
                              label="Value"
                              variant="outlined"
                            />
                          </Grid>
                          <Grid item xs={2}>
                            <Button
                              variant="outlined"
                              component="label"
                              onClick={propertyAdd}
                              disabled={!newProp.key || !newProp.value}
                            >
                              <Add />
                            </Button>
                          </Grid>
                        </Grid>
                      )}
                      <Grid item xs={12}>
                        <Divider />
                      </Grid>

                      <Grid
                        item
                        xs={12}
                        container
                        justifyContent="space-between"
                      >
                        <Typography variant="h6">Pipelines</Typography>
                      </Grid>

                      <PipelinesRow action={action} />
                      <PipelinesRow action={action} />

                      <Grid item xs={12}>
                        <Divider />
                      </Grid>
                      <Grid
                        item
                        xs={12}
                        container
                        justifyContent="space-between"
                      >
                        <Button
                          variant="outlined"
                          color="primary"
                          disabled={action === "VIEW"}
                          onClick={onConfirmDialogOpen}
                        >
                          DELETE
                        </Button>
                        <Button variant="outlined" color="primary" disabled>
                          PROMOTE TO PRIMARY
                        </Button>
                      </Grid>
                    </Grid>
                  </TreeItem>
                );
              })
            : null}
        </TreeView>
        <Box>{props.error}</Box>
      </Box>

      <Dialog onClose={onConfirmDialogClose} open={confirmDialogOpen}>
        <DialogTitle>
          <Grid
            container
            direction="row"
            justifyContent="space-between"
            alignItems="center"
          >
            <Typography variant="h5">Delete Scenario</Typography>
            <IconButton
              aria-label="close"
              onClick={onConfirmDialogClose}
              sx={IconButtonSx}
            >
              <Close />
            </IconButton>
          </Grid>
        </DialogTitle>
        <DialogContent dividers>
          <Typography>
            Are you sure you want to delete this scenario?
          </Typography>
        </DialogContent>

        <DialogActions>
          <Button
            variant="outlined"
            color="inherit"
            onClick={onConfirmDialogClose}
          >
            CANCEL
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={onDeleteScenario}
          >
            DELETE
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};
export default ScenarioVisualizer;
