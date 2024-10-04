import time
import random
from datetime import datetime

class Draw:
    def __init__(self):
        self.number = 0          # 参赛人数或队伍总数
        self.groupNumber = 0     # 分组数
        self.seededNumber = 0    # 种子数
        self.roundOneNumber = 0  # 第一轮参赛人员总数
        self.byeRoundNumber = 0  # 轮空人数
        self.name = []           # 人员名单
        self.seededArray = []    # 种子选手名单
        self.randomArray = []    # 随机数数组
        self.seededName = []     # 种子选手名字
        self.groupArray = []     # 抽签分组结果
        self.byeRoundArray = []  # 轮空人员名单
        self.roundOneArray = []  # 第一轮人员名单

    def random_num_generator(self, arr, num):
        # 生成不重复的随机数
        n, m = 0, num - 1
        if arr == self.seededArray:
            n = self.number
            m = self.number + self.seededNumber - 1

        generated = set()
        while len(generated) < num:
            random_num = random.randint(n, m)
            if random_num not in generated:
                generated.add(random_num)
                arr.append(random_num)

    def divide_array(self, nums, m):
        # 将数组划分为m个子数组
        res = [[] for _ in range(m)]
        n = len(nums)
        for j in range(m):
            for k in range(n // m + (j < n % m)):
                res[j].append(nums.pop(0))
        return res

    def print_list(self, note, arr):
        # 打印抽签结果
        print(f"{note}:")
        for i, group in enumerate(arr, 1):
            print(f"第 {i} 组({len(group)}): {', '.join([self.name[idx] for idx in group])}")

    def distribute_elements(self, seeded_array, temp_name_array):
        # 随机且均匀地将种子选手插入各组
        random.shuffle(seeded_array)
        for i, seeded in enumerate(seeded_array):
            temp_name_array[i % len(temp_name_array)].append(seeded)

        for group in temp_name_array:
            random.shuffle(group)

    def delete_same_elements(self, temp, bye_round_array):
        # 从temp数组中删除bye_round_array中的元素
        result = []
        for i, group in enumerate(temp):
            result.append([x for x in group if x not in bye_round_array[i]])
        return result

    def select(self, temp_name_array, bye_round_number):
        # 从各组中均匀抽取bye_round_number个选手
        res = [[] for _ in temp_name_array]
        remainder = bye_round_number % len(temp_name_array)
        for i in range(len(temp_name_array)):
            selected = random.sample(temp_name_array[i], bye_round_number // len(temp_name_array))
            res[i].extend(selected)
            if i < remainder:
                res[i].append(random.choice([x for x in temp_name_array[i] if x not in selected]))
        return res

    def generation(self, option):
        self.randomArray = random.sample(range(self.number), self.number)

        if self.seededNumber:
            self.seededArray = random.sample(range(self.number, self.number + self.seededNumber), self.seededNumber)
            self.name.extend(self.seededName)
            self.number += self.seededNumber

        temp_name_array = self.divide_array(self.randomArray, self.groupNumber)
        temp_name_array.sort(key=len)
        self.distribute_elements(self.seededArray, temp_name_array)

        if option in [2, 4]:  # 循环赛模式
            self.print_list("\n总分组结果如下", temp_name_array)

        if option in [1, 3]:  # 淘汰赛模式
            odd_group, even_group = 0, 0
            odd_group_num, even_group_num = 0, 0

            for group in temp_name_array:
                if len(group) % 2 != 0:
                    odd_group += 1
                    odd_group_num = len(group)
                else:
                    even_group += 1
                    even_group_num = len(group)

            i = 0
            while 2**i < even_group_num or 2**i == even_group_num:
                if 2**i > even_group_num:
                    break
                i += 1

            gap = even_group_num - 2**(i - 1)
            if gap != 0:
                self.roundOneNumber = (gap * 2 * even_group + (gap - 1) * 2 * odd_group) if odd_group_num < even_group_num else (gap * 2 * even_group + (gap + 1) * 2 * odd_group)
            else:
                self.roundOneNumber = 2 * odd_group * (odd_group_num - 2**(i - 2)) if odd_group_num < even_group_num else 2 * odd_group

            self.byeRoundNumber = self.number - self.roundOneNumber
            self.byeRoundArray = self.select(temp_name_array, self.byeRoundNumber)
            self.roundOneArray = self.delete_same_elements(temp_name_array, self.byeRoundArray)
            self.groupArray = self.roundOneArray[:]
            for i in range(min(len(self.groupArray), len(self.byeRoundArray))):
                self.groupArray[i].extend(self.byeRoundArray[i])

            self.print_list("\n第一轮轮空名单如下", self.byeRoundArray)
            self.print_list("\n第一轮对阵名单如下", self.roundOneArray)
            self.print_list("\n总分组结果如下", self.groupArray)

def get_input_from_user():
    # 获取用户输入的参数
    draw = Draw()

    # 获取参赛人数
    draw.number = int(input("请输入参赛人数: "))

    # 获取分组数
    draw.groupNumber = int(input("请输入分组数: "))

    # 获取种子选手数
    draw.seededNumber = int(input("请输入种子选手数: "))

    # 输入参赛者姓名
    print("请输入参赛者姓名，每行输入一个：")
    for i in range(draw.number):
        draw.name.append(input(f"输入选手{i+1}的名字: "))

    # 输入种子选手姓名
    if draw.seededNumber > 0:
        print("请输入种子选手姓名，每行输入一个：")
        for i in range(draw.seededNumber):
            draw.seededName.append(input(f"输入种子选手{i+1}的名字: "))

    # 选择抽签模式
    print("请选择抽签模式：1. 淘汰赛 2. 循环赛")
    option = int(input("输入模式编号: "))

    # 生成抽签结果
    draw.generation(option)

if __name__ == "__main__":
    get_input_from_user()
