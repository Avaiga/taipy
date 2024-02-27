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

import React, { CSSProperties, useCallback } from "react";
import Modal from "@mui/material/Modal";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";

import { BlockMessage, BLOCK_CLOSE, createBlockAction, createSendActionNameAction } from "../../context/taipyReducers";
import { useDispatch, useModule } from "../../utils/hooks";

interface UIBlockerProps {
    block?: BlockMessage;
}

const style = {
    position: "absolute",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    minWidth: 400,
    width: "30%",
    bgcolor: "background.paper",
    border: "2px solid #000",
    boxShadow: 24,
    p: 4,
} as unknown as CSSProperties;

const UIBlocker = ({ block }: UIBlockerProps) => {
    const dispatch = useDispatch();
    const module = useModule();
    const handleClose = useCallback(() => {
        if (block && !block.noCancel) {
            dispatch(createSendActionNameAction("UIBlocker", module, block.action));
            dispatch(createBlockAction(BLOCK_CLOSE));
        }
    }, [block, dispatch, module]);

    return block === undefined || block.close ? null : (
        <Modal open>
            <Box sx={style} className="taipy-UIBlocker">
                <Typography variant="h6" component="h2">
                    {block.message}
                </Typography>
                {block.noCancel ? null : <Button onClick={handleClose}>Cancel</Button>}
            </Box>
        </Modal>
    );
};

export default UIBlocker;
