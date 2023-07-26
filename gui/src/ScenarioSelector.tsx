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
import { Theme, alpha } from "@mui/material";
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

import { Cycle, Scenario } from "./icons";
import ConfirmDialog from "./utils/ConfirmDialog";
import {
    BadgePos,
    BadgeSx,
    BaseTreeViewSx,
    FlagSx,
    MainBoxSx,
    ParentItemSx,
    ScFProps,
    ScenarioFull,
    useClassNames,
} from "./utils";

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

interface ScenarioDict {
    id?: string;
    config: string;
    name: string;
    date: string;
    properties: Array<Property>;
}

interface ScenarioSelectorProps {
    id?: string;
    defaultShowAddButton: boolean;
    showAddButton?: boolean;
    defaultDisplayCycles: boolean;
    displayCycles?: boolean;
    defaultShowPrimaryFlag: boolean;
    showPrimaryFlag?: boolean;
    updateVarName?: string;
    scenarios?: Cycles | Scenarios;
    onScenarioCrud: string;
    onChange?: string;
    onCreation?: string;
    coreChanged?: Record<string, unknown>;
    updateVars: string;
    configs?: Array<[string, string]>;
    error?: string;
    propagate?: boolean;
    scenarioEdit?: ScenarioFull;
    onScenarioSelect: string;
    value?: string;
    defaultValue?: string;
    height: string;
    libClassName?: string;
    className?: string;
    dynamicClassName?: string;
}

interface ScenarioNodesProps {
    scenarios?: Scenarios | Scenario;
    showPrimary?: boolean;
    openEditDialog: (e: React.MouseEvent<HTMLElement>) => void;
}

interface ScenarioItemProps {
    scenarioId?: string;
    label?: string;
    isPrimary?: boolean;
    openEditDialog: (e: React.MouseEvent<HTMLElement>) => void;
}

interface ScenarioEditDialogProps {
    scenario?: ScenarioFull;
    submit: (...values: unknown[]) => void;
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

const tinyIconButtonSx = {
    position: "relative",
    display: "flex",
    width: "1rem",
    height: "1rem",
    fontSize: "0.750rem",

    "&::before": {
        content: "''",
        position: "absolute",
        top: "50%",
        left: "50%",
        transform: "translate(-50%,-50%)",
        width: "2rem",
        height: "2rem",
    },

    "& .MuiSvgIcon-root": {
        color: "inherit",
        fontSize: "inherit",
    },
};

const ActionContentSx = { mr: 2, ml: 2 };

const treeItemLabelSx = {
    display: "flex",
    alignItems: "center",
    gap: 1,
};

const DialogContentSx = {
    maxHeight: "calc(100vh - 256px)",

    "& .MuiFormControl-root": {
        maxWidth: "100%",
    },
};

const configHelperTextSx = { pl: 12 };

const SquareButtonSx = {
    mb: 0,
    p: 0,
    minWidth: 0,
    aspectRatio: "1",
};

const CancelBtnSx = {
    mr: 2,
};

const IconButtonSx = {
    p: 0,
};

const tinyEditIconButtonSx = (theme: Theme) => ({
    ...tinyIconButtonSx,
    backgroundColor: alpha(theme.palette.text.primary, 0.15),
    color: "text.primary",

    "&:hover": {
        backgroundColor: "primary.main",
        color: "primary.contrastText",
    },
});

const ScenarioItem = ({ scenarioId, label, isPrimary, openEditDialog }: ScenarioItemProps) => (
    <Grid container alignItems="center" direction="row" flexWrap="nowrap" spacing={1}>
        <Grid item xs sx={treeItemLabelSx}>
            {isPrimary ? (
                <Badge
                    badgeContent={<FlagOutlined sx={FlagSx} />}
                    color="primary"
                    anchorOrigin={BadgePos as BadgeOrigin}
                    sx={BadgeSx}
                >
                    <Scenario fontSize="small" color="primary" />
                </Badge>
            ) : (
                <Scenario fontSize="small" color="primary" />
            )}
            {label}
        </Grid>
        <Grid item xs="auto">
            <IconButton data-id={scenarioId} onClick={openEditDialog} sx={tinyEditIconButtonSx}>
                <EditOutlined />
            </IconButton>
        </Grid>
    </Grid>
);

const ScenarioNodes = ({ scenarios = [], showPrimary = true, openEditDialog }: ScenarioNodesProps) => {
    const sc =
        Array.isArray(scenarios) && scenarios.length
            ? Array.isArray(scenarios[0])
                ? (scenarios as Scenarios)
                : [scenarios as Scenario]
            : [];
    return (
        <>
            {
                // eslint-disable-next-line @typescript-eslint/no-unused-vars
                sc.map(([id, label, _, _nodeType, primary]) => (
                    <TreeItem
                        key={id}
                        nodeId={id}
                        label={
                            <ScenarioItem
                                scenarioId={id}
                                label={label}
                                isPrimary={showPrimary && primary}
                                openEditDialog={openEditDialog}
                            />
                        }
                    />
                ))
            }
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

    const propertyAdd = useCallback(() => {
        setProperties((ps) => [...ps, { ...newProp, id: ps.length + 1 + "" }]);
        setNewProp({ id: "", key: "", value: "" });
    }, [newProp]);

    const propertyDelete = useCallback((e: React.MouseEvent<HTMLElement>) => {
        const { id = "-1" } = e.currentTarget.dataset;
        setProperties((ps) => ps.filter((item) => item.id !== id));
    }, []);

    const updatePropertyField = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const { idx = "", name = "" } = e.currentTarget.parentElement?.parentElement?.dataset || {};
        if (name) {
            if (idx) {
                setProperties((ps) =>
                    ps.map((p, i) => {
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

    const form = useFormik({
        initialValues: emptyScenario,
        onSubmit: (values: ScenarioDict) => {
            values.properties = [...properties];
            setProperties([]);
            submit(actionEdit, false, values);
            form.resetForm({ values: { ...emptyScenario, config: configs?.length === 1 ? configs[0][0] : "" } });
            close();
        },
    });

    useEffect(() => {
        form.setValues(
            scenario
                ? {
                      id: scenario[ScFProps.id],
                      config: scenario[ScFProps.config_id],
                      name: scenario[ScFProps.label],
                      date: scenario[ScFProps.creation_date],
                      properties: [],
                  }
                : { ...emptyScenario, config: configs?.length === 1 ? configs[0][0] : "" }
        );
        setProperties(
            scenario ? scenario[ScFProps.properties].map(([k, v], i) => ({ id: i + "", key: k, value: v })) : []
        );
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [scenario]);

    const onDeleteScenario = useCallback(() => {
        submit(actionEdit, true, { id: scenario && scenario[ScFProps.id] });
        setConfirmDialogOpen(false);
        close();
    }, [close, actionEdit, scenario, submit]);

    const onConfirmDialogOpen = useCallback(() => setConfirmDialogOpen(true), []);

    const onConfirmDialogClose = useCallback(() => setConfirmDialogOpen(false), []);

    return (
        <>
            <Dialog onClose={close} open={open} maxWidth="sm">
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
                                        <FormHelperText
                                            error={!!form.errors.config && form.touched.config}
                                            sx={configHelperTextSx}
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
                                      <Grid item xs={12} key={item.id} container spacing={1} alignItems="center">
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
                                          <Grid item xs>
                                              <TextField
                                                  value={item.value}
                                                  label="Value"
                                                  variant="outlined"
                                                  data-name="value"
                                                  data-idx={index}
                                                  onChange={updatePropertyField}
                                              />
                                          </Grid>
                                          <Grid item xs="auto">
                                              <Button
                                                  variant="outlined"
                                                  color="inherit"
                                                  data-id={item.id}
                                                  onClick={propertyDelete}
                                                  sx={SquareButtonSx}
                                              >
                                                  <DeleteOutline />
                                              </Button>
                                          </Grid>
                                      </Grid>
                                  ))
                                : null}
                            <Grid item xs={12} container spacing={1} justifyContent="space-between">
                                <Grid item xs={4}>
                                    <TextField
                                        value={newProp.key}
                                        data-name="key"
                                        onChange={updatePropertyField}
                                        label="Key"
                                        variant="outlined"
                                    />
                                </Grid>
                                <Grid item xs>
                                    <TextField
                                        value={newProp.value}
                                        data-name="value"
                                        onChange={updatePropertyField}
                                        label="Value"
                                        variant="outlined"
                                    />
                                </Grid>
                                <Grid item xs="auto">
                                    <Button
                                        variant="outlined"
                                        onClick={propertyAdd}
                                        disabled={!newProp.key || !newProp.value}
                                        sx={SquareButtonSx}
                                    >
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
                                    <Button
                                        variant="outlined"
                                        color="error"
                                        onClick={onConfirmDialogOpen}
                                        disabled={!scenario || !scenario[ScFProps.deletable]}
                                    >
                                        Delete
                                    </Button>
                                </Grid>
                            )}
                            <Grid item container xs={actionEdit ? 6 : 12} justifyContent="flex-end">
                                <Grid item sx={CancelBtnSx}>
                                    <Button variant="outlined" color="inherit" onClick={close}>
                                        Cancel
                                    </Button>
                                </Grid>
                                <Grid item>
                                    <Button
                                        variant="contained"
                                        type="submit"
                                        disabled={!form.values.config || !form.values.name}
                                    >
                                        {actionEdit ? "Apply" : "Create"}
                                    </Button>
                                </Grid>
                            </Grid>
                        </Grid>
                    </DialogActions>
                </form>
            </Dialog>

            <ConfirmDialog
                title="Delete Scenario"
                message="Are you sure you want to delete this scenario?"
                confirm="Delete"
                open={confirmDialogOpen}
                onClose={onConfirmDialogClose}
                onConfirm={onDeleteScenario}
            />
        </>
    );
};

const ScenarioSelector = (props: ScenarioSelectorProps) => {
    const { id = "", scenarios, propagate = true, defaultValue = "", value } = props;
    const [open, setOpen] = useState(false);
    const [actionEdit, setActionEdit] = useState<boolean>(false);
    const [selected, setSelected] = useState("");

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);

    const dispatch = useDispatch();
    const module = useModule();

    useDispatchRequestUpdateOnFirstRender(dispatch, id, module, props.updateVars);

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
            e.stopPropagation();
            const { id: scenId } = e.currentTarget?.dataset || {};
            scenId &&
                props.onScenarioSelect &&
                dispatch(createSendActionNameAction(id, module, props.onScenarioSelect, scenId));
            setOpen(true);
            setActionEdit(true);
        },
        [props.onScenarioSelect, id, dispatch, module]
    );

    const onSelect = useCallback(
        (e: React.SyntheticEvent, nodeId: string) => {
            const { cycle = false } = (e?.currentTarget as HTMLElement)?.parentElement?.dataset || {};
            const scenariosVar = getUpdateVar(props.updateVars, "scenarios");
            dispatch(
                createSendUpdateAction(
                    props.updateVarName,
                    cycle ? undefined : nodeId,
                    module,
                    props.onChange,
                    propagate,
                    scenariosVar
                )
            );
            setSelected(nodeId);
        },
        [props.updateVarName, props.updateVars, props.onChange, propagate, dispatch, module]
    );

    const unselect = useCallback(() => {
        if (selected) {
            const scenariosVar = getUpdateVar(props.updateVars, "scenarios");
            dispatch(
                createSendUpdateAction(props.updateVarName, undefined, module, props.onChange, propagate, scenariosVar)
            );
            setSelected("");
        }
    }, [props.updateVarName, props.updateVars, props.onChange, propagate, dispatch, module, selected]);

    const onSubmit = useCallback(
        (...values: unknown[]) => {
            dispatch(createSendActionNameAction(id, module, props.onScenarioCrud, ...values, props.onCreation));
            if (values.length > 1 && values[1]) {
                // delete requested => unselect current node
                unselect();
            }
        },
        [id, props.onScenarioCrud, dispatch, module, props.onCreation, unselect]
    );

    // Refresh on broadcast
    useEffect(() => {
        if (props.coreChanged?.scenario) {
            const updateVar = getUpdateVar(props.updateVars, "scenarios");
            updateVar && dispatch(createRequestUpdateAction(id, module, [updateVar], true));
        }
    }, [props.coreChanged, props.updateVars, module, dispatch, id]);

    useEffect(() => {
        if (value !== undefined && value !== null) {
            setSelected(value);
        } else if (defaultValue) {
            try {
                const parsedValue = JSON.parse(defaultValue);
                if (Array.isArray(parsedValue)) {
                    parsedValue.length && setSelected(parsedValue[0]);
                } else {
                    setSelected(parsedValue);
                }
            } catch {
                setSelected(defaultValue);
            }
        } else if (value === null) {
            setSelected("");
        }
    }, [defaultValue, value]);

    useEffect(() => {
        if (scenarios && !scenarios.length) {
            unselect();
        }
    }, [scenarios, unselect]);

    const treeViewSx = useMemo(() => ({ ...BaseTreeViewSx, maxHeight: props.height || "50vh" }), [props.height]);

    return (
        <>
            <Box sx={MainBoxSx} id={props.id} className={className}>
                <TreeView
                    defaultCollapseIcon={<ExpandMore />}
                    defaultExpandIcon={<ChevronRight />}
                    sx={treeViewSx}
                    onNodeSelect={onSelect}
                    selected={selected}
                >
                    {scenarios
                        ? scenarios.map((item) => {
                              const [id, label, scenarios, nodeType] = item;
                              return displayCycles ? (
                                  nodeType === NodeType.CYCLE ? (
                                      <TreeItem
                                          key={id}
                                          nodeId={id}
                                          label={
                                              <Box sx={treeItemLabelSx}>
                                                  <Cycle fontSize="small" color="primary" />
                                                  {label}
                                              </Box>
                                          }
                                          sx={ParentItemSx}
                                          data-cycle
                                      >
                                          <ScenarioNodes
                                              scenarios={scenarios}
                                              showPrimary={showPrimaryFlag}
                                              openEditDialog={openEditDialog}
                                          />
                                      </TreeItem>
                                  ) : (
                                      <ScenarioNodes
                                          key={id}
                                          scenarios={item as Scenario}
                                          showPrimary={showPrimaryFlag}
                                          openEditDialog={openEditDialog}
                                      />
                                  )
                              ) : nodeType === NodeType.SCENARIO ? (
                                  <ScenarioNodes
                                      key={id}
                                      scenarios={item as Scenario}
                                      showPrimary={showPrimaryFlag}
                                      openEditDialog={openEditDialog}
                                  />
                              ) : (
                                  <ScenarioNodes
                                      key={id}
                                      scenarios={scenarios}
                                      showPrimary={showPrimaryFlag}
                                      openEditDialog={openEditDialog}
                                  />
                              );
                          })
                        : null}
                </TreeView>

                {showAddButton ? (
                    <Button variant="outlined" onClick={onDialogOpen} fullWidth endIcon={<Add />}>
                        Add scenario
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
        </>
    );
};

export default ScenarioSelector;
