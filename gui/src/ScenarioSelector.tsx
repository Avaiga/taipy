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
import Badge, { BadgeOrigin } from "@mui/material/Badge";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import FormControl from "@mui/material/FormControl";
import FormGroup from "@mui/material/FormGroup";
import FormHelperText from "@mui/material/FormHelperText";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Dialog from "@mui/material/Dialog";
import Select from "@mui/material/Select";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import {
  ChevronRight,
  ExpandMore,
  FlagOutlined,
  Close,
  DeleteOutline,
  Add,
  EditOutlined,
} from "@mui/icons-material";
import TreeItem from "@mui/lab/TreeItem";
import TreeView from "@mui/lab/TreeView";
import { LocalizationProvider, DatePicker } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { useFormik } from "formik";

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

enum NodeType {
  CYCLE = 0,
  SCENARIO = 1,
}

type Scenario = [string, string, undefined, number, boolean];
type Scenarios = Array<Scenario>;
type Cycles = Array<[string, string, Scenarios, number, boolean]>;

interface ScenarioSelectorProps {
  id?: string;
  defaultShowAddButton: boolean;
  showAddButton?: boolean;
  defaultDisplayCycles: boolean;
  displayCycles?: boolean;
  defaultShowPrimaryFlag: boolean;
  showPrimaryFlag?: boolean;
  value?: Record<string, any>;
  updateVarName?: string;
  scenarios?: Cycles | Scenarios;
  onScenarioCreate: string;
  onChange?: string;
  coreChanged?: Record<string, unknown>;
  updateVars: string;
  configs?: Array<[string, string]>;
  error?: string;
  propagate?: boolean;
  scenario?: Record<string, string>;
}

interface ScenarioNodesProps {
  scenarios?: Scenarios | Scenario;
  showPrimary?: boolean;
  openEditDialog: () => void;
}

interface ScenarioNodesContentProps {
  label?: string;
  openEditDialog: () => void;
}

const BadgePos = {
  vertical: "top",
  horizontal: "left",
} as BadgeOrigin;

const BadgeSx = {
  "& .MuiBadge-badge": {
    marginLeft: "-12px",
    height: "19px",
    width: "12px",
  },
  width: "100%",
};

const FlagSx = {
  color: "#FFFFFF",
  fontSize: "11px",
};

const ScenarioNodesContent = ({
  label,
  openEditDialog,
}: ScenarioNodesContentProps) => {
  return (
    <Grid
      container
      alignItems="center"
      direction="row"
      flexWrap="nowrap"
      justifyContent="space-between"
      spacing={1}
    >
      <Grid item>{label}</Grid>
      <Grid item>
        <EditOutlined
          fontSize="small"
          color="primary"
          onClick={openEditDialog}
        />
      </Grid>
    </Grid>
  );
};

const ScenarioNodes = ({
  scenarios = [],
  showPrimary = true,
  openEditDialog,
}: ScenarioNodesProps) => {
  const sc =
    Array.isArray(scenarios) && scenarios.length && Array.isArray(scenarios[0])
      ? (scenarios as Scenarios)
      : scenarios
      ? [scenarios as Scenario]
      : [];
  return (
    <>
      {sc.map(([id, label, _, _nodeType, primary]) => (
        <TreeItem
          key={id}
          nodeId={id}
          label={
            showPrimary && primary ? (
              <Badge
                badgeContent={<FlagOutlined sx={FlagSx} />}
                color="primary"
                anchorOrigin={BadgePos}
                sx={BadgeSx}
              >
                <ScenarioNodesContent
                  label={label}
                  openEditDialog={openEditDialog}
                />
              </Badge>
            ) : (
              <ScenarioNodesContent
                label={label}
                openEditDialog={openEditDialog}
              />
            )
          }
        />
      ))}
    </>
  );
};

type Property = {
  id: string;
  key: string;
  value: string;
};

const MainBoxSx = {
  maxWidth: 300,
  overflowY: "auto",
};

const TreeViewSx = {
  mb: 2,
};

const CycleSx = {
  ".MuiTreeItem-content": {
    padding: "4px 8px",
    gap: "4px",
    borderRadius: "4px",
    mb: "5px",
  },
  ".MuiTreeItem-label": {
    fontWeight: "700",
    fontSize: "16px",
  },
};

const DialogContentSx = {
  width: "500px",
};

const ScenarioSelector = (props: ScenarioSelectorProps) => {
  const { id = "", scenarios = [], propagate = true } = props;
  const [open, setOpen] = useState(false);
  const [properties, setProperties] = useState<Property[]>([]);
  const [newProp, setNewProp] = useState<Property>({
    id: "",
    key: "",
    value: "",
  });
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [actionEdit, setActionEdit] = useState<boolean>(false);

  const dispatch = useDispatch();
  const module = useModule();

  useDispatchRequestUpdateOnFirstRender(dispatch, "", module, props.updateVars);

  const showAddButton = useDynamicProperty(
    props.showAddButton,
    props.defaultShowAddButton,
    true
  );
  const displayCycles = useDynamicProperty(
    props.displayCycles,
    props.defaultDisplayCycles,
    true
  );
  const showPrimaryFlag = useDynamicProperty(
    props.showPrimaryFlag,
    props.defaultShowPrimaryFlag,
    true
  );

  const onDeleteScenario = useCallback(() => {
    onConfirmDialogClose();
    onDialogClose();
  }, []);

  const onConfirmDialogOpen = useCallback(() => {
    setConfirmDialogOpen(true);
  }, []);

  const onConfirmDialogClose = useCallback(() => {
    setConfirmDialogOpen(false);
  }, []);

  const onDialogClose = useCallback(() => {
    setOpen(false);
  }, []);

  const onDialogOpen = useCallback(() => {
    setOpen(true);
    setActionEdit(false);
  }, []);

  const openEditDialog = useCallback(() => {
    setOpen(true);
    setActionEdit(true);
  }, []);

  const onSubmit = (values: any) => {
    values.properties = [...properties];
    dispatch(
      createSendActionNameAction(id, module, props.onScenarioCreate, values)
    );
    form.resetForm();
    setOpen(false);
    setProperties([]);
  };

  const propertyAdd = () => {
    setProperties((props) => [
      ...props,
      { ...newProp, id: props.length + 1 + "" },
    ]);
    setNewProp({ id: "", key: "", value: "" });
  };

  const propertyDelete = useCallback((e: React.MouseEvent<HTMLElement>) => {
    const { id = "-1" } = e.currentTarget.dataset;
    setProperties((props) => props.filter((item) => item.id !== id));
  }, []);

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

  const form = useFormik({
    initialValues: {
      config: "",
      name: "",
      date: new Date().toISOString(),
      properties: [],
    },
    onSubmit,
  });

  // Refresh on broadcast
  useEffect(() => {
    if (props.coreChanged?.scenario) {
      const updateVar = getUpdateVar(props.updateVars, "scenarios");
      updateVar &&
        dispatch(createRequestUpdateAction(id, module, [updateVar], true));
    }
  }, [props.coreChanged, props.updateVars, module, dispatch]);

  const onSelect = useCallback(
    (e: React.SyntheticEvent, nodeIds: Array<string> | string) => {
      const scenariosVar = getUpdateVar(props.updateVars, "scenarios");
      dispatch(
        createSendUpdateAction(
          props.updateVarName,
          nodeIds,
          module,
          props.onChange,
          propagate,
          scenariosVar
        )
      );
    },
    [props.updateVarName, props.updateVars, props.onChange, propagate, module]
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
                const [id, label, scenarios, nodeType, _] = item;
                return (
                  <>
                    {displayCycles ? (
                      nodeType === NodeType.CYCLE ? (
                        <TreeItem
                          key={id}
                          nodeId={id}
                          label={label}
                          sx={CycleSx}
                        >
                          <ScenarioNodes
                            scenarios={scenarios}
                            showPrimary={showPrimaryFlag}
                            openEditDialog={openEditDialog}
                          />
                        </TreeItem>
                      ) : (
                        <ScenarioNodes
                          scenarios={item as Scenario}
                          showPrimary={showPrimaryFlag}
                          openEditDialog={openEditDialog}
                        />
                      )
                    ) : nodeType === NodeType.SCENARIO ? (
                      <ScenarioNodes
                        scenarios={item as Scenario}
                        showPrimary={showPrimaryFlag}
                        openEditDialog={openEditDialog}
                      />
                    ) : (
                      <ScenarioNodes
                        scenarios={scenarios}
                        showPrimary={showPrimaryFlag}
                        openEditDialog={openEditDialog}
                      />
                    )}
                  </>
                );
              })
            : null}
        </TreeView>

        {showAddButton ? (
          <Button variant="outlined" onClick={onDialogOpen} fullWidth>
            ADD SCENARIO &nbsp;&nbsp;
            <Add />
          </Button>
        ) : null}

        <Box>{props.error}</Box>
      </Box>

      <Dialog onClose={onDialogClose} open={open}>
        <DialogTitle>
          <Grid
            container
            direction="row"
            justifyContent="space-between"
            alignItems="center"
          >
            <Typography variant="h5">{`${
              actionEdit ? `Edit` : `Create`
            } scenario`}</Typography>
            <IconButton
              aria-label="close"
              onClick={onDialogClose}
              sx={{ p: 0 }}
            >
              <Close />
            </IconButton>
          </Grid>
        </DialogTitle>
        <form onSubmit={form.handleSubmit}>
          <DialogContent sx={DialogContentSx} dividers>
            <Grid container rowSpacing={2}>
              <Grid item xs={12}>
                <FormGroup>
                  <FormControl fullWidth>
                    <InputLabel id="select-config">Configuration</InputLabel>
                    <Select
                      labelId="select-config"
                      label="Configuration"
                      {...form.getFieldProps("config")}
                      error={!!form.errors.config && form.touched.config}
                      disabled={actionEdit}
                    >
                      {props.configs
                        ? props.configs.map(([id, label]) => (
                            <MenuItem key={id} value={id}>
                              {label}
                            </MenuItem>
                          ))
                        : null}
                    </Select>
                    <FormHelperText
                      error={!!form.errors.config && form.touched.config}
                      sx={{ pl: 12 }}
                    >
                      {form.errors.config}
                    </FormHelperText>
                  </FormControl>
                </FormGroup>
              </Grid>
              <Grid item xs={12}>
                <FormGroup>
                  <TextField
                    {...form.getFieldProps("name")}
                    error={!!form.errors.name && form.touched.name}
                    helperText={form.errors.name}
                    label="Label"
                    variant="outlined"
                  />
                </FormGroup>
              </Grid>
              <Grid item xs={12}>
                <FormGroup>
                  <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <DatePicker
                      label="Date"
                      value={new Date(form.values.date)}
                      onChange={(date) =>
                        form.setFieldValue("date", date?.toISOString())
                      }
                      disabled={actionEdit}
                    />
                  </LocalizationProvider>
                </FormGroup>
              </Grid>
              <Grid item xs={12} container justifyContent="space-between">
                <Typography variant="h6">Custom Properties</Typography>
              </Grid>
              {properties
                ? properties.map((item, index) => (
                    <Grid
                      item
                      xs={12}
                      key={item.id}
                      container
                      justifyContent="space-between"
                    >
                      <Grid item xs={4}>
                        <TextField
                          value={item.key}
                          label="Key"
                          variant="outlined"
                          data-name="key"
                          data-idx={index}
                          onChange={updatePropertyField}
                        />
                      </Grid>
                      <Grid item xs={5}>
                        <TextField
                          value={item.value}
                          label="Value"
                          variant="outlined"
                          data-name="value"
                          data-idx={index}
                          onChange={updatePropertyField}
                        />
                      </Grid>
                      <Grid item xs={2}>
                        <Button
                          variant="outlined"
                          component="label"
                          data-id={item.id}
                          onClick={propertyDelete}
                        >
                          <DeleteOutline />
                        </Button>
                      </Grid>
                    </Grid>
                  ))
                : null}
              <Grid item xs={12} container justifyContent="space-between">
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
            </Grid>
          </DialogContent>

          <DialogActions>
            <Grid
              container
              justifyContent="space-between"
              spacing={2}
              sx={{ mr: 2, ml: 0 }}
            >
              <Grid item>
                {actionEdit && (
                  <Button
                    variant="outlined"
                    color="primary"
                    onClick={onConfirmDialogOpen}
                  >
                    DELETE
                  </Button>
                )}
              </Grid>
              <Grid item>
                <Button
                  variant="outlined"
                  onClick={onDialogClose}
                  sx={{ mr: 1 }}
                >
                  CANCEL
                </Button>
              </Grid>

              <Grid item>
                <Button
                  variant="contained"
                  type="submit"
                  disabled={!form.values.config || !form.values.name}
                >
                  {actionEdit ? "APPLY" : "CREATE"}
                </Button>
              </Grid>
            </Grid>
          </DialogActions>
        </form>
      </Dialog>

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
              onClick={onDialogClose}
              sx={{ p: 0 }}
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

export default ScenarioSelector;
