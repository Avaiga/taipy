import { LoV, useDynamicProperty } from "taipy-gui";

interface ScenarioSelectorProps {
  defaultShowAddButton: boolean;
  showAddButton?: boolean;
  defaultDisplayCycles: boolean;
  displayCycles?: boolean;
  defaultShowPrimaryFlag: boolean;
  showPrimaryFlag?: boolean;
  scenarios?: LoV;
  defaultScenarioId?: string;
  scenarioId?: string;
  onScenarioCreate?: string;
  coreChanged?: Record<string, unknown>;
}

const ScenarioSelector = (props: ScenarioSelectorProps) => {
  const { } = props;

  const showAddButton = useDynamicProperty(props.showAddButton, props.defaultShowAddButton, true);
  const displayCycles = useDynamicProperty(props.displayCycles, props.defaultDisplayCycles, true);
  const showPrimaryFlag = useDynamicProperty(props.showPrimaryFlag, props.defaultShowPrimaryFlag, true);
  const scenarioId = useDynamicProperty(props.scenarioId, props.defaultScenarioId, "");

  return <><span>ScenarioSelector</span><code>{JSON.stringify(props)}</code></>
}

export default ScenarioSelector;