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

import React from "react";
import { useEffect, useState } from "react";
import {
  Box,
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormGroup,
  FormHelperText,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Dialog as MuiDialog,
  Select,
  TextField,
} from "@mui/material";
import { ChevronRight, ExpandMore, Flag, Close } from "@mui/icons-material";
import { TreeItem } from "@mui/lab";
import { Typography } from "@mui/material";
import { useFormik } from "formik";

import {
  LoV,
  useDynamicProperty,
  useDispatch,
  useModule,
  createRequestUpdateAction,
  getUpdateVar,
} from "taipy-gui";
import { LocalizationProvider, DatePicker } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { TreeView } from "@mui/lab";
import { scenarios } from "./data";
import { format } from "date-fns";

export type Scenario = {
  date: string;
  name: string;
  config: string;
};

export type TreeNodeChild = {
  label: string;
  properties?: any[];
  primary?: boolean;
};

export type TreeNode = {
  date: string;
  children: TreeNodeChild[];
};

interface ScenarioSelectorProps {
  defaultShowAddButton: boolean;
  showAddButton?: boolean;
  defaultDisplayCycles: boolean;
  displayCycles?: boolean;
  defaultShowPrimaryFlag: boolean;
  showPrimaryFlag?: boolean;
  scenarios?: LoV;
  defaultScenarios?: LoV;
  defaultScenarioId?: string;
  scenarioId?: string;
  onScenarioCreate?: string;
  coreChanged?: Record<string, unknown>;
  updateVarNames: string;
}

// COMMENTED THIS OUT SINCE WE DONT NEED TO VALIDATE FOR NOW
//
// const scenarioSchema = Yup.object().shape({
//   config: Yup.string()
//     .trim("Cannot include leading and trailing spaces")
//     .required("Config is required."),
//   name: Yup.string()
//     .trim("Cannot include leading and trailing spaces")
//     .required("Name is required."),
//   date: Yup.string().required("Date is required."),
// });

const ScenarioSelector = (props: ScenarioSelectorProps) => {
  const [open, setOpen] = useState(false);
  const [nodes, setNodes] = useState<TreeNode[]>([]);

  const dispatch = useDispatch();
  const module = useModule();

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
  const scenarioId = useDynamicProperty(
    props.scenarioId,
    props.defaultScenarioId,
    ""
  );

  const onAdd = (node: Scenario) => {
    const nodeIndex = nodes.findIndex((item) => item.date === node.date);

    if (nodeIndex > -1) {
      setNodes(
        nodes.map((item, index) =>
          nodeIndex === index
            ? { ...item, children: [...item.children, { label: node.name }] }
            : item
        )
      );
    } else {
      setNodes([
        ...nodes,
        { date: node.date, children: [{ label: node.name }] },
      ]);
    }
  };

  const onSubmit = (values: any) => {
    onAdd(values);
    form.resetForm();
    setOpen(false);
  };

  const form = useFormik({
    initialValues: {
      config: "",
      name: "",
      date: new Date().toString(),
    },
    onSubmit,
  });

  useEffect(() => {
    if (props.coreChanged?.scenario) {
      const updateVar = getUpdateVar(props.updateVarNames, "scenarios");
      updateVar &&
        dispatch(createRequestUpdateAction("", module, [updateVar], true));
    }
  }, [props.coreChanged, props.updateVarNames, module, dispatch]);

  useEffect(() => {
    if (scenarios) {
      let initalNodes: any[] = [];
      for (var s of scenarios) {
        const date = format(new Date(s.creation_date), "yyyy-MM-dd");
        const nodeDate = initalNodes.find((n) => n.date === date);

        const childrenObj = {
          label: s.id,
          primary: s.primary_scenario,
          version: s.version,
          properties: s.properties,
        };

        if (nodeDate) {
          nodeDate.children.push(childrenObj);
        } else {
          let parent = {
            date: date,
            children: [childrenObj],
          };
          initalNodes.push(parent);
        }
      }
      setNodes(initalNodes);
    }
  }, []);

  return (
    <div>
      <Box>
        <Typography variant="h5" gutterBottom>
          Scenarios
        </Typography>
        <TreeView
          defaultCollapseIcon={<ExpandMore />}
          defaultExpandIcon={<ChevronRight />}
          sx={{
            mb: 2,
            maxWidth: 400,
            overflowY: "auto",
          }}
        >
          {nodes.map((item) => (
            <TreeItem
              key={item.date}
              nodeId={item.date}
              label={`Cycle ${format(new Date(item.date), "yyyy-MM-dd")}`}
            >
              {item.children.map((child, index) => (
                <TreeItem
                  key={item.date + index}
                  nodeId={item.date + index.toString()}
                  label={
                    <Grid
                      container
                      alignItems="center"
                      direction="row"
                      flexWrap="nowrap"
                      justifyContent="space-between"
                      spacing={1}
                    >
                      <Grid item>{child.label}</Grid>
                      {child.primary && (
                        <Grid item>
                          <Flag />
                        </Grid>
                      )}
                    </Grid>
                  }
                />
              ))}
            </TreeItem>
          ))}
        </TreeView>

        <Button variant="outlined" color="error" onClick={() => setOpen(true)}>
          Add
        </Button>
      </Box>

      <MuiDialog onClose={() => setOpen(false)} open={open}>
        <DialogTitle>
          <Grid
            container
            direction="row"
            justifyContent="space-between"
            alignItems="center"
          >
            Create new scenario
            <IconButton
              aria-label="close"
              onClick={() => setOpen(false)}
              sx={{ p: 0 }}
            >
              <Close />
            </IconButton>
          </Grid>
        </DialogTitle>
        <form onSubmit={form.handleSubmit}>
          <DialogContent
            sx={{
              width: "500px",
            }}
            dividers
          >
            <Grid container rowSpacing={2}>
              <Grid item xs={12}>
                <FormGroup>
                  <InputLabel id="select-config">config:</InputLabel>
                  <Select
                    id="select-config"
                    label="Config:"
                    {...form.getFieldProps("config")}
                    error={!!form.errors.config && form.touched.config}
                  >
                    <MenuItem value={1}>config_test_1</MenuItem>
                    <MenuItem value={2}>config_test_2</MenuItem>
                    <MenuItem value={3}>config_test_3</MenuItem>
                  </Select>
                  <FormHelperText
                    error={!!form.errors.config && form.touched.config}
                    sx={{ pl: 12 }}
                  >
                    {form.errors.config}
                  </FormHelperText>
                </FormGroup>
              </Grid>
              <Grid item xs={12}>
                <FormGroup>
                  <InputLabel id="name">name:</InputLabel>
                  <TextField
                    id="name"
                    {...form.getFieldProps("name")}
                    error={!!form.errors.name && form.touched.name}
                    helperText={form.errors.name}
                  />
                </FormGroup>
              </Grid>
              <Grid item xs={12}>
                <FormGroup>
                  <InputLabel id="date">date:</InputLabel>
                  <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <DatePicker
                      value={new Date(form.values.date)}
                      onChange={(date) =>
                        form.setFieldValue("date", date?.toString())
                      }
                    />
                  </LocalizationProvider>
                </FormGroup>
              </Grid>
            </Grid>
          </DialogContent>

          <DialogActions>
            <Button variant="outlined" color="error" type="submit">
              Add Scenario
            </Button>
            <Button
              variant="outlined"
              color="error"
              onClick={() => setOpen(false)}
            >
              Cancel
            </Button>
          </DialogActions>
        </form>
      </MuiDialog>
    </div>
  );
};

export default ScenarioSelector;
