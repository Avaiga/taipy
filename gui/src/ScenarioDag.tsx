import React, { useCallback, useEffect, useMemo, useState } from "react";
import { CanvasWidget } from "@projectstorm/react-canvas-core";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import AppBar from "@mui/material/AppBar";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle/DialogTitle";
import DialogContent from "@mui/material/DialogContent/DialogContent";
import IconButton from "@mui/material/IconButton";
import Slide from "@mui/material/Slide";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import { TransitionProps } from "@mui/material/transitions";
import { Close, ZoomIn } from "@mui/icons-material";

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

interface ScenarioDagProps {
    id?: string;
    scenario?: DisplayModel | DisplayModel[];
    coreChanged?: Record<string, unknown>;
    buttonLabel?: string;
    defaultButtonLabel?: string;
    updateVarName?: string;
    show?: boolean;
    defaultShow?: boolean;
    withButton?: boolean;
    width?: string;
    height?: string;
    updateVars: string;
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

interface DagTitleProps {
    title: string;
    zoomToFit: () => void;
    hideDialog?: () => void;
}
const DagTitle = (props: DagTitleProps) => (
    <AppBar sx={appBarSx}>
        <Toolbar>
            <Typography sx={titleSx} variant="h6" component="div">
                Scenario: {props.title}
            </Typography>
            <IconButton edge="end" color="inherit" onClick={props.zoomToFit} title="zoom to fit">
                <ZoomIn />
            </IconButton>{" "}
            {props.hideDialog ? (
                <IconButton edge="end" color="inherit" onClick={props.hideDialog} title="close">
                    <Close />
                </IconButton>
            ) : null}
        </Toolbar>
    </AppBar>
);

const ScenarioDag = (props: ScenarioDagProps) => {
    const { withButton = true } = props;

    const [open, setOpen] = useState(false);
    const [disabled, setDisabled] = useState(false);
    const [title, setTitle] = useState("");

    const dispatch = useDispatch();
    const module = useModule();

    const label = useDynamicProperty(props.buttonLabel, props.defaultButtonLabel, "Show DAG");
    const show = useDynamicProperty(props.show, props.defaultShow, !withButton);

    const [full, sizeSx] = useMemo(() => {
        return [!props.width && !props.height, { width: props.width || "50vw", height: props.height || "50vh" }];
    }, [props.width, props.height]);

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
    }, [props.coreChanged, props.updateVarName, module, dispatch, props.id]);

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
        if (!displayModel || !props.scenario) {
            setDisabled(true);
            setTitle("");
        } else {
            setDisabled(false);
            setTitle(displayModel[0]);
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
        if (withButton) {
            show && setTimeout(relayout, 500);
            setOpen(!!show);
        }
    }, [show, withButton]);

    useEffect(() => {
        const showVar = getUpdateVar(props.updateVars, "show");
        showVar && dispatch(createSendUpdateAction(showVar, show, module));
    }, [show, props.updateVars, dispatch, module]);

    return withButton ? (
        <>
            <Button id={props.id} variant="outlined" onClick={showGraph} disabled={disabled}>
                {label}
            </Button>
            {full ? (
                <Dialog fullScreen open={open} onClose={hideGraph} TransitionComponent={Transition}>
                    <DagTitle title={title} zoomToFit={zoomToFit} hideDialog={hideGraph} />
                    <Box sx={boxSx}>{open ? <CanvasWidget engine={engine} /> : null}</Box>
                </Dialog>
            ) : (
                <Dialog open={open} onClose={hideGraph} TransitionComponent={Transition}>
                    <DialogTitle>
                        <DagTitle title={title} zoomToFit={zoomToFit} hideDialog={hideGraph} />
                    </DialogTitle>
                    <DialogContent sx={sizeSx}>
                        <Box sx={boxSx}>{open ? <CanvasWidget engine={engine} /> : null}</Box>
                    </DialogContent>
                </Dialog>
            )}
        </>
    ) : show ? (
        <>
            <Box sx={sizeSx}>
                <DagTitle title={title} zoomToFit={zoomToFit} />
                <Box sx={boxSx}>
                    <CanvasWidget engine={engine} />
                </Box>
            </Box>
        </>
    ) : null;
};

export default ScenarioDag;
