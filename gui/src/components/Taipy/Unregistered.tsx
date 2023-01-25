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

interface UnregisteredProps {
    tagName?: string;
    error?: string;
}

const Unregistered = ({ tagName, error }: UnregisteredProps) =>
    tagName ? <div>Component {tagName} is not registered</div> : <div>An Error occurred: {error}</div>;

export const unregisteredRender = (tagName?: string, error?: string) => (
    <Unregistered tagName={tagName} error={error} />
);

export const renderError = (props: { error: string }) => unregisteredRender(undefined, props.error);
