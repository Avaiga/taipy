class ScenarioManager:
    
    def has_data_node_changed(self, task):
        # Check if input Data Nodes for the task have changed
        for data_node in task.input_data_nodes:
            if not self.is_data_node_unchanged(data_node):
                return True
        return False

    def is_data_node_unchanged(self, data_node):
        # Logic to compare current Data Node state with the cached version
        cached_data_node = self.get_cached_data_node(data_node.id)
        return data_node.value == cached_data_node.value

    def get_cached_data_node(self, data_node_id):
        # Placeholder: Retrieve cached Data Node from database or memory
        pass
