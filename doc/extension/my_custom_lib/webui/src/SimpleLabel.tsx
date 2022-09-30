import React from "react";
import { useDynamicProperty } from "taipy-gui";

interface SimpleLabelProps {
  value?: string;
  defaultValue?: string;
}

const SimpleLabel = (props: SimpleLabelProps) => {
  const value = useDynamicProperty(props.value, props.defaultValue, "");
  return <span>My Label: {value}</span>
}

// Note that for this very simple component, we could have used a one-liner:
// const SimpleLabel = (props: SimpleLabelProps) => <span>My Label: {useDynamicProperty(props.value, props.defaultValue, "")}</span>

export default SimpleLabel;
