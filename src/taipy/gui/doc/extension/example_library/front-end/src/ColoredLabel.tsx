// Implementation of the React component "ColoredLabel".
//
// This component displays a text string changing the color of
// each successive letter.
import React from "react";
import { useDynamicProperty } from "taipy-gui";

interface ColoredLabelProps {
  value?: string;
  defaultValue?: string;
}

// Sequence of colors
const colorWheel = ["#FF0000", "#A0A000", "#00FF00", "#00A0A0", "#0000FF", "#A000A0"]
// The array of styles using these colors
const colorStyles = colorWheel.map(c => ({ color: c }))

// ColoredLabel component definition
const ColoredLabel = (props: ColoredLabelProps) => {
  // The dynamic property that holds the text value
  const value = useDynamicProperty(props.value, props.defaultValue, "");
  // Empty text? Returning null produces no output.
  if (!value) {
    return null;
  }
  // Create a <span> element for each letter with the proper style.
  // Note that React needs, in this situation, to set the 'key' property
  // with a unique value for each <span> element.
  return (
    <>
      {value.split("").map((letter, index) => (
        <span key={"key" + index} style={colorStyles[index % 6]}>{letter}</span>
      ))}
    </>
  )
}

export default ColoredLabel;
