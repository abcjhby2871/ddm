import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

i = 1 # 2,3
df = pd.read_csv(f"exp{i}.csv")

# 显示数据的前几行，检查数据结构
print("数据预览：")
print(df.head())

# 2. 缺失值处理
# 查看缺失值
print("\n缺失值统计：")
print(df.isnull().sum())

# 可视化缺失值
plt.figure(figsize=(10, 6))
sns.heatmap(df.isnull(), cbar=False, cmap="viridis", yticklabels=False)
plt.title("缺失值热图")
plt.show()

# 对数值型列填充均值，对类别型列填充众数
df['reaction_time'].fillna(df['reaction_time'].mean(), inplace=True)
df['value_difference'].fillna(df['value_difference'].mean(), inplace=True)
df['CV'].fillna(df['CV'].mean(), inplace=True)

df['category'].fillna(df['category'].mode()[0], inplace=True)
df['correct'].fillna(df['correct'].mode()[0], inplace=True)

# 缺失值处理后，查看缺失值统计
print("\n缺失值处理后统计：")
print(df.isnull().sum())

# 可视化缺失值处理后的结果
plt.figure(figsize=(10, 6))
sns.heatmap(df.isnull(), cbar=False, cmap="viridis", yticklabels=False)
plt.title("缺失值处理后的热图")
plt.show()

# 3. 异常值处理
# 使用箱型图检测异常值
plt.figure(figsize=(10, 6))
sns.boxplot(data=df[['reaction_time', 'value_difference', 'CV']])
plt.title("箱型图 - 异常值检测")
plt.show()

# 使用标准差法检测异常值
for col in ['reaction_time', 'value_difference', 'CV']:
    mean = df[col].mean()
    std = df[col].std()
    # 超过3个标准差的值被视为异常值
    df = df[df[col].between(mean - 3*std, mean + 3*std)]

# 处理异常值后，绘制处理后的箱型图
plt.figure(figsize=(10, 6))
sns.boxplot(data=df[['reaction_time', 'value_difference', 'CV']])
plt.title("箱型图 - 异常值处理后的数据")
plt.show()

# 4. 保存清洗后的数据
df.to_csv(f"cleaned_exp{i}.csv", index=False)

# 输出清洗后的数据
print("清洗后的数据预览：")
print(df.head())
