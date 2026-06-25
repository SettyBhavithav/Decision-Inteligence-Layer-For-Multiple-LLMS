import collections
from typing import Dict, Any, List, Set

class DynamicTaskScheduler:
    """
    Topologically sorts subtasks and coordinates their execution as dependencies resolve.
    """
    def __init__(self, subtasks: List[Dict[str, Any]]):
        self.subtasks = {t["id"]: t for t in subtasks}
        self.dependencies = {t["id"]: set(t.get("dependencies", [])) for t in subtasks}
        self.completed_tasks: Set[str] = set()
        self.running_tasks: Set[str] = set()

    def get_ready_tasks(self) -> List[Dict[str, Any]]:
        """
        Returns a list of tasks that have all their dependencies completed
        and are not yet running or finished.
        """
        ready = []
        for task_id, deps in self.dependencies.items():
            if task_id in self.completed_tasks or task_id in self.running_tasks:
                continue
            if deps.issubset(self.completed_tasks):
                ready.append(self.subtasks[task_id])
        return ready

    def mark_running(self, task_id: str) -> None:
        """Mark a task as currently executing."""
        if task_id in self.subtasks:
            self.running_tasks.add(task_id)

    def mark_completed(self, task_id: str) -> None:
        """Mark a task as completed, releasing it as a dependency for downstream tasks."""
        if task_id in self.running_tasks:
            self.running_tasks.remove(task_id)
        self.completed_tasks.add(task_id)

    def is_finished(self) -> bool:
        """Returns True if all scheduled tasks are completed."""
        return len(self.completed_tasks) == len(self.subtasks)

    def get_execution_order(self) -> List[str]:
        """
        Performs topological sort to find execution order.
        """
        in_degree = {t_id: len(deps) for t_id, deps in self.dependencies.items()}
        adj = collections.defaultdict(list)
        for t_id, deps in self.dependencies.items():
            for dep in deps:
                adj[dep].append(t_id)

        queue = collections.deque([t_id for t_id, deg in in_degree.items() if deg == 0])
        order = []
        
        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    
        if len(order) != len(self.subtasks):
            raise ValueError("Dependency cycle detected in the task list!")
        return order
