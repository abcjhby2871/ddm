from hybrid_planner import HybridPlanner, PlannerConfig


def build_u_shape_map(size: int = 40):
    occ = [[0 for _ in range(size)] for _ in range(size)]

    # Build a U-shape obstacle ("凹坑").
    for y in range(8, 30):
        occ[y][10] = 1
        occ[y][28] = 1
    for x in range(10, 29):
        occ[29][x] = 1

    return occ


def main():
    occ = build_u_shape_map()
    planner = HybridPlanner(
        occ,
        PlannerConfig(resolution=1.0, local_horizon_m=6.0, waypoint_stride_m=2.0),
    )

    start = (6, 12)
    goal = (34, 12)
    global_path = planner.plan_global(start, goal)

    print(f"Global path points: {len(global_path)}")
    print(f"Start -> Goal: {global_path[0]} -> {global_path[-1]}")

    cur = start
    for step in range(6):
        local_goal = planner.pick_local_goal(cur)
        print(f"step={step}, current={cur}, local_goal={local_goal}")
        cur = local_goal
        if cur == goal:
            break


if __name__ == "__main__":
    main()
