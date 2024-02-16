# Taipy GUI Extension API

This API is a JavaScript API that allows for building custom visual elements, on the client
side.

Visual elements are converted by the Taipy GUI Python library into React components that
can be rendered by a browser, connected to live variables, and respond to user actions
to trigger callbacks in the user Python code.

When the Python application generates pages to be displayed on a browser, both the application and the resulting page are connected under the hood so they can communicate.
The Extension API provides the entry points to send messages to the application.

In all this JavaScript API documentation section, we will refer to the Python side
of the application as the *backend*. This is where Python variables are stored and
manipulated, and where callbacks are invoked.<br/>
The client part, which usually is a tab in the browser of a user connected to the
Taipy GUI application, is referred to as the *front-end*. The front-end of the application
is it self an application, running on the end-user's user agent (the browser), and
is responsible for creating the pages that the user can look at and interact with. The
front-end application is able to receive messages from and send messages to the backend,
by means of the Extension API.

## Usage

The Extension API is located by the 'taipy-gui' module.

In order to import items from this module, you have to install it, using `npm`.
The most simple way to install the Taipy GUI Extension module is:
```bash
$ npm i <TAIPY_DIR>/taipy/gui/webapp
```

Where *<TAIPY_DIR>* represents the directory where, in the development machine's
filesystem, the Taipy GUI Python package has been installed.

When the package is installed, your JavaScript code can import items from it:
```javascript
import { ... } from "taipy-gui";
```

## Technical details

### Bound variables

When a variable is bound by a visual element, a corresponding variable is created on
the front-end.<br/>
Backend and front-end variables may not have the same names. While the backend variable
has the name that the Python script has created it with, the equivalent to this variable
on the front-end might have a different name, for technical reasons.

Note that controls that hold dynamic properties have two generated properties called
*updateVars* and *updateVarName*, that are used to ensure a proper update of variable changes. The function [getUpdateVar()](modules/#getupdatevar) uses that property.

Components dynamic properties are tied to the State: all updates of the State will
automatically be propagated to the relevant components and the component is in charge
of updating the render.

### Messaging

In order for the front-end to notify the backend of a change or query data, an `Action`
must be created (using the `create*Action()` functions) and dispatched to the React
context:

```javascript
const dispatch = useDispatch();
...
const action = create*Action(...);
...
dispatch(action);
```
