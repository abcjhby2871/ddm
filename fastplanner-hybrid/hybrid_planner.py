from __future__ import annotations

from dataclasses import dataclass
import heapq
import math
from typing import Dict, Iterable, List, Optional, Tuple

GridPoint = Tuple[int, int]


@dataclass(frozen=True)
class PlannerConfig:
    """Configuration for global-local hybrid planning."""

    resolution: float = 1.0
    local_horizon_m: float = 8.0
    waypoint_stride_m: float = 2.0


class GridAStar:
    """A* over a 2D occupancy grid.

    `occupancy[y][x] == 1` is obstacle, `0` is free.
    """

    def __init__(self, occupancy: List[List[int]]):
        if not occupancy or not occupancy[0]:
            raise ValueError("occupancy grid must be non-empty")
        self.occ = occupancy
        self.h = len(occupancy)
        self.w = len(occupancy[0])

    def _in_bounds(self, p: GridPoint) -> bool:
        x, y = p
        return 0 <= x < self.w and 0 <= y < self.h

    def _free(self, p: GridPoint) -> bool:
        x, y = p
        return self.occ[y][x] == 0

    def _neighbors(self, p: GridPoint) -> Iterable[Tuple[GridPoint, float]]:
        x, y = p
        dirs = [
            (-1, 0, 1.0),
            (1, 0, 1.0),
            (0, -1, 1.0),
            (0, 1, 1.0),
            (-1, -1, math.sqrt(2.0)),
            (-1, 1, math.sqrt(2.0)),
            (1, -1, math.sqrt(2.0)),
            (1, 1, math.sqrt(2.0)),
        ]
        for dx, dy, c in dirs:
            nxt = (x + dx, y + dy)
            if self._in_bounds(nxt) and self._free(nxt):
                yield nxt, c

    @staticmethod
    def _heuristic(a: GridPoint, b: GridPoint) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def search(self, start: GridPoint, goal: GridPoint) -> List[GridPoint]:
        if not (self._in_bounds(start) and self._in_bounds(goal)):
            raise ValueError("start/goal out of map")
        if not (self._free(start) and self._free(goal)):
            raise ValueError("start/goal in obstacle")

        pq: List[Tuple[float, GridPoint]] = []
        heapq.heappush(pq, (0.0, start))

        g_score: Dict[GridPoint, float] = {start: 0.0}
        parent: Dict[GridPoint, Optional[GridPoint]] = {start: None}

        while pq:
            _, cur = heapq.heappop(pq)
            if cur == goal:
                return self._reconstruct(parent, goal)

            cur_g = g_score[cur]
            for nxt, c in self._neighbors(cur):
                ng = cur_g + c
                if ng < g_score.get(nxt, float("inf")):
                    g_score[nxt] = ng
                    parent[nxt] = cur
                    f = ng + self._heuristic(nxt, goal)
                    heapq.heappush(pq, (f, nxt))

        raise RuntimeError("A* failed: no path")

    @staticmethod
    def _reconstruct(parent: Dict[GridPoint, Optional[GridPoint]], end: GridPoint) -> List[GridPoint]:
        path: List[GridPoint] = []
        cur: Optional[GridPoint] = end
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        return path


class HybridPlanner:
    """Global path + local target extraction for receding-horizon local planning.

    This mirrors the common Fast-Planner integration strategy:
    1) Run A* once to get a topological-safe global guide path.
    2) During flight, project current position to this guide path.
    3) Pick a local goal ahead by horizon distance.
    """

    def __init__(self, occupancy: List[List[int]], cfg: PlannerConfig = PlannerConfig()):
        self.cfg = cfg
        self.astar = GridAStar(occupancy)
        self.global_path: List[GridPoint] = []

    def plan_global(self, start: GridPoint, goal: GridPoint) -> List[GridPoint]:
        raw = self.astar.search(start, goal)
        self.global_path = self._downsample(raw)
        return self.global_path

    def pick_local_goal(self, cur: GridPoint) -> GridPoint:
        if not self.global_path:
            raise RuntimeError("global path not available")

        # find nearest point index on global path
        best_i = min(
            range(len(self.global_path)),
            key=lambda i: self._dist_m(cur, self.global_path[i]),
        )

        horizon = self.cfg.local_horizon_m
        acc = 0.0
        for i in range(best_i, len(self.global_path) - 1):
            seg = self._dist_m(self.global_path[i], self.global_path[i + 1])
            acc += seg
            if acc >= horizon:
                return self.global_path[i + 1]
        return self.global_path[-1]

    def _downsample(self, path: List[GridPoint]) -> List[GridPoint]:
        if len(path) <= 2:
            return path
        stride = max(1, int(self.cfg.waypoint_stride_m / self.cfg.resolution))
        out = path[::stride]
        if out[-1] != path[-1]:
            out.append(path[-1])
        return out

    def _dist_m(self, a: GridPoint, b: GridPoint) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1]) * self.cfg.resolution
