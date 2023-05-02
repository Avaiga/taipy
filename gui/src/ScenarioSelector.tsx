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
import { ChevronRight, ExpandMore, FlagOutlined, Close, DeleteOutline, Add, EditOutlined } from "@mui/icons-material";
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

type Property = {
  id: string;
  key: string;
  value: string;
};

type Scenario = [string, string, undefined, number, boolean];
type Scenarios = Array<Scenario>;
type Cycles = Array<[string, string, Scenarios, number, boolean]>;

// id, is_primary, config_id, creation_date, label, tags, properties(key, value), pipelines(id, label), authorized_tags
type ScenarioFull = [string, boolean, string, string, string, string[], Array<[string, string]>, Array<[string, string]>, string[]];
interface ScenarioDict {
  config: string;
  name: string;
  date: string;
  properties: Array<[string, string]>;
}

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
  onScenarioCrud: string;
  onChange?: string;
  coreChanged?: Record<string, unknown>;
  updateVars: string;
  configs?: Array<[string, string]>;
  error?: string;
  propagate?: boolean;
  scenarioEdit?: ScenarioFull;
  onScenarioSelect: string;
}

interface ScenarioNodesProps {
  scenarios?: Scenarios | Scenario;
  showPrimary?: boolean;
  openEditDialog: (e: React.MouseEvent<HTMLElement>) => void;
}

interface ScenarioNodesContentProps {
  scenarioId?: string;
  label?: string;
  openEditDialog: (e: React.MouseEvent<HTMLElement>) => void;
}

interface ScenarioEditDialogProps {
  scenario?: ScenarioFull;
  submit: (...values: any[]) => void;
  open: boolean;
  actionEdit: boolean;
  configs?: Array<[string, string]>;
  close: () => void;
}

const emptyScenario: ScenarioDict = {
  config: "",
  name: "",
  date: new Date().toISOString(),
  properties: [],
};

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

const ActionContentSx = { mr: 2, ml: 2 };

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
  maxHeight: "calc(100vh - 256px)",
};

const CancelBtnSx = {
  mr: 2,
};

const IconButtonSx = {
  p: 0,
};

const ScenarioNodesContent = ({ scenarioId, label, openEditDialog }: ScenarioNodesContentProps) => {
  return (
    <Grid container alignItems="center" direction="row" flexWrap="nowrap" justifyContent="space-between" spacing={1}>
      <Grid item>{label}</Grid>
      <Grid item>
        <IconButton data-id={scenarioId} onClick={openEditDialog}>
          <EditOutlined fontSize="small" color="primary" />
        </IconButton>
      </Grid>
    </Grid>
  );
};

const ScenarioNodes = ({ scenarios = [], showPrimary = true, openEditDialog }: ScenarioNodesProps) => {
  const sc = Array.isArray(scenarios) && scenarios.length && Array.isArray(scenarios[0]) ? (scenarios as Scenarios) : scenarios ? [scenarios as Scenario] : [];
  return (
    <>
      {sc.map(([id, label, _, _nodeType, primary]) => (
        <TreeItem
          key={id}
          nodeId={id}
          label={
            showPrimary && primary ? (
              <Badge badgeContent={<FlagOutlined sx={FlagSx} />} color="primary" anchorOrigin={BadgePos} sx={BadgeSx}>
                <ScenarioNodesContent scenarioId={id} label={label} openEditDialog={openEditDialog} />
              </Badge>
            ) : (
              <ScenarioNodesContent scenarioId={id} label={label} openEditDialog={openEditDialog} />
            )
          }
        />
      ))}
    </>
  );
};

const ScenarioEditDialog = ({ scenario, submit, open, actionEdit, configs, close }: ScenarioEditDialogProps) => {
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [properties, setProperties] = useState<Property[]>([]);
  const [newProp, setNewProp] = useState<Property>({
    id: "",
    key: "",
    value: "",
  });

  const propertyAdd = () => {
    setProperties((props) => [...props, { ...newProp, id: props.length + 1 + "" }]);
    setNewProp({ id: "", key: "", value: "" });
  };

  const propertyDelete = useCallback((e: React.MouseEvent<HTMLElement>) => {
    const { id = "-1" } = e.currentTarget.dataset;
    setProperties((props) => props.filter((item) => item.id !== id));
  }, []);

  const updatePropertyField = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const { idx = "", name = "" } = e.currentTarget.parentElement?.parentElement?.dataset || {};
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
  }, []);

  useEffect(() => {
    form.setValues(scenario ? { config: scenario[2], name: scenario[4], date: scenario[3], properties: scenario[6] } : emptyScenario);
    setProperties(scenario ? scenario[6].map(([k, v], i) => ({ id: i + "", key: k, value: v })) : []);
  }, [scenario]);

  const form = useFormik({
    initialValues: emptyScenario,
    onSubmit: (values: any) => {
      values.properties = [...properties];
      actionEdit && scenario && (values.id = scenario[0]);
      setProperties([]);
      submit(actionEdit, false, values);
      form.resetForm();
      close();
    },
  });

  const onDeleteScenario = useCallback(() => {
    submit(actionEdit, true, { id: scenario && scenario[0] });
    setConfirmDialogOpen(false);
    close();
  }, [close, actionEdit, scenario]);

  const onConfirmDialogOpen = useCallback(() => setConfirmDialogOpen(true), []);

  const onConfirmDialogClose = useCallback(() => setConfirmDialogOpen(false), []);

  return (
    <>
      <Dialog onClose={close} open={open}>
        <DialogTitle>
          <Grid container direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="h5">{`${actionEdit ? `Edit` : `Create`} scenario`}</Typography>
            <IconButton aria-label="close" onClick={close} sx={IconButtonSx}>
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
                      {configs
                        ? configs.map(([id, label]) => (
                            <MenuItem key={id} value={id}>
                              {label}
                            </MenuItem>
                          ))
                        : null}
                    </Select>
                    <FormHelperText error={!!form.errors.config && form.touched.config} sx={{ pl: 12 }}>
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
                      onChange={(date) => form.setFieldValue("date", date?.toISOString())}
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
                    <Grid item xs={12} key={item.id} container justifyContent="space-between">
                      <Grid item xs={4}>
                        <TextField value={item.key} label="Key" variant="outlined" data-name="key" data-idx={index} onChange={updatePropertyField} />
                      </Grid>
                      <Grid item xs={5}>
                        <TextField value={item.value} label="Value" variant="outlined" data-name="value" data-idx={index} onChange={updatePropertyField} />
                      </Grid>
                      <Grid item xs={2}>
                        <Button variant="outlined" component="label" data-id={item.id} onClick={propertyDelete}>
                          <DeleteOutline />
                        </Button>
                      </Grid>
                    </Grid>
                  ))
                : null}
              <Grid item xs={12} container justifyContent="space-between">
                <Grid item xs={4}>
                  <TextField value={newProp.key} data-name="key" onChange={updatePropertyField} label="Key" variant="outlined" />
                </Grid>
                <Grid item xs={5}>
                  <TextField value={newProp.value} data-name="value" onChange={updatePropertyField} label="Value" variant="outlined" />
                </Grid>
                <Grid item xs={2}>
                  <Button variant="outlined" component="label" onClick={propertyAdd} disabled={!newProp.key || !newProp.value}>
                    <Add />
                  </Button>
                </Grid>
              </Grid>
            </Grid>
          </DialogContent>

          <DialogActions>
            <Grid container justifyContent="space-between" sx={ActionContentSx}>
              {actionEdit && (
                <Grid item xs={6}>
                  <Button variant="outlined" color="primary" onClick={onConfirmDialogOpen}>
                    DELETE
                  </Button>
                </Grid>
              )}
              <Grid item container xs={actionEdit ? 6 : 12} justifyContent="flex-end">
                <Grid item sx={CancelBtnSx}>
                  <Button variant="outlined" onClick={close}>
                    CANCEL
                  </Button>
                </Grid>
                <Grid item>
                  <Button variant="contained" type="submit" disabled={!form.values.config || !form.values.name}>
                    {actionEdit ? "APPLY" : "CREATE"}
                  </Button>
                </Grid>
              </Grid>
            </Grid>
          </DialogActions>
        </form>
      </Dialog>

      <Dialog onClose={onConfirmDialogClose} open={confirmDialogOpen}>
        <DialogTitle>
          <Grid container direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="h5">Delete Scenario</Typography>
            <IconButton aria-label="close" onClick={onConfirmDialogClose} sx={IconButtonSx}>
              <Close />
            </IconButton>
          </Grid>
        </DialogTitle>
        <DialogContent dividers>
          <Typography>Are you sure you want to delete this scenario?</Typography>
        </DialogContent>

        <DialogActions>
          <Button variant="outlined" color="inherit" onClick={onConfirmDialogClose}>
            CANCEL
          </Button>
          <Button variant="contained" color="primary" onClick={onDeleteScenario}>
            DELETE
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

const ScenarioSelector = (props: ScenarioSelectorProps) => {
  const { id = "", scenarios = [], propagate = true } = props;
  const [open, setOpen] = useState(false);
  const [actionEdit, setActionEdit] = useState<boolean>(false);

  const dispatch = useDispatch();
  const module = useModule();

  useDispatchRequestUpdateOnFirstRender(dispatch, "", module, props.updateVars);

  const showAddButton = useDynamicProperty(props.showAddButton, props.defaultShowAddButton, true);
  const displayCycles = useDynamicProperty(props.displayCycles, props.defaultDisplayCycles, true);
  const showPrimaryFlag = useDynamicProperty(props.showPrimaryFlag, props.defaultShowPrimaryFlag, true);

  const onDialogOpen = useCallback(() => {
    setOpen(true);
    setActionEdit(false);
  }, []);

  const onDialogClose = useCallback(() => {
    setOpen(false);
    setActionEdit(false);
  }, []);

  const openEditDialog = useCallback(
    (e: React.MouseEvent<HTMLElement>) => {
      const { id: scenId } = e.currentTarget?.dataset || {};
      scenId && props.onScenarioSelect && dispatch(createSendActionNameAction(id, module, props.onScenarioSelect, scenId));
      setOpen(true);
      setActionEdit(true);
      return false;
    },
    [props.onScenarioSelect]
  );

  const onSubmit = useCallback(
    (...values: any[]) => dispatch(createSendActionNameAction(id, module, props.onScenarioCrud, ...values)),
    [id, module, props.onScenarioCrud]
  );

  // Refresh on broadcast
  useEffect(() => {
    if (props.coreChanged?.scenario) {
      const updateVar = getUpdateVar(props.updateVars, "scenarios");
      updateVar && dispatch(createRequestUpdateAction(id, module, [updateVar], true));
    }
  }, [props.coreChanged, props.updateVars, module, dispatch]);

  const onSelect = useCallback(
    (e: React.SyntheticEvent, nodeIds: Array<string> | string) => {
      const { cycle = false } = (e.currentTarget as HTMLElement)?.parentElement?.dataset || {};
      if (cycle) {
        return;
      }
      const scenariosVar = getUpdateVar(props.updateVars, "scenarios");
      dispatch(createSendUpdateAction(props.updateVarName, nodeIds, module, props.onChange, propagate, scenariosVar));
    },
    [props.updateVarName, props.updateVars, props.onChange, propagate, module]
  );

  return (
    <div>
      <Box sx={MainBoxSx}>
        <TreeView defaultCollapseIcon={<ExpandMore />} defaultExpandIcon={<ChevronRight />} sx={TreeViewSx} onNodeSelect={onSelect}>
          {scenarios
            ? scenarios.map((item) => {
                const [id, label, scenarios, nodeType, _] = item;
                return (
                  <>
                    {displayCycles ? (
                      nodeType === NodeType.CYCLE ? (
                        <TreeItem key={id} nodeId={id} label={label} sx={CycleSx} data-cycle>
                          <ScenarioNodes scenarios={scenarios} showPrimary={showPrimaryFlag} openEditDialog={openEditDialog} />
                        </TreeItem>
                      ) : (
                        <ScenarioNodes scenarios={item as Scenario} showPrimary={showPrimaryFlag} openEditDialog={openEditDialog} />
                      )
                    ) : nodeType === NodeType.SCENARIO ? (
                      <ScenarioNodes scenarios={item as Scenario} showPrimary={showPrimaryFlag} openEditDialog={openEditDialog} />
                    ) : (
                      <ScenarioNodes scenarios={scenarios} showPrimary={showPrimaryFlag} openEditDialog={openEditDialog} />
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

      <ScenarioEditDialog
        close={onDialogClose}
        actionEdit={actionEdit}
        open={open}
        configs={props.configs}
        scenario={props.scenarioEdit}
        submit={onSubmit}
      ></ScenarioEditDialog>
    </div>
  );
};

export default ScenarioSelector;
