from psychopy import visual, event, core, gui
import random
import os
import csv

# 初始化窗口
win = visual.Window([1600, 800], fullscr=False, color='white', units='pix')

# 如果文件存在，读取当前的 trial 编号，以便从最后一个编号继续
if os.path.isfile("data_exp2.csv"):
    with open("data_exp2.csv", "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        # 获取最后一行的 trial 值
        last_trial = 0
        for row in reader:
            last_trial = int(row["trial"])  # 读取最后一行的trial编号
else:
    last_trial = 0  # 如果文件不存在，则从0开始

def save_data(data, filename="data_exp2.csv"):
    """追加实验数据到CSV文件，确保trial编号接着上次继续"""
    keys = ["trial", "pic1", "pic2", "chosen_pic", "reaction_time", "rating_diff", "category", "hint", "correct"]

    # 追加数据到文件
    with open(filename, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        # 如果文件不存在，写入表头
        if not os.path.isfile(filename) or os.path.getsize(filename) == 0:
            writer.writeheader()
        writer.writerows(data)

# 第一阶段：评分任务
def phase_1():
    instructions = visual.TextStim(win, text="请对以下艺术图片进行评分，范围从0到10。点击'非常不喜欢'按钮可选择不喜欢该艺术图。", 
                                   color='black', height=20, pos=(-190, 300))

    # 创建Slider用于评分
    rating_slider = visual.Slider(win, ticks=list(range(11)), labels=[str(i) for i in range(11)], 
                                  startValue=None, pos=(0, -100), size=(600, 50), granularity=1, style='rating',
                                  markerColor='red', lineColor='black', labelColor='black')

    # 创建“宁愿不吃”按钮
    no_eat_button = visual.Rect(win, width=150, height=50, fillColor='red', pos=(0, -240))
    no_eat_text = visual.TextStim(win, text="非常不喜欢", color='white', pos=(0, -240), height=20)

    snack_ratings = {}

    snack_images = []
    for i in range(1, 6):
        # 尝试加载 .png 文件，如果不存在则尝试 .jpg
        if os.path.isfile(f"snacks/{i}.png"):
            snack_images.append(f"{i}.png")
        elif os.path.isfile(f"snacks/{i}.jpg"):
            snack_images.append(f"{i}.jpg")


    for snack in snack_images:
        instructions.draw()

        # 加载当前零食图片
        snack_image = visual.ImageStim(win, image=os.path.join(r"art", snack), pos=(0, 100), size=(300, 300))
        snack_image.draw()
        win.flip()
        # 重置Slider和按钮
        rating_slider.reset()

        while True:
            instructions.draw()
            rating_slider.draw()
            no_eat_button.draw()
            no_eat_text.draw()
            snack_image.draw()
            win.flip()

            # 检测按键事件
            keys = event.getKeys()

            # 检测退出按键
            if 'escape' in keys:
                core.quit()

            # 鼠标事件
            mouse = event.Mouse(win=win)
            if mouse.isPressedIn(no_eat_button):
                snack_ratings[snack] = "非常不喜欢"
                break

            # 检测Slider评分并按回车键确认
            if 'return' in keys and rating_slider.getRating() is not None:
                snack_ratings[snack] = rating_slider.getRating()
                break

        core.wait(0.5)  # 等待短暂时间进入下一个试次

    return snack_ratings

# 中间休息页面
def rest_screen():
    rest_text = visual.TextStim(win, text="稍事休息，实验将在1分钟后继续。", color='black', height=40, pos=(-120, 0))
    rest_text.draw()
    win.flip()
    core.wait(6)  # 休息1分钟


def phase_2_train(snack_ratings):
    instructions = visual.TextStim(win, text="本阶段为训练阶段！\n 请选择你更喜欢的艺术图片，使用左右箭头键选择。", color='black', height=20, pos=(0, 250))

    # 按评分分组
    high_value = [snack for snack, rating in snack_ratings.items() if isinstance(rating, (int, float)) and rating > 6.66]
    mid_value = [snack for snack, rating in snack_ratings.items() if isinstance(rating, (int, float)) and 3.34 <= rating <= 6.66]
    low_value = [snack for snack, rating in snack_ratings.items() if isinstance(rating, (int, float)) and rating < 3.34]

    snack_categories = {
        "high": high_value,
        "mid": mid_value,
        "low": low_value
    }

    # 更新配对生成逻辑
    snack_pairs = []

    # 同类别配对：确保 rating 值不同
    for category, snacks in snack_categories.items():
        random.shuffle(snacks)
        for i in range(len(snacks)):
            for j in range(i + 1, len(snacks)):
                if snack_ratings[snacks[i]] != snack_ratings[snacks[j]]:
                    snack_pairs.append((snacks[i], snacks[j], category))

    random.shuffle(snack_pairs)

    # 训练模式不保存数据，只提供反馈
    trial_clock = core.Clock()

    for trial_num, (snack1, snack2, category) in enumerate(snack_pairs[:270]):
        hint = True  # 随机决定是否显示提示界面

        if hint:
            category_text = {"high": "高值艺术图片对比", "mid": "中值艺术图片对比", "low": "低值艺术图片对比"}[category]
            category_instructions = visual.TextStim(win, text=category_text, color='black', height=30, pos=(0, 0))
            category_instructions.draw()
            win.flip()
            core.wait(2)  # 提示页面显示2秒

        snack1_image = visual.ImageStim(win, image=os.path.join(r"art", snack1), pos=(-200, 0), size=(200, 200))
        snack2_image = visual.ImageStim(win, image=os.path.join(r"art", snack2), pos=(200, 0), size=(200, 200))
        
        instructions.draw()
        snack1_image.draw()
        snack2_image.draw()
        win.flip()

        # 等待选择
        trial_clock.reset()
        keys = event.waitKeys(keyList=['left', 'right', 'escape'])
        reaction_time = trial_clock.getTime()

        if 'escape' in keys:
            core.quit()

        chosen_snack = snack1 if keys[0] == 'left' else snack2

        # 计算评分差值
        rating_diff = abs(snack_ratings[snack1] - snack_ratings[snack2]) if isinstance(snack_ratings[snack1], (int, float)) and isinstance(snack_ratings[snack2], (int, float)) else None

        # 判断是否正确（示例规则：选择评分高的为正确）
        correct = None
        if isinstance(snack_ratings[snack1], (int, float)) and isinstance(snack_ratings[snack2], (int, float)):
            correct = (chosen_snack == snack1 and snack_ratings[snack1] > snack_ratings[snack2]) or \
                      (chosen_snack == snack2 and snack_ratings[snack2] > snack_ratings[snack1])

        # 显示反馈
        feedback_text = "选择正确！" if correct else "选择错误！"
        feedback = visual.TextStim(win, text=feedback_text, color='black', height=30, pos=(0, 0))
        feedback.draw()
        win.flip()
        core.wait(1)  # 显示反馈1秒

        core.wait(0.5)  # 短暂等待进入下一个试次

# 第二阶段：二元选择任务
def phase_2_CV(snack_ratings):
    instructions = visual.TextStim(win, text="请选择你更喜欢的艺术图片，使用左右箭头键选择。", color='black', height=20, pos=(0, 250))

    # 按评分分组
    high_value = [snack for snack, rating in snack_ratings.items() if isinstance(rating, (int, float)) and rating > 6.66]
    mid_value = [snack for snack, rating in snack_ratings.items() if isinstance(rating, (int, float)) and 3.34 <= rating <= 6.66]
    low_value = [snack for snack, rating in snack_ratings.items() if isinstance(rating, (int, float)) and rating < 3.34]

    snack_categories = {
        "high": high_value,
        "mid": mid_value,
        "low": low_value
    }

    # 更新配对生成逻辑
    snack_pairs = []

    # 同类别配对：确保 rating 值不同
    for category, snacks in snack_categories.items():
        random.shuffle(snacks)
        for i in range(len(snacks)):
            for j in range(i + 1, len(snacks)):
                if snack_ratings[snacks[i]] != snack_ratings[snacks[j]]:
                    snack_pairs.append((snacks[i], snacks[j], category))

    random.shuffle(snack_pairs)

    # 实验数据存储
    experiment_data = []
    trial_clock = core.Clock()

    for trial_num, (snack1, snack2, category) in enumerate(snack_pairs[:270]):
        hint = True  # 随机决定是否显示提示界面

        if hint:
            category_text = {"high": "高值艺术图片对比", "mid": "中值艺术图片对比", "low": "低值艺术图片对比"}[category]
            category_instructions = visual.TextStim(win, text=category_text, color='black', height=30, pos=(0, 0))
            category_instructions.draw()
            win.flip()
            core.wait(2)  # 提示页面显示2秒

        snack1_image = visual.ImageStim(win, image=os.path.join(r"art", snack1), pos=(-200, 0), size=(200, 200))
        snack2_image = visual.ImageStim(win, image=os.path.join(r"art", snack2), pos=(200, 0), size=(200, 200))
        
        instructions.draw()
        snack1_image.draw()
        snack2_image.draw()
        win.flip()

        # 等待选择
        trial_clock.reset()
        keys = event.waitKeys(keyList=['left', 'right', 'escape'])
        reaction_time = trial_clock.getTime()

        if 'escape' in keys:
            core.quit()

        chosen_snack = snack1 if keys[0] == 'left' else snack2

        # 计算评分差值
        rating_diff = abs(snack_ratings[snack1] - snack_ratings[snack2]) if isinstance(snack_ratings[snack1], (int, float)) and isinstance(snack_ratings[snack2], (int, float)) else None

        # 判断是否正确（示例规则：选择评分高的为正确）
        correct = None
        if isinstance(snack_ratings[snack1], (int, float)) and isinstance(snack_ratings[snack2], (int, float)):
            correct = (chosen_snack == snack1 and snack_ratings[snack1] > snack_ratings[snack2]) or \
                      (chosen_snack == snack2 and snack_ratings[snack2] > snack_ratings[snack1])

        # 保存数据
        experiment_data.append({
            "trial": trial_num + 1 + last_trial,
            "pic1": snack1,
            "pic2": snack2,
            "chosen_pic": chosen_snack,
            "reaction_time": reaction_time,
            "rating_diff": rating_diff,
            "category": category,
            "hint": hint,
            "correct": correct
        })

        core.wait(0.5)  # 短暂等待进入下一个试次

    save_data(experiment_data)

def phase_2_MV(snack_ratings):
    instructions = visual.TextStim(win, text="请选择你更喜欢的艺术图片，使用左右箭头键选择。", color='black', height=20, pos=(0, 250))

    # 按评分分组
    high_value = [snack for snack, rating in snack_ratings.items() if isinstance(rating, (int, float)) and rating > 6.66]
    mid_value = [snack for snack, rating in snack_ratings.items() if isinstance(rating, (int, float)) and 3.34 <= rating <= 6.66]
    low_value = [snack for snack, rating in snack_ratings.items() if isinstance(rating, (int, float)) and rating < 3.34]

    snack_categories = {
        "high": high_value,
        "mid": mid_value,
        "low": low_value
    }

    # 更新配对生成逻辑
    snack_pairs = []

    # 同类别配对：确保 rating 值不同
    for category, snacks in snack_categories.items():
        random.shuffle(snacks)
        for i in range(len(snacks)):
            for j in range(i + 1, len(snacks)):
                if snack_ratings[snacks[i]] != snack_ratings[snacks[j]]:
                    snack_pairs.append((snacks[i], snacks[j], category))

    random.shuffle(snack_pairs)

    # 实验数据存储
    experiment_data = []
    trial_clock = core.Clock()

    for trial_num, (snack1, snack2, category) in enumerate(snack_pairs[:270]):
        hint = False

        if hint:
            category_text = {"high": "高值艺术图片对比", "mid": "中值艺术图片对比", "low": "低值艺术图片对比"}[category]
            category_instructions = visual.TextStim(win, text=category_text, color='black', height=30, pos=(0, 0))
            category_instructions.draw()
            win.flip()
            core.wait(2)  # 提示页面显示2秒

        snack1_image = visual.ImageStim(win, image=os.path.join(r"art", snack1), pos=(-200, 0), size=(200, 200))
        snack2_image = visual.ImageStim(win, image=os.path.join(r"art", snack2), pos=(200, 0), size=(200, 200))
        
        instructions.draw()
        snack1_image.draw()
        snack2_image.draw()
        win.flip()

        # 等待选择
        trial_clock.reset()
        keys = event.waitKeys(keyList=['left', 'right', 'escape'])
        reaction_time = trial_clock.getTime()

        if 'escape' in keys:
            core.quit()

        chosen_snack = snack1 if keys[0] == 'left' else snack2

        # 计算评分差值
        rating_diff = abs(snack_ratings[snack1] - snack_ratings[snack2]) if isinstance(snack_ratings[snack1], (int, float)) and isinstance(snack_ratings[snack2], (int, float)) else None

        # 判断是否正确（示例规则：选择评分高的为正确）
        correct = None
        if isinstance(snack_ratings[snack1], (int, float)) and isinstance(snack_ratings[snack2], (int, float)):
            correct = (chosen_snack == snack1 and snack_ratings[snack1] > snack_ratings[snack2]) or \
                      (chosen_snack == snack2 and snack_ratings[snack2] > snack_ratings[snack1])

        # 保存数据
        experiment_data.append({
            "trial": trial_num + 1 + last_trial,
            "pic1": snack1,
            "pic2": snack2,
            "chosen_pic": chosen_snack,
            "reaction_time": reaction_time,
            "rating_diff": rating_diff,
            "category": category,
            "hint": hint,
            "correct": correct
        })

        core.wait(0.5)  # 短暂等待进入下一个试次

    save_data(experiment_data)

# 运行实验
def run_experiment():
    snack_ratings = phase_1()  # 第一阶段
    rest_screen()  # 中间休息页面
#    phase_2_train(snack_ratings)
    phase_2_CV(snack_ratings)  # 第二阶段

run_experiment()
win.close()
