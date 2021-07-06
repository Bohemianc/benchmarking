import matplotlib.pyplot as plt

lab_mem = "内存大小（MB）"
lab_time = "时间（s）"

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


def plot_data_size(data_size: list, run_time: list, mem_size: list, fn: str):
    fig, ax1 = plt.subplots()

    color1 = 'tab:blue'
    ax1.set_xlabel('数据量', fontsize=14)
    ax1.set_ylabel(lab_time, color=color1, fontsize=14)
    ax1.plot(data_size, run_time, color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    for x in ax1.get_xticklabels():  # 获取x轴上所有坐标，并设置字号
        x.set_fontsize(14)
    for y in ax1.get_yticklabels():
        y.set_fontsize(14)

    ax2 = ax1.twinx()  # 创建共用x轴的第二个y轴

    color2 = 'tab:orange'
    ax2.set_ylabel(lab_mem, color=color2, fontsize=14)
    ax2.plot(data_size, mem_size, color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)

    for y in ax2.get_yticklabels():
        y.set_fontsize(14)

    fig.tight_layout()
    plt.savefig(fn)
    plt.show()


def plot_rule_length(rls: list, run_time: list, mem_size: list, fn: str):
    fig, ax1 = plt.subplots()

    color1 = 'tab:blue'
    ax1.set_xlabel('规则长度', fontsize=14)
    ax1.set_ylabel(lab_time, color=color1, fontsize=14)
    ax1.plot(rls, run_time, color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    for x in ax1.get_xticklabels():  # 获取x轴上所有坐标，并设置字号
        x.set_fontsize(14)
    for y in ax1.get_yticklabels():
        y.set_fontsize(14)

    ax1.set_ylim([0, 70])
    ax2 = ax1.twinx()  # 创建共用x轴的第二个y轴
    ax2.set_ylim([500, 1600])
    # axes = plt.gca()
    # axes.set_ylim([30,90])
    color2 = 'tab:orange'
    ax2.set_ylabel(lab_mem, color=color2, fontsize=14)
    ax2.plot(rls, mem_size, color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)

    for y in ax2.get_yticklabels():
        y.set_fontsize(14)

    fig.tight_layout()
    plt.savefig(fn)
    plt.show()


def plot_rule_depth(rds: list, run_time: list, mem_size: list, fn: str):
    fig, ax1 = plt.subplots()

    color1 = 'tab:blue'
    ax1.set_xlabel('规则深度', fontsize=14)
    ax1.set_ylabel(lab_time, color=color1, fontsize=14)
    ax1.plot(rds, run_time, color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    for x in ax1.get_xticklabels():  # 获取x轴上所有坐标，并设置字号
        x.set_fontsize(14)
    for y in ax1.get_yticklabels():
        y.set_fontsize(14)

    ax1.set_ylim([0, 70])
    ax2 = ax1.twinx()  # 创建共用x轴的第二个y轴
    ax2.set_ylim([500, 1600])
    # axes = plt.gca()
    # axes.set_ylim([30,90])
    color2 = 'tab:orange'
    ax2.set_ylabel(lab_mem, color=color2, fontsize=14)
    ax2.plot(rds, mem_size, color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)

    for y in ax2.get_yticklabels():
        y.set_fontsize(14)

    fig.tight_layout()
    plt.savefig(fn)
    plt.show()


if __name__ == "__main__":
    data_size = ["112MB", "224MB", "341MB", "451MB"]
    run_time = [24, 40, 69, 90]
    mem_size = [792, 1316, 1542, 1593]
    # plot_data_size(data_size, run_time, mem_size, "1.png")

    # rls = ["2", "3", "4"]
    # run_time = [20, 19, 20]
    # mem_size = [710, 733, 693]
    rls = ["2", "5", "10"]
    run_time = [14.511, 14.903, 16.384]
    mem_size = [632, 772, 859]
    # plot_rule_length(rls, run_time, mem_size, "2.png")

    # rds = rls
    # run_time = [19, 18, 20]
    # mem_size = [746, 653, 698]
    rds = ["1", "5", "10"]
    run_time = [13.641, 13.901, 15.852]
    mem_size = [731, 577, 639]
    plot_rule_depth(rds, run_time, mem_size, "3.png")
