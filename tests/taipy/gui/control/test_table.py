from taipy.gui import Gui


def test_table_md_1(gui: Gui, helpers, csvdata):
    gui.bind_var_val("csvdata", csvdata)
    md_string = "<|{csvdata}|table|page_size=10|page_size_options=10;30;100|columns=Day;Entity;Code;Daily hospital occupancy|date_format=eee dd MMM yyyy|>"
    expected_list = [
        "<Table",
        'columns="{&quot;Entity&quot;: {&quot;index&quot;: 1, &quot;type&quot;: &quot;object&quot;, &quot;dfid&quot;: &quot;Entity&quot;}, &quot;Code&quot;: {&quot;index&quot;: 2, &quot;type&quot;: &quot;object&quot;, &quot;dfid&quot;: &quot;Code&quot;}, &quot;Daily hospital occupancy&quot;: {&quot;index&quot;: 3, &quot;type&quot;: &quot;int64&quot;, &quot;dfid&quot;: &quot;Daily hospital occupancy&quot;}, &quot;Day_str&quot;: {&quot;index&quot;: 0, &quot;type&quot;: &quot;datetime64[ns]&quot;, &quot;dfid&quot;: &quot;Day&quot;, &quot;format&quot;: &quot;eee dd MMM yyyy&quot;}}"',
        'height="80vh"',
        'width="100vw"',
        'pageSizeOptions="[10, 30, 100]"',
        "pageSize={100}",
        "refresh={csvdata__refresh}",
        "selected={[]}",
        'tp_varname="csvdata"',
        "data={csvdata}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_table_md_2(gui: Gui, helpers, csvdata):
    gui.bind_var_val("csvdata", csvdata)
    gui.bind_var_val(
        "table_properties",
        {
            "page_size": 10,
            "page_size_options": [10, 50, 100, 500],
            "allow_all_rows": True,
            "columns": {
                "Day": {"index": 0, "format": "dd/MM/yyyy", "title": "Date of measure"},
                "Entity": {"index": 1},
                "Code": {"index": 2},
                "Daily hospital occupancy": {"index": 3},
            },
            "date_format": "eee dd MMM yyyy",
            "number_format": "%.3f",
            "width": "60vw",
            "height": "60vh",
        },
    )
    md_string = "<|{csvdata}|table|properties=table_properties|not auto_loading|>"
    expected_list = [
        "<Table",
        "allowAllRows={true}",
        "autoLoading={false}",
        'columns="{&quot;Entity&quot;: {&quot;index&quot;: 1, &quot;type&quot;: &quot;object&quot;, &quot;dfid&quot;: &quot;Entity&quot;}, &quot;Code&quot;: {&quot;index&quot;: 2, &quot;type&quot;: &quot;object&quot;, &quot;dfid&quot;: &quot;Code&quot;}, &quot;Daily hospital occupancy&quot;: {&quot;index&quot;: 3, &quot;type&quot;: &quot;int64&quot;, &quot;dfid&quot;: &quot;Daily hospital occupancy&quot;, &quot;format&quot;: &quot;%.3f&quot;}, &quot;Day_str&quot;: {&quot;index&quot;: 0, &quot;format&quot;: &quot;dd/MM/yyyy&quot;, &quot;title&quot;: &quot;Date of measure&quot;, &quot;type&quot;: &quot;datetime64[ns]&quot;, &quot;dfid&quot;: &quot;Day&quot;}}"',
        'height="60vh"',
        'width="60vw"',
        'pageSizeOptions="[10, 50, 100, 500]"',
        "pageSize={100}",
        "refresh={csvdata__refresh}",
        "selected={[]}",
        'tp_varname="csvdata"',
        "data={csvdata}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_table_html_1(gui: Gui, helpers, csvdata):
    gui.bind_var_val("csvdata", csvdata)
    html_string = '<taipy:table data="{csvdata}" page_size="10" page_size_options="10;30;100" columns="Day;Entity;Code;Daily hospital occupancy" date_format="eee dd MMM yyyy" />'
    expected_list = [
        "<Table",
        'columns="{&quot;Entity&quot;: {&quot;index&quot;: 1, &quot;type&quot;: &quot;object&quot;, &quot;dfid&quot;: &quot;Entity&quot;}, &quot;Code&quot;: {&quot;index&quot;: 2, &quot;type&quot;: &quot;object&quot;, &quot;dfid&quot;: &quot;Code&quot;}, &quot;Daily hospital occupancy&quot;: {&quot;index&quot;: 3, &quot;type&quot;: &quot;int64&quot;, &quot;dfid&quot;: &quot;Daily hospital occupancy&quot;}, &quot;Day_str&quot;: {&quot;index&quot;: 0, &quot;type&quot;: &quot;datetime64[ns]&quot;, &quot;dfid&quot;: &quot;Day&quot;, &quot;format&quot;: &quot;eee dd MMM yyyy&quot;}}"',
        'height="80vh"',
        'width="100vw"',
        'pageSizeOptions="[10, 30, 100]"',
        "pageSize={100}",
        "refresh={csvdata__refresh}",
        "selected={[]}",
        'tp_varname="csvdata"',
        "data={csvdata}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_table_html_2(gui: Gui, helpers, csvdata):
    gui.bind_var_val("csvdata", csvdata)
    gui.bind_var_val(
        "table_properties",
        {
            "page_size": 10,
            "page_size_options": [10, 50, 100, 500],
            "allow_all_rows": True,
            "columns": {
                "Day": {"index": 0, "format": "dd/MM/yyyy", "title": "Date of measure"},
                "Entity": {"index": 1},
                "Code": {"index": 2},
                "Daily hospital occupancy": {"index": 3},
            },
            "date_format": "eee dd MMM yyyy",
            "number_format": "%.3f",
            "width": "60vw",
            "height": "60vh",
        },
    )
    html_string = '<taipy:table data="{csvdata}" properties="table_properties" auto_loading="False" />'
    expected_list = [
        "<Table",
        "allowAllRows={true}",
        "autoLoading={false}",
        'columns="{&quot;Entity&quot;: {&quot;index&quot;: 1, &quot;type&quot;: &quot;object&quot;, &quot;dfid&quot;: &quot;Entity&quot;}, &quot;Code&quot;: {&quot;index&quot;: 2, &quot;type&quot;: &quot;object&quot;, &quot;dfid&quot;: &quot;Code&quot;}, &quot;Daily hospital occupancy&quot;: {&quot;index&quot;: 3, &quot;type&quot;: &quot;int64&quot;, &quot;dfid&quot;: &quot;Daily hospital occupancy&quot;, &quot;format&quot;: &quot;%.3f&quot;}, &quot;Day_str&quot;: {&quot;index&quot;: 0, &quot;format&quot;: &quot;dd/MM/yyyy&quot;, &quot;title&quot;: &quot;Date of measure&quot;, &quot;type&quot;: &quot;datetime64[ns]&quot;, &quot;dfid&quot;: &quot;Day&quot;}}"',
        'height="60vh"',
        'width="60vw"',
        'pageSizeOptions="[10, 50, 100, 500]"',
        "pageSize={100}",
        "refresh={csvdata__refresh}",
        "selected={[]}",
        'tp_varname="csvdata"',
        "data={csvdata}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)
