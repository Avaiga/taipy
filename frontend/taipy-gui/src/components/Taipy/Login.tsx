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

import React, { ChangeEvent, KeyboardEvent, MouseEvent, useCallback, useEffect, useMemo, useState } from "react";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import DialogTitle from "@mui/material/DialogTitle";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import InputAdornment from "@mui/material/InputAdornment";
import TextField from "@mui/material/TextField";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import { SxProps, Theme } from "@mui/system";

import { createSendActionNameAction } from "../../context/taipyReducers";
import { TaipyBaseProps, getSuffixedClassNames } from "./utils";
import { useClassNames, useDispatch, useModule } from "../../utils/hooks";

// allow only one instance of this component
let nbLogins = 0;

interface LoginProps extends TaipyBaseProps {
    title?: string;
    onAction?: string;
    defaultMessage?: string;
    message?: string;
}

const closeSx: SxProps<Theme> = {
    color: (theme: Theme) => theme.palette.grey[500],
    marginTop: "-0.6em",
    marginLeft: "auto",
    alignSelf: "start",
};
const titleSx = { m: 0, p: 2, display: "flex", paddingRight: "0.1em" };
const userProps = { autocomplete: "username" };
const pwdProps = { autocomplete: "current-password" };

const Login = (props: LoginProps) => {
    const { id, title = "Log-in", onAction = "on_login", message, defaultMessage } = props;
    const dispatch = useDispatch();
    const module = useModule();
    const [onlyOne, setOnlyOne] = useState(false);
    const [user, setUser] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [showProgress, setShowProgress] = useState(false);

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);

    const handleAction = useCallback(
        (evt: MouseEvent<HTMLElement>) => {
            const { close } = evt?.currentTarget.dataset || {};
            const args = close
                ? [null, null, document.location.pathname.substring(1)]
                : [user, password, document.location.pathname.substring(1)];
            setShowProgress(true);
            dispatch(createSendActionNameAction(id, module, onAction, ...args));
        },
        [user, password, dispatch, id, onAction, module]
    );

    const changeInput = useCallback((evt: ChangeEvent<HTMLInputElement>) => {
        const { input } = evt.currentTarget.parentElement?.parentElement?.dataset || {};
        input == "user" ? setUser(evt.currentTarget.value) : setPassword(evt.currentTarget.value);
    }, []);

    const handleEnter = useCallback(
        (evt: KeyboardEvent<HTMLInputElement>) => {
            if (!evt.shiftKey && !evt.ctrlKey && !evt.altKey && evt.key == "Enter") {
                handleAction(undefined as unknown as MouseEvent<HTMLElement>);
                evt.preventDefault();
            }
        },
        [handleAction]
    );

    // password
    const handleClickShowPassword = useCallback(() => setShowPassword((show) => !show), []);
    const handleMouseDownPassword = useCallback(
        (event: React.MouseEvent<HTMLButtonElement>) => event.preventDefault(),
        []
    );
    const passwordProps = useMemo(
        () => ({
            endAdornment: (
                <InputAdornment position="end">
                    <IconButton
                        aria-label="toggle password visibility"
                        onClick={handleClickShowPassword}
                        onMouseDown={handleMouseDownPassword}
                        edge="end"
                    >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                </InputAdornment>
            ),
        }),
        [showPassword, handleClickShowPassword, handleMouseDownPassword]
    );

    useEffect(() => {
        nbLogins++;
        if (nbLogins === 1) {
            setOnlyOne(true);
        }
        return () => {
            nbLogins--;
        };
    }, []);

    return onlyOne ? (
        <Dialog id={id} open={true} className={className}>
            <DialogTitle sx={titleSx}>
                {title}
                <IconButton aria-label="close" onClick={handleAction} sx={closeSx} title="close" data-close>
                    <CloseIcon />
                </IconButton>
            </DialogTitle>

            <DialogContent dividers>
                <TextField
                    variant="outlined"
                    label="User name"
                    required
                    fullWidth
                    margin="dense"
                    className={getSuffixedClassNames(className, "-user")}
                    value={user}
                    onChange={changeInput}
                    data-input="user"
                    onKeyDown={handleEnter}
                    inputProps={userProps}
                ></TextField>
                <TextField
                    variant="outlined"
                    label="Password"
                    required
                    fullWidth
                    margin="dense"
                    className={getSuffixedClassNames(className, "-password")}
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={changeInput}
                    data-input="password"
                    onKeyDown={handleEnter}
                    inputProps={pwdProps}
                    InputProps={passwordProps}
                />
                <DialogContentText>{message || defaultMessage}</DialogContentText>
            </DialogContent>
            <DialogActions>
                <Button
                    variant="outlined"
                    className={getSuffixedClassNames(className, "-button")}
                    onClick={handleAction}
                    disabled={!user || !password || showProgress}
                >
                    {showProgress ? <CircularProgress size="2rem" /> : "Log in"}
                </Button>
            </DialogActions>
        </Dialog>
    ) : null;
};

export default Login;
