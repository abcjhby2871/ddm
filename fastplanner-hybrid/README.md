# Fast-Planner 全局+局部规划衔接示例

这个目录提供一个可运行的最小化原型，用于演示你描述的方案：

1. 先用 A* 在已知障碍栅格地图上求全局路径。
2. 在飞行过程中，沿全局路径滚动选取局部目标点（local goal）。
3. 把 local goal 交给 Fast-Planner 现有的局部轨迹优化器。

> 注意：这里是独立原型，便于验证算法逻辑；集成到 `HKUST-Aerial-Robotics/Fast-Planner` 时，需要把同样逻辑迁移到 ROS 节点/规划管理器。

## 文件说明

- `hybrid_planner.py`
  - `GridAStar`: 全局路径搜索。
  - `HybridPlanner`: 全局路径降采样 + 局部目标点选择。
- `example_usage.py`
  - 构造一个 U 形（凹坑）障碍示例并演示滚动 local goal。

## 运行

```bash
cd fastplanner-hybrid
python example_usage.py
```

## 集成到 Fast-Planner 的建议改造点

1. **新增全局规划模块**
   - 输入：ESDF/占据栅格、起点、终点。
   - 输出：全局路标序列（世界坐标）。
2. **在 replanning 回调中加入“路径投影 + 前视取点”**
   - 用当前无人机位置投影到全局路径最近点索引 `i*`。
   - 沿路径累计弧长到 `horizon`，得到 local goal。
3. **局部规划失败回退策略**
   - 若局部优化失败，不立即放弃；尝试缩短 horizon 或回退到 `i* + k` 的次优候选点。
4. **状态机联动**
   - 到达终点阈值内后切换完成状态。
   - 若偏离全局路径过大（比如被扰动推离），触发全局重规划。

这套方式可以显著降低在凹形障碍附近“局部最优陷阱”的概率。
