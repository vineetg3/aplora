
class WorkState:
    def __init__(self, work_id, renderedHTML):
        self.work_id = work_id
        self.renderedHTML = renderedHTML

    def __str__(self) -> str:
        return (
            f"WorkState("
            f"work_id={self.work_id}, "
            f"renderedHTML={self.renderedHTML[:200]}{'...' if len(self.renderedHTML) > 200 else ''}"
            f")"
        )