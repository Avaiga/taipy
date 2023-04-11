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
  ThemeProvider as MuiThemeProvider,
  Select,
  TextField,
  createTheme,
} from "@mui/material";
import { ThemeProvider as StyledThemeProvider } from "styled-components";
import { ChevronRight, ExpandMore, Flag, Close } from "@mui/icons-material";
import TreeItem from "@mui/lab/TreeItem";
import { Typography } from "@mui/material";
import dayjs from "dayjs";
import { useFormik } from "formik";

import {
  LoV,
  useDynamicProperty,
  useDispatch,
  useModule,
  createRequestUpdateAction,
  getUpdateVar,
} from "taipy-gui";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { DatePicker as MuiDatePicker } from "@mui/x-date-pickers/DatePicker";
import MuiTreeView from "@mui/lab/TreeView";
import * as Yup from "yup";
import { InferType } from "yup";

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

const scenarioSchema = Yup.object().shape({
  config: Yup.string()
    .trim("Cannot include leading and trailing spaces")
    .required("Config is required."),
  name: Yup.string()
    .trim("Cannot include leading and trailing spaces")
    .required("Name is required."),
  date: Yup.string().required("Date is required."),
});

const ScenarioSelector = (props: ScenarioSelectorProps) => {
  const {} = props;

  const [open, setOpen] = useState(false);
  const [nodes, setNodes] = useState<TreeNode[]>([]);

  const dispatch = useDispatch();
  const module = useModule();

  const theme = createTheme({
    spacing: 1,
    palette: {
      mode: "dark",
    },
  });

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

  //mock data
  const scenarios = [
    {
      cycle: "CYCLE_863418_fdd1499a-8925-4540-93fd-9dbfb4f0846d",
      id: "SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c",
      properties: {},
      tags: [],
      version: "latest",
      pipelines: [
        "PIPELINE_mean_baseline_5af317c9-34df-48b4-8a8a-bf4007e1de99",
        "PIPELINE_arima_90aef6b9-8922-4a0c-b625-b2c6f3d19fa4",
      ],
      subscribers: [],
      creation_date: "2022-08-15T19:21:01.871587",
      primary_scenario: true,
    },
    {
      cycle: "CYCLE_863418_fdd1499a-8925-4540-93fd-9dbfb4f0846d",
      id: "SCENARIO_2222222222263cb358d-5834-4d73-84e4-a6343df5e08c",
      properties: {},
      tags: [],
      version: "latest",
      pipelines: [
        "PIPELINE_mean_baseline_5af317c9-34df-48b4-8a8a-bf4007e1de99",
        "PIPELINE_arima_90aef6b9-8922-4a0c-b625-b2c6f3d19fa4",
      ],
      subscribers: [],
      creation_date: "2022-08-15T19:21:01.871587",
      primary_scenario: false,
    },
    {
      cycle: "CYCLE_863418_fdd1499a-8925-4540-93fd-9dbfb4f0846d",
      id: "SCENARIO_333333333333333363cb358d-5834-4d73-84e4-a6343df5e08c",
      properties: {},
      tags: [],
      version: "latest",
      pipelines: [
        "PIPELINE_mean_baseline_5af317c9-34df-48b4-8a8a-bf4007e1de99",
        "PIPELINE_arima_90aef6b9-8922-4a0c-b625-b2c6f3d19fa4",
      ],
      subscribers: [],
      creation_date: "2022-08-16T19:21:01.871587",
      primary_scenario: true,
    },
  ];

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

  const onSubmit = (values: InferType<typeof scenarioSchema>) => {
    onAdd(values);
    form.resetForm();
    setOpen(false);
  };

  const form = useFormik({
    initialValues: {
      config: "",
      name: "",
      date: dayjs().toString(),
    },
    validationSchema: scenarioSchema,
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
        const date = dayjs(s.creation_date).format("YYYY-MM-DD");
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
    <MuiThemeProvider theme={theme}>
      <StyledThemeProvider theme={theme}>
        <div>
          <Box>
            <Typography variant="h5" gutterBottom>
              Scenarios
            </Typography>
            <MuiTreeView
              defaultCollapseIcon={<ExpandMore />}
              defaultExpandIcon={<ChevronRight />}
              sx={{
                mb: 20,
                maxWidth: 400,
                overflowY: "auto",
              }}
            >
              {nodes.map((item) => (
                <TreeItem
                  key={item.date}
                  nodeId={item.date}
                  label={`Cycle ${dayjs(item.date).format("YYYY-MM-DD")}`}
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
            </MuiTreeView>

            <Button
              variant="outlined"
              color="error"
              onClick={() => setOpen(true)}
            >
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
                <Grid container rowSpacing={20}>
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
                      <LocalizationProvider
                        id="date"
                        dateAdapter={AdapterDayjs}
                      >
                        <MuiDatePicker
                          value={dayjs(form.values.date)}
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
      </StyledThemeProvider>
    </MuiThemeProvider>
  );
};

export default ScenarioSelector;
