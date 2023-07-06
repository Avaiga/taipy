# check if all scenario inputs are ready to run
def is_ready_to_run(scenario):
    return all([d.is_ready_for_reading for d in scenario._get_inputs()])


# get all scenario inputs
def get_inputs(scenario):
    return {d.id: (d.id, d.get_simple_label(), d) for d in scenario._get_inputs()}


# get all scenario outputs
def get_outputs(scenario):
    data_nodes = scenario.data_nodes.values()
    return {d.id: (d.id, d.get_simple_label(), d) for d in data_nodes if d not in scenario._get_inputs()}
