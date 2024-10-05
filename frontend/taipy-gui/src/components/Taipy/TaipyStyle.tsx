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

import React, { ReactNode } from "react";
import { Helmet } from "react-helmet-async";

interface TaipyStyleProps {
    className: string;
    content: string;
}

/**
 * A function that retrieves the dynamic className associated
 * to an instance of component through the style property
 *
 * @param children - The react children of the component
 * @returns The associated className.
 */
export const getComponentClassName = (children: ReactNode) =>
    (
        React.Children.map(children, (element) =>
            React.isValidElement(element) && element.type == TaipyStyle ? element.props.className : undefined
        )?.filter((v) => v) || []
    ).join(" ");

export const getStyle = (style: Record<string, unknown>): string =>
    Object.entries(style)
        .map(
            ([k, v]) =>
                `${k}${v &&
                          typeof v == "object" &&
                          !Array.isArray(v) ?
                          `{${Object.entries(v as Record<string, unknown>)
                              .map(([vk, vv]) => (typeof vv == "string" ? `${vk}:${vv}` : getStyle({ [vk]: vv })))
                              .join(";")}}` : `:${v}`
                }`
        )
        .join("\n");

const TaipyStyle = (props: TaipyStyleProps) => {
    try {
        const style = JSON.parse(props.content);
        return (
            <Helmet>
                <style>{getStyle({ [`.${props.className}`]: style })}</style>
            </Helmet>
        );
    } catch (e) {
        console.log("TaipyStyle", props, e);
        return null;
    }
};

export default TaipyStyle;
