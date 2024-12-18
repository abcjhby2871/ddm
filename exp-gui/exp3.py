from psychopy import visual, core, event
import random
import csv
import os
# 创建窗口
win = visual.Window(size=(1600, 800), color='white', units='pix')
trial_num = 1
if os.path.isfile("data_exp3.csv"):
    with open("data_exp3.csv", "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        # 获取最后一行的 trial 值
        last_trial = 0
        for row in reader:
            last_trial = int(row["experiment_id"])  # 读取最后一行的trial编号
else:
    last_trial = 0  # 如果文件不存在，则从0开始

def save_data(data, filename="data_exp3.csv"):
    """追加实验数据到CSV文件，确保trial编号接着上次继续"""
    keys = ["experiment_id", "correct", "reaction_time", "value_difference", "CV", "category"]
    # 追加数据到文件
    with open(filename, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        # 如果文件不存在或为空，写入表头
        if not os.path.isfile(filename) or os.path.getsize(filename) == 0:
            writer.writeheader()
        writer.writerows(data)
experiment_data = []
# 设定实验参数
colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'pink', 'cyan', 'brown', 'gray', 'black', 'white']  # 示例颜色
color_values = list(range(1, 13))  # 1 到 12 的点值


def display_color_spectrum():
    square_size = 50
    margin = 20
    start_x = -(square_size + margin) * 5 - 35
    y_pos = 0

    # 随机选择箭头方向（0 = 从小到大，1 = 从大到小）
    random_order = random.choice([True, False])  # True表示从小到大，False表示从大到小
    arrow_length = 300 
    arrow_width = 20
    arrow_body = visual.Line(win, start=(-arrow_length/2 - 260, -100), end=(arrow_length/2 + 260, -100), lineColor='red', lineWidth=5)
    
    # 随机决定点值是从小到大还是从大到小
    points = list(range(1, 13))
    # 根据random_order建立颜色和值的关系
    if random_order:
        points.sort()  # 从小到大
        arrow_head = visual.Polygon(win, edges=3, size=(arrow_width, arrow_width), fillColor='red', lineColor='black', pos=(arrow_length/2 + 260, -100))
        rotation_angle = 90
        arrow_head.ori = rotation_angle
        color_value_mapping = dict(zip(color_values, colors))
    else:
        points.sort(reverse=True)  # 从大到小
        arrow_head = visual.Polygon(win, edges=3, size=(arrow_width, arrow_width), fillColor='red', lineColor='black', pos=(-arrow_length/2 - 260, -100))
        rotation_angle = -90
        arrow_head.ori = rotation_angle
        color_value_mapping = dict(zip(color_values, colors[::-1]))
    arrow_head.draw()
    arrow_body.draw()
    # 在箭头下方显示这些点值
    text_stimuli = []
    y_pos = -150
    for i, point in enumerate(points):
        text = visual.TextStim(win, text=str(point), pos=(i * 60 - 350, y_pos), height=30, color='black')  # 每个数字的位置稍微间隔
        text_stimuli.append(text)

    # 在最上方显示一段文字
    header_text = "12种不同颜色组成的色谱图，颜色的值如下所示"
    header = visual.TextStim(win, text=header_text, pos=(-100, 150), height=30, color='black')

    # 绘制图形
    header.draw()  # 绘制最上方的文字
    for text in text_stimuli:
        text.draw()
    
    # 绘制颜色谱
    for i in range(12):
        square = visual.Rect(win, width=square_size, height=square_size, fillColor=colors[i], lineColor='black')
        x_pos = start_x + (square_size + margin) * i
        square.pos = (x_pos, 0)
        square.draw()
        # 显示点值
        text = visual.TextStim(win, text=str(color_values[i]), pos=(x_pos, y_pos - square_size / 2 - 20), height=20)
        text.draw()

    # 更新窗口，显示颜色、点值和箭头
    win.flip()

# 提醒页面
def enter_reminder_phase():
    reminder_text = "接下来将进入测试阶段，请做好准备！"
    reminder = visual.TextStim(win, text=reminder_text, pos=(-50, 0), height=30, color='black')
    reminder.draw()
    win.flip()

    # 等待 3 秒
    core.wait(3)

# 中值、低值和高值刺激的生成函数
def generate_stimulus_pair(base_values, delta=4):
    """
    生成一个刺激对，包括：
    1. 中值刺激（base_values）
    2. 低值刺激（base_values - delta）
    3. 高值刺激（base_values + delta）
    """
    hxh = random.choice([True, False])
    if hxh:
        low_values = [max(1, value - random.randint(1, delta)) for value in base_values]  # 避免低于1
        high_values = [min(value + 1, 12) for value in low_values]  # 避免高于12
    else:
        low_values = [min(12, value + random.randint(1, delta)) for value in base_values]  # 避免低于1
        high_values = [max(value - 1, 1) for value in low_values]  # 避免高于12
    return low_values, base_values, high_values

# 显示测试阶段刺激的函数
def display_testing_stimulus_train(left_values, right_values):
    square_size = 50
    margin = 10
    # 左右两边的位置
    left_x_pos = -360
    right_x_pos = 140
    y_pos_top = 27  # 左右两边顶部的Y坐标
    y_pos_bottom = -27  # 左右两边底部的Y坐标
    # 添加任务说明文本
    instruction_text = "请对比左右两边的方块值，按方向键选择哪一边的值更大（左箭头表示左边更大，右箭头表示右边更大）。"
    instruction = visual.TextStim(win, text=instruction_text, pos=(-510, 250), height=30, color='black')
    instruction.draw()

    # 创建左侧和右侧的刺激
    for i, (left_value, right_value) in enumerate(zip(left_values, right_values)):
        # 计算左边和右边每个方块的坐标
        if i < 3:  # 第一行
            left_pos = (left_x_pos + (square_size + margin) * i, y_pos_top)
            right_pos = (right_x_pos + (square_size + margin) * i, y_pos_top)
        else:  # 第二行
            left_pos = (left_x_pos + (square_size + margin) * (i - 3), y_pos_bottom)
            right_pos = (right_x_pos + (square_size + margin) * (i - 3), y_pos_bottom)

        # 左侧
        left_square = visual.Rect(win, width=square_size, height=square_size, fillColor=colors[left_value-1], lineColor='black')
        left_square.pos = left_pos
        left_square.draw()
        
        # 右侧
        right_square = visual.Rect(win, width=square_size, height=square_size, fillColor=colors[right_value-1], lineColor='black')
        right_square.pos = right_pos
        right_square.draw()

        # 显示左边和右边的小块值
        left_text = visual.TextStim(win, text=str(left_value), pos=(left_pos[0], left_pos[1] - square_size / 2 - 20), height=20)
        right_text = visual.TextStim(win, text=str(right_value), pos=(right_pos[0], right_pos[1] - square_size / 2 - 20), height=20)
        left_text.draw()
        right_text.draw()

    # 在窗口显示测试刺激
    win.flip()
    # 等待键盘事件，并判断是否正确
    correct_response = 'left' if sum(left_values) > sum(right_values) else 'right'
    while True:
        keys = event.getKeys()
        if 'escape' in keys:  # 退出实验
            win.close()
            core.quit()
        
        if 'left' in keys and correct_response == 'left':
            feedback = "正确！"
            feedback_text = visual.TextStim(win, text=feedback, pos=(0, -200), height=30, color='green')
            feedback_text.draw()
            win.flip()
            core.wait(1)  # 显示正确反馈1秒
            break
        elif 'right' in keys and correct_response == 'right':
            feedback = "正确！"
            feedback_text = visual.TextStim(win, text=feedback, pos=(0, -200), height=30, color='green')
            feedback_text.draw()
            win.flip()
            core.wait(1)  # 显示正确反馈1秒
            break
        elif 'left' in keys or 'right' in keys:
            feedback = "错误！"
            feedback_text = visual.TextStim(win, text=feedback, pos=(0, -200), height=30, color='red')
            feedback_text.draw()
            win.flip()
            core.wait(1)  # 显示错误反馈1秒
            break

def display_testing_stimulus_test(left_values, right_values, num):
    correct_response = 'left' if sum(left_values) > sum(right_values) else 'right'
    if sum(left_values) == sum(right_values):
        return 
    diff = abs(sum(left_values) - sum(right_values))
    total_value = sum(left_values)
    if total_value <= 24:
        category = "low"
    elif total_value <= 48:
        category = "mid"
    elif total_value <= 72:
        category = "high"

    CV = True
    if CV == True:
        message = visual.TextStim(win, text=f"Category: {category}", color="black", height=30)
        # 显示文本
        message.draw()
        win.flip()
        # 等待一段时间然后关闭
        core.wait(2)
    square_size = 50
    margin = 7
    # 左右两边的位置
    left_x_pos = -360
    right_x_pos = 140
    y_pos_top = 27  # 左右两边顶部的Y坐标
    y_pos_bottom = -27  # 左右两边底部的Y坐标
    # 添加任务说明文本
    instruction_text = "请对比左右两边的方块值，按方向键选择哪一边的值更大（左箭头表示左边更大，右箭头表示右边更大）。"
    instruction = visual.TextStim(win, text=instruction_text, pos=(-510, 250), height=30, color='black')
    instruction.draw()
    trial_clock = core.Clock()
    # 创建左侧和右侧的刺激
    for i, (left_value, right_value) in enumerate(zip(left_values, right_values)):
        # 计算左边和右边每个方块的坐标
        if i < 3:  # 第一行
            left_pos = (left_x_pos + (square_size + margin) * i, y_pos_top)
            right_pos = (right_x_pos + (square_size + margin) * i, y_pos_top)
        else:  # 第二行
            left_pos = (left_x_pos + (square_size + margin) * (i - 3), y_pos_bottom)
            right_pos = (right_x_pos + (square_size + margin) * (i - 3), y_pos_bottom)

        # 左侧
        left_square = visual.Rect(win, width=square_size, height=square_size, fillColor=colors[left_value-1], lineColor='black')
        left_square.pos = left_pos
        left_square.draw()
        
        # 右侧
        right_square = visual.Rect(win, width=square_size, height=square_size, fillColor=colors[right_value-1], lineColor='black')
        right_square.pos = right_pos
        right_square.draw()

        # 显示左边和右边的小块值
        left_text = visual.TextStim(win, text=str(left_value), pos=(left_pos[0], left_pos[1] - square_size / 2 - 20), height=20)
        right_text = visual.TextStim(win, text=str(right_value), pos=(right_pos[0], right_pos[1] - square_size / 2 - 20), height=20)
        left_text.draw()
        right_text.draw()

    # 在窗口显示测试刺激
    win.flip()
    # 等待键盘事件，并判断是否正确
    trial_clock.reset()
    correct = None
    correct_response = 'left' if sum(left_values) > sum(right_values) else 'right'
    while True:
        keys = event.getKeys()
        if 'escape' in keys:  # 退出实验
            win.close()
            core.quit()
        
        if 'left' in keys and correct_response == 'left':
            correct = True
            # feedback = "正确！"
            # feedback_text = visual.TextStim(win, text=feedback, pos=(0, -200), height=30, color='green')
            # feedback_text.draw()
            # win.flip()
            core.wait(2)  # 显示正确反馈1秒
            break
        elif 'right' in keys and correct_response == 'right':
            correct = True
            # feedback = "正确！"
            # feedback_text = visual.TextStim(win, text=feedback, pos=(0, -200), height=30, color='green')
            # feedback_text.draw()
            # win.flip()
            core.wait(2)  # 显示正确反馈1秒
            break
        elif 'left' in keys or 'right' in keys:
            correct = False
            # feedback = "错误！"
            # feedback_text = visual.TextStim(win, text=feedback, pos=(0, -200), height=30, color='red')
            # feedback_text.draw()
            # win.flip()
            core.wait(2)  # 显示错误反馈1秒
            break
    reaction_time = trial_clock.getTime()
    experiment_data.append({
        'experiment_id': num + last_trial,
        'correct': correct,
        'reaction_time': reaction_time,  # 时间单位为秒
        'value_difference': diff,
        'CV': CV,
        'category':  category
        })
    core.wait(0.5)  # 短暂等待进入下一个试次
# 实验开始函数
def run_experiment_train():
    display_color_spectrum()
    # 展示测试阶段
    enter_reminder_phase()
    # 显示左侧和右侧刺激
    for hxh in range(1, 200):
        base_values = [random.randint(1, 12) for _ in range(6)]
        delta = random.randint(1, 8)
        low_values, _, high_values = generate_stimulus_pair(base_values, delta)
        print(low_values)
        display_testing_stimulus_train(low_values, high_values)
    
    # 计时等待
    core.wait(10)

def run_experiment_test():
    display_color_spectrum()
    core.wait(10)
    # 展示测试阶段
    enter_reminder_phase()
    # 显示左侧和右侧刺激
    num = 1
    for hxh in range(1, 20):
        base_values = [random.randint(1, 12) for _ in range(6)]
        delta = random.randint(1, 8)
        low_values, _, high_values = generate_stimulus_pair(base_values, delta)
        print(low_values)
        display_testing_stimulus_test(low_values, high_values,num)
        num += 1
    save_data(experiment_data)
    # 计时等待
    core.wait(10)

# 运行实验
run_experiment_test()

# 关闭窗口
win.close()
core.quit()



