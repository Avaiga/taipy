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

import React, { useState, useCallback, useEffect } from "react";
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
  FlagOutlined,
  Close,
  DeleteOutline,
  Add,
  Send,
  CheckCircle,
  Cancel,
  ArrowForwardIosSharp,
} from "@mui/icons-material";

import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  AccordionSummaryProps,
  Autocomplete,
  Chip,
  Divider,
  styled,
} from "@mui/material";
import { FlagSx, Property, ScenarioFull } from "./utils";

interface ScenarioViewerProps {
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
  scenario?: ScenarioFull;
  onSubmit: string;
  error?: string;
}

interface PipelinesRowProps {
  action: string;
  number: number;
  value: string;
}

const MainBoxSx = {
  overflowY: "auto",
};

const FieldNoMaxWidth = {
  maxWidth: "none",
};

const AccordionSummarySx = { fontSize: "0.9rem" };
const IconButtonSx = { p: 0 };
const ChipSx = { ml: 1 };
const IconPaddingSx = { padding: 0 };
const DeleteIconSx = { height: 50, width: 50, p: 0 };

const tagsAutocompleteSx = {
  "& .MuiOutlinedInput-root": {
    padding: "3px 15px 3px 3px !important",
  },
  maxWidth: "none",
};

const PipelineRow = ({ action, number, value }: PipelinesRowProps) => {
  const [pipeline, setPipeline] = useState<string>(value);
  const [focus, setFocus] = useState(false);

  const onFieldBlur = useCallback((e: any) => {
    setPipeline(e.target.value);
    setFocus(false);
  }, []);

  const index = number + 1;
  return (
    <Grid item xs={12} container justifyContent="space-between">
      <Grid item container xs={10}>
        {action === "EDIT" && (
          <TextField
            data-name={`pipe${index}`}
            label={"Pipeline " + index}
            variant="outlined"
            name={`pipeline${index}`}
            value={pipeline}
            onBlur={onFieldBlur}
            sx={FieldNoMaxWidth}
            onFocus={(e) => setFocus(true)}
            fullWidth
            InputProps={{
              endAdornment: focus && (
                <>
                  <IconButton sx={IconPaddingSx}>
                    <CheckCircle color="primary" />
                  </IconButton>
                  <IconButton sx={IconPaddingSx}>
                    <Cancel color="inherit" />
                  </IconButton>
                </>
              ),
            }}
          />
        )}
        {action !== "EDIT" && (
          <Typography variant="subtitle2">{pipeline}</Typography>
        )}
      </Grid>
      <Grid
        item
        xs={2}
        container
        alignContent="center"
        alignItems="center"
        justifyContent="center"
      >
        <IconButton component="label" size="small">
          <Send color="info" />
        </IconButton>
      </Grid>
    </Grid>
  );
};

const ScenarioViewer = (props: ScenarioViewerProps) => {
  const {
    id = "",
    scenario = [
      "test12",
      true,
      "test",
      "test",
      "test",
      ["tags"],
      [["key", "value"]],
      [["key", "value"]],
      ["test123"],
    ],
  } = props;

  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [properties, setProperties] = useState<Property[]>([]);
  const [action, setAction] = useState<string>("EDIT");
  const [tags, setTags] = useState<string[]>();
  const [newProp, setNewProp] = useState<Property>({
    id: "",
    key: "",
    value: "",
  });
  const [label, setLabel] = useState<string>();

  const [labelFocus, setLabelFocus] = useState(false);
  const [tagsFocus, setTagsFocus] = useState(false);

  const sendScenario = useCallback((e: React.MouseEvent<HTMLElement>) => {},
  []);

  const updateScenario = useCallback((e: React.MouseEvent<HTMLElement>) => {},
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

  const onLabelChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setLabel(e.target.value);
    },
    []
  );

  const MuiAccordionSummary = styled((props: AccordionSummaryProps) => (
    <AccordionSummary
      expandIcon={<ArrowForwardIosSharp sx={AccordionSummarySx} />}
      {...props}
    />
  ))(({ theme }) => ({
    flexDirection: "row-reverse",
    "& .MuiAccordionSummary-expandIconWrapper.Mui-expanded": {
      transform: "rotate(90deg)",
      marginRight: theme.spacing(1),
    },
    "& .MuiAccordionSummary-content": {
      marginLeft: theme.spacing(1),
    },
  }));

  const [
    scenarioId,
    primary,
    config,
    date,
    scenarioLabel,
    scenarioTags,
    scenarioProperties,
    pipelines,
    authorizedTags,
  ] = scenario;

  useEffect(() => {
    setTags(scenario ? scenarioTags : []);
    setProperties(
      scenario
        ? scenarioProperties.map(([k, v], i) => ({
            id: i + "",
            key: k,
            value: v,
          }))
        : []
    );
  }, []);

  return (
    <div>
      <Box sx={MainBoxSx}>
        <Accordion>
          <MuiAccordionSummary id={`panel-${scenarioId}`}>
            <Grid
              container
              alignItems="center"
              direction="row"
              flexWrap="nowrap"
              justifyContent="space-between"
              spacing={1}
            >
              <Grid item>
                {scenarioLabel}
                {primary && (
                  <Chip
                    color="primary"
                    label={<FlagOutlined sx={FlagSx} />}
                    size="small"
                    sx={ChipSx}
                  />
                )}
              </Grid>
              <Grid item>
                <IconButton
                  data-id={scenarioId}
                  sx={IconPaddingSx}
                  onClick={updateScenario}
                >
                  <Send fontSize="small" color="info" />
                </IconButton>
              </Grid>
            </Grid>
          </MuiAccordionSummary>
          <AccordionDetails>
            <Grid container rowSpacing={2}>
              <Grid item xs={12} container justifyContent="space-between">
                <Grid item xs={4} pb={2}>
                  <Typography variant="subtitle2">Config ID</Typography>
                </Grid>
                <Grid item xs={8}>
                  <Typography variant="subtitle2">{config}</Typography>
                </Grid>
              </Grid>
              <Grid item xs={12} container justifyContent="space-between">
                <Grid item xs={4}>
                  <Typography variant="subtitle2">Cycle / Frequency</Typography>
                </Grid>
                <Grid item xs={8}>
                  <Typography variant="subtitle2">
                    Thursday 2023-02-05 / Daily
                  </Typography>
                </Grid>
              </Grid>
              {action === "EDIT" && (
                <Grid item xs={11} container justifyContent="space-between">
                  <TextField
                    label="Label"
                    variant="outlined"
                    fullWidth
                    sx={FieldNoMaxWidth}
                    value={label}
                    onChange={onLabelChange}
                    onFocus={(e) => setLabelFocus(true)}
                    onBlur={(e) => setLabelFocus(false)}
                    InputProps={{
                      endAdornment: labelFocus && (
                        <>
                          <IconButton
                            sx={IconPaddingSx}
                            onClick={() => console.log("1")}
                          >
                            <CheckCircle color="primary" />
                          </IconButton>
                          <IconButton
                            sx={IconPaddingSx}
                            onClick={() => console.log("2")}
                          >
                            <Cancel color="inherit" />
                          </IconButton>
                        </>
                      ),
                    }}
                  />
                </Grid>
              )}
              {action !== "EDIT" && (
                <Grid item xs={12} container justifyContent="space-between">
                  <Grid item xs={4}>
                    <Typography variant="subtitle2">Label</Typography>
                  </Grid>
                  <Grid item xs={8}>
                    <Typography variant="subtitle2">Scenario 3</Typography>
                  </Grid>
                </Grid>
              )}
              {action !== "EDIT" ? (
                <Grid item xs={12} container justifyContent="space-between">
                  <Grid item xs={4}>
                    <Typography variant="subtitle2">Tags</Typography>
                  </Grid>
                  <Grid item xs={8}>
                    {tags &&
                      tags.map((tag, index) => (
                        <Chip key={index} label={tag} variant="outlined" />
                      ))}
                  </Grid>
                </Grid>
              ) : (
                <Grid item xs={11} container justifyContent="space-between">
                  <Autocomplete
                    multiple
                    id="tags-filled"
                    options={[]}
                    freeSolo
                    renderTags={(value: readonly string[], getTagProps) =>
                      value.map((option: string, index: number) => (
                        <Chip
                          variant="outlined"
                          label={option}
                          sx={IconPaddingSx}
                          {...getTagProps({ index })}
                        />
                      ))
                    }
                    onFocus={(e) => setTagsFocus(true)}
                    onBlur={(e) => setTagsFocus(false)}
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
                          endAdornment: tagsFocus && (
                            <>
                              <IconButton sx={IconPaddingSx}>
                                <CheckCircle color="primary" />
                              </IconButton>
                              <IconButton sx={IconPaddingSx}>
                                <Cancel color="inherit" />
                              </IconButton>
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
              <Grid item xs={12} container justifyContent="space-between">
                <Typography variant="h6">Custom Properties</Typography>
              </Grid>
              {scenarioProperties
                ? scenarioProperties.map((item, index) => {
                    const [key, value] = item;
                    return (
                      <Grid
                        item
                        xs={12}
                        spacing={1}
                        container
                        justifyContent="space-between"
                      >
                        <Grid item xs={5}>
                          {action !== "EDIT" ? (
                            <Typography variant="subtitle2">{key}</Typography>
                          ) : (
                            <TextField
                              label="Key"
                              variant="outlined"
                              value={key}
                              sx={FieldNoMaxWidth}
                            />
                          )}
                        </Grid>
                        <Grid item xs={5}>
                          {action !== "EDIT" ? (
                            <Typography variant="subtitle2">{value}</Typography>
                          ) : (
                            <TextField
                              label="Value"
                              variant="outlined"
                              value={value}
                              sx={FieldNoMaxWidth}
                            />
                          )}
                        </Grid>
                        <Grid
                          item
                          xs={2}
                          container
                          alignContent="center"
                          alignItems="center"
                          justifyContent="center"
                        >
                          {action !== "VIEW" && (
                            <IconButton
                              sx={DeleteIconSx}
                              data-id={index}
                              onClick={propertyDelete}
                            >
                              <DeleteOutline fontSize="small" color="primary" />
                            </IconButton>
                          )}
                        </Grid>
                      </Grid>
                    );
                  })
                : null}
              {action !== "VIEW" && (
                <Grid
                  item
                  xs={12}
                  spacing={1}
                  container
                  justifyContent="space-between"
                >
                  <Grid item xs={5}>
                    <TextField
                      value={newProp.key}
                      data-name="key"
                      onChange={updatePropertyField}
                      label="Key"
                      variant="outlined"
                      sx={FieldNoMaxWidth}
                    />
                  </Grid>
                  <Grid item xs={5}>
                    <TextField
                      value={newProp.value}
                      data-name="value"
                      onChange={updatePropertyField}
                      label="Value"
                      variant="outlined"
                      sx={FieldNoMaxWidth}
                    />
                  </Grid>
                  <Grid
                    item
                    xs={2}
                    container
                    alignContent="center"
                    alignItems="center"
                    justifyContent="center"
                  >
                    <IconButton
                      onClick={propertyAdd}
                      disabled={!newProp.key || !newProp.value}
                    >
                      <Add color="primary" />
                    </IconButton>
                  </Grid>
                </Grid>
              )}

              <Grid item xs={12}>
                <Divider />
              </Grid>

              <Grid item xs={12} container justifyContent="space-between">
                <Typography variant="h6">Pipelines</Typography>
              </Grid>

              {pipelines &&
                pipelines.map((item, index) => {
                  const [key, value] = item;
                  return (
                    <PipelineRow
                      action={action}
                      number={index}
                      value={value}
                      key={key}
                    />
                  );
                })}

              <Grid item xs={12}>
                <Divider />
              </Grid>
              <Grid item xs={12} container justifyContent="space-between">
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
          </AccordionDetails>
        </Accordion>
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
export default ScenarioViewer;
