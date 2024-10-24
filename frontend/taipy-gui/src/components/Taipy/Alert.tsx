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

import React from "react";
import Alert from "@mui/material/Alert";
import { TaipyBaseProps } from "./utils";
import { useClassNames, useDynamicProperty } from "../../utils/hooks";

interface AlertProps extends TaipyBaseProps {
    severity?: "error" | "warning" | "info" | "success";
    message?: string;
    variant?: "filled" | "outlined";
    render?: boolean;
    defaultMessage?: string;
    defaultSeverity?: string;
    defaultVariant?: string;
    defaultRender?: boolean;
}

const TaipyAlert = (props: AlertProps) => {
    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const render = useDynamicProperty(props.render, props.defaultRender, true);
    const severity = useDynamicProperty(props.severity, props.defaultSeverity, "error") as
        | "error"
        | "warning"
        | "info"
        | "success";
    const variant = useDynamicProperty(props.variant, props.defaultVariant, "filled") as "filled" | "outlined";
    const message = useDynamicProperty(props.message, props.defaultMessage, "");

    if (!render) return null;

    return (
        <Alert severity={severity} variant={variant} id={props.id} className={className}>
            {message}
        </Alert>
    );
};

export default TaipyAlert;
