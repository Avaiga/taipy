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
import SvgIcon, { SvgIconProps } from "@mui/material/SvgIcon";

export const MatchCase = (props: SvgIconProps) => (
    <SvgIcon {...props} viewBox="0 0 16 16">
        <g stroke="currentColor">
            <path d="M20 14c0-1.5-.5-2-2-2h-2v-1c0-1 0-1-2-1v9h4c1.5 0 2-.53 2-2zm-8-2c0-1.5-.53-2-2-2H6c-1.5 0-2 .5-2 2v7h2v-3h4v3h2zm-2-5h4V5h-4zm12 2v11c0 1.11-.89 2-2 2H4a2 2 0 0 1-2-2V9c0-1.11.89-2 2-2h4V5l2-2h4l2 2v2h4a2 2 0 0 1 2 2m-6 8h2v-3h-2zM6 12h4v2H6z" />
        </g>
    </SvgIcon>
);
