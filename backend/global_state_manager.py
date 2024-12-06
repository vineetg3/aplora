from workflow_runner import WorkflowRunner


class GlobalStateManager:
    def __init__(self):
        # Internal dictionary to store WorkflowRunner objects
        self.global_state = {}

    def add_workflow_runner(self, work_id, workflow_runner):
        """
        Add a new WorkflowRunner object.
        :param work_id: Unique identifier for the workflow.
        :param workflow_runner: Instance of WorkflowRunner to be added.
        """
        self.global_state[work_id] = workflow_runner

    def get_workflow_runner(self, work_id):
        """
        Retrieve a WorkflowRunner object by work_id.
        :param work_id: Unique identifier for the workflow.
        :return: WorkflowRunner instance or None if not found.
        """
        return self.global_state.get(work_id, None)

    def remove_workflow_runner(self, work_id):
        """
        Remove a WorkflowRunner object by work_id.
        :param work_id: Unique identifier for the workflow.
        """
        if work_id in self.global_state:
            del self.global_state[work_id]

    def list_work_ids(self):
        """
        List all work_ids in the global state.
        :return: List of work_id keys.
        """
        return list(self.global_state.keys())

    def has_workflow_runner(self, work_id):
        """
        Check if a WorkflowRunner exists for a given work_id.
        :param work_id: Unique identifier for the workflow.
        :return: True if work_id exists, False otherwise.
        """
        return work_id in self.global_state

    def clear_all(self):
        """
        Clear all WorkflowRunner objects.
        """
        self.global_state.clear()
