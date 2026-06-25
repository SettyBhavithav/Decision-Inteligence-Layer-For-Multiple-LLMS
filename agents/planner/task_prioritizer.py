import collections
import logging
from typing import List, Dict, Any

logger = logging.getLogger("trust_framework")

class TaskPrioritizer:
    """Submodule 3: Sorts decomposed subtasks in topological dependency order and validates dependency integrity."""
    def __init__(self):
        pass

    def prioritize(self, subtasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not subtasks:
            return []

        task_map = {t["id"]: t for t in subtasks}
        dependencies = {t["id"]: set(t.get("dependencies", [])) for t in subtasks}
        
        # Build adjacency list
        in_degree = {t_id: len(deps) for t_id, deps in dependencies.items()}
        adj = collections.defaultdict(list)
        for t_id, deps in dependencies.items():
            for dep in deps:
                adj[dep].append(t_id)

        queue = collections.deque([t_id for t_id, deg in in_degree.items() if deg == 0])
        ordered_ids = []
        
        while queue:
            node = queue.popleft()
            ordered_ids.append(node)
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    
        # Check for circular dependency cycles
        if len(ordered_ids) != len(subtasks):
            logger.warning("TaskPrioritizer: Circular dependency cycle detected! Falling back to raw sequence order.")
            return subtasks

        ordered_tasks = [task_map[t_id] for t_id in ordered_ids]
        logger.info(f"TaskPrioritizer: Successfully prioritized {len(ordered_tasks)} subtasks topologically.")
        return ordered_tasks
