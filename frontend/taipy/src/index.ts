import React, { useState, useEffect } from 'react';
import ScenarioSelector from "./ScenarioSelector";
import ScenarioViewer from "./ScenarioViewer";
import ScenarioDag from "./ScenarioDag";
import NodeSelector from "./NodeSelector";
import JobSelector from "./JobSelector";
import DataNodeViewer from "./DataNodeViewer";

// Example Component to demonstrate useEffect for refreshing selector list on first render
const MyComponent = () => {
  const [selectorList, setSelectorList] = useState([]);

  useEffect(() => {
    // Simulate fetching selector list data on first render
    const fetchSelectorList = async () => {
      const response = await fetch('/api/selector-list');
      const data = await response.json();
      setSelectorList(data);
    };
    fetchSelectorList();
  }, []); // Empty dependency array ensures this runs only on the first render

  return (
    <div>
      <select>
        {selectorList.map((option, index) => (
          <option key={index} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
};

// Re-exporting components to be used in other parts of the application
export {
  ScenarioSelector,
  ScenarioDag,
  ScenarioViewer as Scenario,
  NodeSelector as DataNodeSelector,
  JobSelector,
  DataNodeViewer as DataNode,
  MyComponent // Adding the example component for testing
};
