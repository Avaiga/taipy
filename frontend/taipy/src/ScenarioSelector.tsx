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

import React, { useEffect, useState, useCallback, useMemo } from "react";
import { Theme, Tooltip, alpha } from "@mui/material";

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
import { Close, DeleteOutline, Add, EditOutlined } from "@mui/icons-material";
import { LocalizationProvider, DatePicker } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { useFormik } from "formik";

import {
    useDispatch,
    useModule,
    createSendActionNameAction,
    getUpdateVar,
    createSendUpdateAction,
    TableFilter,
    ColumnDesc,
    FilterDesc,
    useDynamicProperty,
    createRequestUpdateAction,
} from "taipy-gui";

import ConfirmDialog from "./utils/ConfirmDialog";
import { MainTreeBoxSx, ScFProps, ScenarioFull, useClassNames, tinyIconButtonSx, getUpdateVarNames } from "./utils";
import CoreSelector, { EditProps } from "./CoreSelector";
import { Cycles, NodeType, Scenarios } from "./utils/types";

type Property = {
    id: string;
    key: string;
    value: string;
};

// type Scenario = [string, string, undefined, number, boolean];
// type Scenarios = Array<Scenario>;
// type Cycles = Array<[string, string, Scenarios, number, boolean]>;

interface ScenarioDict {
    id?: string;
    config: string;
    name: string;
    date: string;
    properties: Array<Property>;
}

interface ScenarioSelectorProps {
    id?: string;
    active?: boolean;
    defaultActive?: boolean;
    showAddButton?: boolean;
    displayCycles?: boolean;
    showPrimaryFlag?: boolean;
    updateVarName?: string;
    updateVars: string;
    innerScenarios?: Cycles | Scenarios;
    onScenarioCrud: string;
    onChange?: string;
    onCreation?: string;
    coreChanged?: Record<string, unknown>;
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
    showPins?: boolean;
    showDialog?: boolean;
    multiple?: boolean;
    filterBy?: string;
    updateScVars?: string;
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

const ActionContentSx = { mr: 2, ml: 2 };

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
    }, [scenario, configs]);

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
                        <Tooltip title="close">
                            <IconButton onClick={close} sx={IconButtonSx}>
                                <Close />
                            </IconButton>
                        </Tooltip>
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
                                            onChange={(date?: Date | null) =>
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
                                      <Grid item xs={12} key={item.id} container spacing={1} alignItems="end">
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
                                              <Tooltip title="Delete Property">
                                                  <Button
                                                      variant="outlined"
                                                      color="inherit"
                                                      data-id={item.id}
                                                      onClick={propertyDelete}
                                                      sx={SquareButtonSx}
                                                  >
                                                      <DeleteOutline />
                                                  </Button>
                                              </Tooltip>
                                          </Grid>
                                      </Grid>
                                  ))
                                : null}
                            <Grid item xs={12} container spacing={1} justifyContent="space-between" alignItems="end">
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
                                    <Tooltip title="Add Property">
                                        <span>
                                            <Button
                                                variant="outlined"
                                                onClick={propertyAdd}
                                                disabled={!newProp.key || !newProp.value}
                                                sx={SquareButtonSx}
                                            >
                                                <Add />
                                            </Button>
                                        </span>
                                    </Tooltip>
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
    const {
        showAddButton = true,
        propagate = true,
        showPins = false,
        showDialog = true,
        multiple = false,
        updateVars = "",
        updateScVars = "",
    } = props;
    const [open, setOpen] = useState(false);
    const [actionEdit, setActionEdit] = useState<boolean>(false);

    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);

    const dispatch = useDispatch();
    const module = useModule();

    const colFilters = useMemo(() => {
        try {
            const res = props.filterBy ? (JSON.parse(props.filterBy) as Array<[string, string]>) : undefined;
            return Array.isArray(res)
                ? res.reduce((pv, [name, coltype], idx) => {
                      pv[name] = { dfid: name, type: coltype, index: idx, filter: true };
                      return pv;
                  }, {} as Record<string, ColumnDesc>)
                : undefined;
        } catch (e) {
            return undefined;
        }
    }, [props.filterBy]);
    const [filters, setFilters] = useState<FilterDesc[]>([]);

    const applyFilters = useCallback(
        (filters: FilterDesc[]) => {
            setFilters((old) => {
                if (old.length != filters.length || JSON.stringify(old) != JSON.stringify(filters)) {
                    const filterVar = getUpdateVar(updateScVars, "filter");
                    dispatch(
                        createRequestUpdateAction(
                            props.id,
                            module,
                            getUpdateVarNames(updateVars, "innerScenarios"),
                            true,
                            filterVar ? { [filterVar]: filters } : undefined
                        )
                    );
                    return filters;
                }
                return old;
            });
        },
        [updateVars, dispatch, props.id, updateScVars, module]
    );

    const onSubmit = useCallback(
        (...values: unknown[]) => {
            dispatch(
                createSendActionNameAction(
                    props.id,
                    module,
                    { action: props.onScenarioCrud, error_id: getUpdateVar(updateScVars, "error_id") },
                    props.onCreation,
                    props.updateVarName,
                    ...values
                )
            );
            if (values.length > 1 && values[1]) {
                // delete requested => unselect current node
                const lovVar = getUpdateVar(updateVars, "innerScenarios");
                dispatch(
                    createSendUpdateAction(props.updateVarName, undefined, module, props.onChange, propagate, lovVar)
                );
            }
        },
        [
            props.id,
            props.onScenarioCrud,
            dispatch,
            module,
            propagate,
            props.onChange,
            props.updateVarName,
            updateVars,
            props.onCreation,
            updateScVars,
        ]
    );

    const onDialogOpen = useCallback(() => {
        if (showDialog) {
            setOpen(true);
            setActionEdit(false);
        } else {
            onSubmit(false, false, {}, false);
        }
    }, [showDialog, onSubmit]);

    const onDialogClose = useCallback(() => {
        setOpen(false);
        setActionEdit(false);
    }, []);

    const openEditDialog = useCallback(
        (e: React.MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            const { id: scenId } = e.currentTarget?.dataset || {};
            const varName = getUpdateVar(updateScVars, "sc_id");
            scenId &&
                props.onScenarioSelect &&
                dispatch(createSendActionNameAction(props.id, module, props.onScenarioSelect, varName, scenId));
            setOpen(true);
            setActionEdit(true);
        },
        [props.onScenarioSelect, props.id, dispatch, module, updateScVars]
    );

    const EditScenario = useCallback(
        (props: EditProps) => (
            <Tooltip title="Edit Scenario">
                <IconButton
                    data-id={props.id}
                    onClick={openEditDialog}
                    sx={tinyEditIconButtonSx}
                    disabled={props.active}
                >
                    <EditOutlined />
                </IconButton>
            </Tooltip>
        ),
        [openEditDialog]
    );

    return (
        <>
            <Box sx={MainTreeBoxSx} id={props.id} className={className}>
                {active && colFilters ? (
                    <TableFilter
                        columns={colFilters}
                        appliedFilters={filters}
                        filteredCount={0}
                        onValidate={applyFilters}
                    ></TableFilter>
                ) : null}
                <CoreSelector
                    {...props}
                    entities={props.innerScenarios}
                    leafType={NodeType.SCENARIO}
                    lovPropertyName="innerScenarios"
                    editComponent={EditScenario}
                    showPins={showPins}
                    multiple={multiple}
                />
                {showAddButton ? (
                    <Button variant="outlined" onClick={onDialogOpen} fullWidth endIcon={<Add />} disabled={!active}>
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
