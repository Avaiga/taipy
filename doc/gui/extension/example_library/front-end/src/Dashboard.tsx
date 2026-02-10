/*
 * Copyright 2021-2025 Avaiga Private Limited
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

import React, { useMemo } from "react";
import { useDynamicJsonProperty } from "taipy-gui";

import Plot from "react-plotly.js";
import { Data, Layout } from "plotly.js";

interface DashboardProps {
  data?: string;
  defaultData?: string;
  layout?: string;
  defaultLayout?: string;
}

const Dashboard = (props: DashboardProps) => {
  const value = useDynamicJsonProperty(props.data, props.defaultData || "", {} as Partial<Data>);
  const dashboardLayout = useDynamicJsonProperty(props.layout, props.defaultLayout || "", {} as Partial<Layout>);

  const data = useMemo(() => {
    if (Array.isArray(value)) {
      return value as Data[];
    }
    return [] as Data[];
  }, [value]);

  const baseLayout = useMemo(() => {
    const layout = {
      ...dashboardLayout,
    };
    return layout as Partial<Layout>;
  }, [dashboardLayout]);

  return <Plot data={data} layout={baseLayout} />;
};

export default Dashboard;
