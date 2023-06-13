import React, { useEffect, useMemo, useState } from "react";
import { CanvasWidget } from "@projectstorm/react-canvas-core";
import Box from "@mui/material/Box";
import AppBar from "@mui/material/AppBar";
import IconButton from "@mui/material/IconButton";
import Toolbar from "@mui/material/Toolbar";
import { ZoomIn } from "@mui/icons-material";

import { DisplayModel } from "./utils/types";
import { initDiagram, populateModel, relayoutDiagram } from "./utils/diagram";
import { TaipyDiagramModel } from "./projectstorm/models";
import {
    createRequestUpdateAction,
    createSendUpdateAction,
    getUpdateVar,
    useDispatch,
    useDynamicProperty,
    useModule,
} from "taipy-gui";
import { useClassNames } from "./utils";

interface ScenarioDagProps {
    id?: string;
    scenario?: DisplayModel | DisplayModel[];
    coreChanged?: Record<string, unknown>;
    updateVarName?: string;
    render?: boolean;
    defaultRender?: boolean;
    showToolbar?: boolean;
    width?: string;
    height?: string;
    updateVars: string;
    libClassName?: string;
    className?: string;
    dynamicClassName?: string;
}

const boxSx = { "&>div": { height: "100%", width: "100%" }, height: "100%", width: "100%" };
const titleSx = { ml: 2, flex: 1 };
const appBarSx = { position: "relative" };

const [engine, dagreEngine] = initDiagram();

const relayout = () => relayoutDiagram(engine, dagreEngine);

const zoomToFit = () => engine.zoomToFit();

interface DagTitleProps {
    zoomToFit: () => void;
}
const DagTitle = (props: DagTitleProps) => (
    <AppBar sx={appBarSx}>
        <Toolbar>
            <Box sx={titleSx} />{" "}
            <IconButton edge="end" color="inherit" onClick={props.zoomToFit} title="zoom to fit">
                <ZoomIn />
            </IconButton>
        </Toolbar>
    </AppBar>
);

const ScenarioDag = (props: ScenarioDagProps) => {
    const { showToolbar = true } = props;
    const [scenarioId, setScenarioId] = useState("");
    const dispatch = useDispatch();
    const module = useModule();

    const render = useDynamicProperty(props.render, props.defaultRender, true);
    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);

    const sizeSx = useMemo(
        () => ({ width: props.width || "50vw", height: props.height || "50vh" }),
        [props.width, props.height]
    );

    // Refresh on broadcast
    useEffect(() => {
        const ids = props.coreChanged?.scenario;
        if (typeof ids === "string" ? ids === scenarioId : Array.isArray(ids) ? ids.includes(scenarioId) : ids) {
            props.updateVarName && dispatch(createRequestUpdateAction(props.id, module, [props.updateVarName], true));
        }
    }, [props.coreChanged, props.updateVarName, scenarioId, module, dispatch, props.id]);

    useEffect(() => {
        const displayModel = Array.isArray(props.scenario)
            ? props.scenario.length == 3 && typeof props.scenario[0] === "string"
                ? (props.scenario as DisplayModel)
                : props.scenario.length == 1
                ? (props.scenario[0] as DisplayModel)
                : undefined
            : undefined;

        // clear model
        const model = new TaipyDiagramModel();
        if (displayModel && props.scenario) {
            setScenarioId(displayModel[0]);
            // populate model
            populateModel(displayModel, model);
        }
        engine.setModel(model);
        // Block deletion
        //engine.getActionEventBus().registerAction(new DeleteItemsAction({ keyCodes: [1] }));
        model.setLocked(true);
        setTimeout(relayout, 500);
    }, [props.scenario]);

    useEffect(() => {
        const showVar = getUpdateVar(props.updateVars, "show");
        showVar && dispatch(createSendUpdateAction(showVar, render, module));
    }, [render, props.updateVars, dispatch, module]);

    return render ? (
        <Box sx={sizeSx} id={props.id} className={className}>
            {showToolbar ? <DagTitle zoomToFit={zoomToFit} /> : null}
            <Box sx={boxSx}>
                <CanvasWidget engine={engine} />
            </Box>
        </Box>
    ) : null;
};

export default ScenarioDag;
