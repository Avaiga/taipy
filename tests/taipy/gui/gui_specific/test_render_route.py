import json
import warnings

from taipy.gui import Gui


def test_render_route(gui: Gui):
    gui.add_page("page1", "# first page")
    gui.add_page("page2", "# second page")
    gui.run(run_server=False)
    with warnings.catch_warnings(record=True) as w:
        client = gui._server.test_client()
        response = client.get("/taipy-init/")
        response_data = json.loads(response.get_data().decode("utf-8", "ignore"))
        assert response.status_code == 200
        assert isinstance(response_data, dict)
        assert "page1" in response_data["router"]
        assert "page2" in response_data["router"]
        assert "/" in response_data["router"]
        assert (
            response_data["router"]
            == '<Routes key="routes"><Route path="/" key="TaiPy_root_page" element={<MainPage key="trTaiPy_root_page" path="/TaiPy_root_page" route="/page1" />} ><Route path="page1" key="page1" element={<TaipyRendered key="trpage1"/>} /><Route path="page2" key="page2" element={<TaipyRendered key="trpage2"/>} /><Route path="*" key="NotFound" element={<NotFound404 />} /></Route></Routes>'
        )
