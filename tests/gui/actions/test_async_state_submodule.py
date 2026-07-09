import inspect
import typing as t
import pytest
from taipy.gui import Gui, Markdown
from taipy.gui.state import _AsyncState, _GuiState

def test_async_state_submodule(gui: Gui, helpers):
    counter = 0
    gui._set_frame(inspect.currentframe())
    gui.add_page("test", Markdown("<|Hello|button|>\n<|{counter}|>"))
    gui.run(run_server=False)
    
    server_test_client = gui._server.test_client()
    ws_client = gui._server._ws.test_client(gui._server.get_server_instance())  # type: ignore[arg-type]
    cid = helpers.create_scope_and_get_sid(gui)
    server_test_client.get(f"/{Gui._JSX_URL}/test?client_id={cid}")
    
    with gui._server.test_request_context(f"/{Gui._JSX_URL}/test/?client_id={cid}", data={"client_id": cid}):
        gui._server.request.get_request_meta().client_id = cid
        async_state = _AsyncState(t.cast(_GuiState, gui._Gui__state))
        
        async_state.counter = 5
        assert async_state.counter == 5
        
        # Test __get_var_from_state inside invoke_callback (this runs on the thread invoke_callback executes in)
        val = async_state.counter
        assert val == 5
