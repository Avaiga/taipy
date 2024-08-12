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

import React, { useState, useCallback, useEffect, ChangeEvent, MouseEvent, KeyboardEvent } from "react";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import { DeleteOutline, CheckCircle, Cancel } from "@mui/icons-material";

import { createSendActionNameAction, getUpdateVar, useDispatch, useModule } from "taipy-gui";

import { DeleteIconSx, FieldNoMaxWidth, IconPaddingSx, disableColor, hoverSx } from "./utils";

type Property = {
    id: string;
    key: string;
    value: string;
};

type PropertiesEditPayload = {
    id: string;
    properties?: Property[];
    deleted_properties?: Array<Partial<Property>>;
    error_id?: string;
};

export type DatanodeProperties = Array<[string, string]>;

interface PropertiesEditorProps {
    id?: string;
    entityId: string;
    active: boolean;
    show: boolean;
    entProperties: DatanodeProperties;
    onFocus: (e: MouseEvent<HTMLElement>) => void;
    focusName: string;
    setFocusName: (name: string) => void;
    isDefined: boolean;
    onEdit?: string;
    notEditableReason: string;
    updatePropVars?: string;
}

const PropertiesEditor = (props: PropertiesEditorProps) => {
    const {
        id,
        entityId,
        isDefined,
        show,
        active,
        onFocus,
        focusName,
        setFocusName,
        entProperties,
        notEditableReason,
        updatePropVars = "",
    } = props;

    const dispatch = useDispatch();
    const module = useModule();

    const [properties, setProperties] = useState<Property[]>([]);
    const [newProp, setNewProp] = useState<Property>({
        id: "",
        key: "",
        value: "",
    });

    // Properties
    const updatePropertyField = useCallback((e: ChangeEvent<HTMLInputElement>) => {
        const { id = "", name = "" } = e.currentTarget.parentElement?.parentElement?.dataset || {};
        if (name) {
            if (id) {
                setProperties((ps) => ps.map((p) => (id === p.id ? { ...p, [name]: e.target.value } : p)));
            } else {
                setNewProp((np) => ({ ...np, [name]: e.target.value }));
            }
        }
    }, []);

    const editProperty = useCallback(
        (e?: MouseEvent<HTMLElement>, dataset?: DOMStringMap) => {
            e && e.stopPropagation();
            if (isDefined) {
                const { id: propId = "" } = dataset || e?.currentTarget.dataset || {};
                const property = propId ? properties.find((p) => p.id === propId) : newProp;
                if (property) {
                    const oldId = property.id;
                    const payload: PropertiesEditPayload = {
                        id: entityId,
                        properties: [property],
                        error_id: getUpdateVar(updatePropVars, "error_id"),
                    };
                    if (oldId && oldId != property.key) {
                        payload.deleted_properties = [{ key: oldId }];
                    }
                    dispatch(createSendActionNameAction(id, module, props.onEdit, payload));
                }
                setNewProp((np) => ({ ...np, key: "", value: "" }));
                setFocusName("");
            }
        },
        [isDefined, props.onEdit, entityId, properties, newProp, id, dispatch, module, setFocusName, updatePropVars]
    );
    const cancelProperty = useCallback(
        (e?: MouseEvent<HTMLElement>, dataset?: DOMStringMap) => {
            e && e.stopPropagation();
            if (isDefined) {
                const { id: propId = "" } = dataset || e?.currentTarget.dataset || {};
                const property = entProperties.find(([key]) => key === propId);
                property &&
                    setProperties((ps) =>
                        ps.map((p) => (p.id === property[0] ? { ...p, key: property[0], value: property[1] } : p))
                    );
                setFocusName("");
            }
        },
        [isDefined, entProperties, setFocusName]
    );

    const onKeyDown = useCallback(
        (e: KeyboardEvent<HTMLInputElement>) => {
            if (!e.shiftKey && !e.ctrlKey && !e.altKey) {
                if (e.key == "Enter" && e.currentTarget.dataset.enter) {
                    editProperty(undefined, e.currentTarget.parentElement?.parentElement?.dataset);
                    e.preventDefault();
                    e.stopPropagation();
                } else if (e.key == "Escape") {
                    cancelProperty(undefined, e.currentTarget.parentElement?.parentElement?.dataset);
                    e.preventDefault();
                    e.stopPropagation();
                }
            }
        },
        [editProperty, cancelProperty]
    );

    const deleteProperty = useCallback(
        (e: React.MouseEvent<HTMLElement>) => {
            e.stopPropagation();
            const { id: propId = "" } = e.currentTarget.dataset;
            setProperties((ps) => ps.filter((item) => item.id !== propId));
            const property = properties.find((p) => p.id === propId);
            property &&
                dispatch(
                    createSendActionNameAction(id, module, props.onEdit, {
                        id: entityId,
                        deleted_properties: [property],
                    })
                );
            setFocusName("");
        },
        [props.onEdit, entityId, id, dispatch, module, properties, setFocusName]
    );

    useEffect(() => {
        show &&
            setProperties(
                entProperties.map(([k, v]) => ({
                    id: k,
                    key: k,
                    value: v,
                }))
            );
    }, [show, entProperties]);

    return show ? (
        <>
            <Grid item xs={12} container rowSpacing={2}>
                {properties
                    ? properties.map((property) => {
                          const propName = `property-${property.id}`;
                          return (
                              <Grid
                                  item
                                  xs={12}
                                  spacing={1}
                                  container
                                  justifyContent="space-between"
                                  key={property.id}
                                  data-focus={propName}
                                  onClick={onFocus}
                                  sx={hoverSx}
                              >
                                  {active && !notEditableReason && focusName === propName ? (
                                      <>
                                          <Grid item xs={4}>
                                              <TextField
                                                  label="Key"
                                                  variant="outlined"
                                                  value={property.key}
                                                  sx={FieldNoMaxWidth}
                                                  disabled={!isDefined}
                                                  data-name="key"
                                                  data-id={property.id}
                                                  onChange={updatePropertyField}
                                                  inputProps={{ onKeyDown }}
                                              />
                                          </Grid>
                                          <Grid item xs={5}>
                                              <TextField
                                                  label="Value"
                                                  variant="outlined"
                                                  value={property.value}
                                                  sx={FieldNoMaxWidth}
                                                  disabled={!isDefined}
                                                  data-name="value"
                                                  data-id={property.id}
                                                  onChange={updatePropertyField}
                                                  inputProps={{ onKeyDown, "data-enter": true }}
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
                                              <Tooltip title="Apply">
                                                  <IconButton
                                                      sx={IconPaddingSx}
                                                      data-id={property.id}
                                                      onClick={editProperty}
                                                      size="small"
                                                  >
                                                      <CheckCircle color="primary" />
                                                  </IconButton>
                                              </Tooltip>
                                              <Tooltip title="Cancel">
                                                  <IconButton
                                                      sx={IconPaddingSx}
                                                      data-id={property.id}
                                                      onClick={cancelProperty}
                                                      size="small"
                                                  >
                                                      <Cancel color="inherit" />
                                                  </IconButton>
                                              </Tooltip>
                                          </Grid>
                                          <Grid
                                              item
                                              xs={1}
                                              container
                                              alignContent="center"
                                              alignItems="center"
                                              justifyContent="center"
                                          >
                                              <Tooltip title="Delete property">
                                                  <span>
                                                      <IconButton
                                                          sx={DeleteIconSx}
                                                          data-id={property.id}
                                                          onClick={deleteProperty}
                                                          disabled={!isDefined}
                                                      >
                                                          <DeleteOutline
                                                              fontSize="small"
                                                              color={disableColor("primary", !isDefined)}
                                                          />
                                                      </IconButton>
                                                  </span>
                                              </Tooltip>
                                          </Grid>
                                      </>
                                  ) : (
                                      <>
                                          <Grid item xs={4}>
                                              <Typography variant="subtitle2">{property.key}</Typography>
                                          </Grid>
                                          <Grid item xs={5}>
                                              <Typography variant="subtitle2">{property.value}</Typography>
                                          </Grid>
                                          <Grid item xs={3} />
                                      </>
                                  )}
                              </Grid>
                          );
                      })
                    : null}
                <Grid
                    item
                    xs={12}
                    spacing={1}
                    container
                    justifyContent="space-between"
                    data-focus="new-property"
                    onClick={onFocus}
                    sx={hoverSx}
                >
                    {active && focusName == "new-property" ? (
                        <>
                            <Grid item xs={4}>
                                <TextField
                                    value={newProp.key}
                                    data-name="key"
                                    onChange={updatePropertyField}
                                    label="Key"
                                    variant="outlined"
                                    sx={FieldNoMaxWidth}
                                    disabled={!isDefined}
                                    inputProps={{ onKeyDown }}
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
                                    disabled={!isDefined}
                                    inputProps={{ onKeyDown, "data-enter": true }}
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
                                <Tooltip title="Apply">
                                    <IconButton sx={IconPaddingSx} onClick={editProperty} size="small">
                                        <CheckCircle color="primary" />
                                    </IconButton>
                                </Tooltip>
                                <Tooltip title="Cancel">
                                    <IconButton sx={IconPaddingSx} onClick={cancelProperty} size="small">
                                        <Cancel color="inherit" />
                                    </IconButton>
                                </Tooltip>
                            </Grid>
                            <Grid item xs={1} />
                        </>
                    ) : (
                        <>
                            <Grid item xs={4}>
                                <Typography variant="subtitle2">New Property Key</Typography>
                            </Grid>
                            <Grid item xs={5}>
                                <Typography variant="subtitle2">Value</Typography>
                            </Grid>
                            <Grid item xs={3} />
                        </>
                    )}
                </Grid>
            </Grid>
            <Grid item xs={12}>
                <Divider />
            </Grid>
        </>
    ) : null;
};

export default PropertiesEditor;
