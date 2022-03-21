from src.taipy.rest.app import create_app
import taipy.core as tp

if __name__ == '__main__':
    d = tp.configure_data_node("test")
    t = tp.configure_task("test", print, d)
    tp.configure_scenario_from_tasks("tp", [t])

    app = create_app()
    app.run(debug=False)
