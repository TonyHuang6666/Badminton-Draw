import random
import time
import math

SINGLE_GAME = 1
SINGLE_GAME_LOOP = 2
TEAM_GAME = 3
TEAM_GAME_LOOP = 4

class Draw:
    def __init__(self):
        self.number = 0  # 单项目参赛人数或队伍总数
        self.groupNumber = 0  # 分组数
        self.seededNumber = 0  # 种子数
        self.roundOneNumber = 0  # 第一轮人员总数
        self.byeRoundNumber = 0  # 第一轮轮空人员总数
        self.name = []  # 输入的人员名单的一维列表
        self.seededArray = []  # 高水平选手/种子选手一维列表
        self.randomArray = []  # 储存不重复随机数的一维列表
        self.seededName = []  # 高水平选手/种子选手名单一维列表
        self.groupArray = []  # 总抽签结果二维列表
        self.byeRoundArray = []  # 第一轮轮空选手名单二维列表
        self.roundOneArray = []  # 第一轮人员名单二维列表

    def get_time(self):
        # 获取系统当前时间并格式化
        return time.strftime("%c", time.localtime())

    def random_num_generator(self, array, num):
        # 使用随机数生成器生成不重复的随机数
        n = 0
        m = num - 1
        if array == self.seededArray:
            n = self.number
            m = self.number + self.seededNumber - 1
        
        while len(array) < num:
            random_num = random.randint(n, m)
            if random_num not in array:
                array.append(random_num)

    def divide_array(self, nums, m):
        # 将一个列表划分为 m 份
        n = len(nums)
        result = []
        i = 0
        for j in range(m):
            size = n // m + (1 if j < n % m else 0)
            result.append(nums[i:i + size])
            i += size
        return result

    def delete_same_elements(self, temp, bye_round_number):
        # 删除 temp 和 bye_round_number 中相同的元素
        result = []
        for i in range(len(temp)):
            result.append([x for x in temp[i] if x not in bye_round_number[i]])
        return result

    def select(self, temp_name_array, bye_round_number):
        # 从 temp_name_array 中均匀选择特定数量的元素
        res = [[] for _ in range(len(temp_name_array))]
        remainder = bye_round_number % len(temp_name_array)
        for i in range(len(temp_name_array)):
            indices = list(range(len(temp_name_array[i])))
            for j in range(bye_round_number // len(temp_name_array)):
                res[i].append(temp_name_array[i][indices[j]])
            if i < remainder:
                res[i].append(temp_name_array[i][indices[len(res[i])]])
        return res

    def distribute_elements(self, seeded_array, temp_name_array):
        # 将种子选手均匀分布到各个小组
        random.shuffle(seeded_array)
        num_rows = len(temp_name_array)
        for i in range(len(seeded_array)):
            row_index = i % num_rows
            temp_name_array[row_index].append(seeded_array[i])
        for i in range(num_rows):
            random.shuffle(temp_name_array[i])

    def generation(self, option):
        # 抽签分组生成函数
        with open("抽签结果.txt", "w", encoding="utf-8") as out_file:
            self.random_num_generator(self.randomArray, self.number)
            if self.seededNumber != 0:
                self.seededArray = []
                self.random_num_generator(self.seededArray, self.seededNumber)
                for i in range(len(self.seededName)):
                    self.name.append(self.seededName[i])
                self.number += self.seededNumber

            temp_name_array = self.divide_array(self.randomArray, self.groupNumber)
            temp_name_array.sort(key=len)
            self.distribute_elements(self.seededArray, temp_name_array)
            temp_name_array.sort(key=len)

            if option in [SINGLE_GAME_LOOP, TEAM_GAME_LOOP]:
                self.print_list(out_file, "总分组结果如下：", temp_name_array)

            if option in [SINGLE_GAME, TEAM_GAME]:
                # 计算附加赛人数和轮空人数
                odd_groups = [g for g in temp_name_array if len(g) % 2 != 0]
                even_groups = [g for g in temp_name_array if len(g) % 2 == 0]
                
                i = 0
                while (2 ** i) < len(even_groups) or (2 ** i) == len(even_groups):
                    if (2 ** i) > len(even_groups):
                        break
                    i += 1

                gap = len(even_groups) - 2 ** (i - 1)
                if gap != 0:
                    self.roundOneNumber = gap * len(even_groups) * 2 + (gap - 1) * len(odd_groups) * 2
                else:
                    self.roundOneNumber = 2 * len(odd_groups)

                self.byeRoundNumber = self.number - self.roundOneNumber
                self.byeRoundArray = self.select(temp_name_array, self.byeRoundNumber)
                self.roundOneArray = self.delete_same_elements(temp_name_array, self.byeRoundArray)
                self.groupArray = self.roundOneArray.copy()

                for i in range(min(len(self.groupArray), len(self.byeRoundArray))):
                    self.groupArray[i].extend(self.byeRoundArray[i])

                self.print_list(out_file, "第一轮轮空名单如下：", self.byeRoundArray)
                self.print_list(out_file, "第一轮对阵名单如下：", self.roundOneArray)
                self.print_list(out_file, "总分组结果如下：", self.groupArray)

    def print_list(self, out_file, note, array):
        # 打印名单并输出到文件
        out_file.write(note + "\n")
        print(note)
        for i, group in enumerate(array):
            group_str = f"第 {i + 1} 组({len(group)}): {' '.join([self.name[x] for x in group])}"
            print(group_str)
            out_file.write(group_str + "\n")
