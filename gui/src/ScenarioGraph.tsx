import React, { useCallback, useEffect, useState } from "react";
import { CanvasWidget } from "@projectstorm/react-canvas-core";
import { DeleteItemsAction } from "@projectstorm/react-diagrams";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import AppBar from "@mui/material/AppBar";
import Dialog from "@mui/material/Dialog";
import IconButton from "@mui/material/IconButton";
import Slide from "@mui/material/Slide";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import { TransitionProps } from "@mui/material/transitions";
import { Close, ZoomIn } from "@mui/icons-material";

import { DisplayModel } from "./utils/types";
import { initDiagram, populateModel, relayoutDiagram } from "./utils/diagram";
import { TaipyDiagramModel } from "./projectstorm/models";
import { createRequestUpdateAction, useDispatch, useDynamicProperty, useModule } from "taipy-gui";

interface ScenarioGraphProps {
    id?: string;
    scenario?: DisplayModel;
    coreChanged?: Record<string, unknown>;
    buttonLabel?: string;
    defaultButtonLabel?: string;
    updateVarName?: string;
}

const boxSx = { "&>div": { height: "100%", width: "100%" }, height: "100%", width: "100%" };
const titleSx = { ml: 2, flex: 1 };
const appBarSx = { position: "relative" };

const [engine, dagreEngine] = initDiagram();

const relayout = () => relayoutDiagram(engine, dagreEngine);

const zoomToFit = () => engine.zoomToFit();

const Transition = React.forwardRef(function Transition(
    props: TransitionProps & {
        children: React.ReactElement;
    },
    ref: React.Ref<unknown>
) {
    return <Slide direction="up" ref={ref} {...props} />;
});

const ScenarioGraph = (props: ScenarioGraphProps) => {
    const [open, setOpen] = useState(false);
    const [disabled, setDisabled] = useState(false);
    const [title, setTitle] = useState("");

    const dispatch = useDispatch();
    const module = useModule();

    const label = useDynamicProperty(props.buttonLabel, props.defaultButtonLabel, "Show graph");

    const showGraph = useCallback(() => {
        setTimeout(relayout, 500);
        setOpen(true);
    }, []);
    const hideGraph = useCallback(() => setOpen(false), []);

    // Refresh on broadcast
    useEffect(() => {
        if (props.coreChanged?.scenario) {
            props.updateVarName && dispatch(createRequestUpdateAction(props.id, module, [props.updateVarName], true));
        }
    }, [props.coreChanged, props.updateVarName, module, dispatch]);

    useEffect(() => {
        const displayModel = props.scenario
            ? Array.isArray(props.scenario)
                ? props.scenario.length == 1
                    ? props.scenario[0]
                    : undefined
                : props.scenario
            : undefined;

        if (!displayModel || !props.scenario) {
            setDisabled(true);
            return;
        }
        setDisabled(false);
        setTitle(displayModel.label);
        // clear model
        const model = new TaipyDiagramModel();
        // populate model
        populateModel(displayModel, model);
        engine.setModel(model);
        // Block deletion
        //engine.getActionEventBus().registerAction(new DeleteItemsAction({ keyCodes: [1] }));
        model.setLocked(true);
    }, [props.scenario]);

    return (
        <>
            <Button id={props.id} variant="outlined" onClick={showGraph} disabled={disabled}>
                {label}
            </Button>
            <Dialog fullScreen open={open} onClose={hideGraph} TransitionComponent={Transition}>
                <AppBar sx={appBarSx}>
                    <Toolbar>
                        <Typography sx={titleSx} variant="h6" component="div">
                            Scenario: {title}
                        </Typography>
                        <IconButton edge="end" color="inherit" onClick={zoomToFit} title="zoom to fit">
                            <ZoomIn />
                        </IconButton>
                        <IconButton edge="end" color="inherit" onClick={hideGraph} title="close">
                            <Close />
                        </IconButton>
                    </Toolbar>
                </AppBar>
                <Box sx={boxSx}>{open ? <CanvasWidget engine={engine} /> : null}</Box>
            </Dialog>
        </>
    );
};

export default ScenarioGraph;
