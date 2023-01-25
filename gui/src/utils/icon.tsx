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
import Avatar from "@mui/material/Avatar";

/**
 * An Icon representation.
 */
export interface Icon {
    /** The URL to the image. */
    path: string;
    /** The text. */
    text: string;
}

/**
 * A string or an icon.
 */
export type stringIcon = string | Icon;

interface IconProps {
    id?: string;
    img: Icon
    className?: string;
}

export const IconAvatar = ({id, img, className}:IconProps) => <Avatar alt={img.text || id} src={img.path} className={className} />
