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

import { TaipyBaseProps } from "../components/Taipy/utils";
import { stringIcon } from "./icon";

/**
 * An item in a List of Values (LoV).
 */
export interface LovItem {
    /** The unique identifier of this item. */
    id: string;
    /** The items label (string and/or icon). */
    item: stringIcon;
    /** The array of child items. */
    children?: LovItem[];
}

export interface MenuProps extends TaipyBaseProps {
    label?: string;
    width?: string;
    onAction?: string;
    inactiveIds?: string[];
    lov?: LovItem[];
    active?: boolean;
}
