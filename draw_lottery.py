# -*- coding: utf-8 -*-
"""
由 22 届深大羽协会长 Tony Huang 编写的通用快速抽签分组程序（Python 版）。
本文件是从原单文件 C++ 版本等价转换而来，尽量保持交互与输出一致：
- 支持：单项赛/团体赛（淘汰/循环）、设立种子、单双打名单录入、分组、首轮轮空/对阵计算、结果写入“抽签结果.txt”。
- 交互提示、中文输出、Excel 友好格式打印的交互保持与原逻辑一致。

注意：原 C++ 版本中的“首轮轮空/对阵人数计算”算法与分组人数结构相关，
此处严格按原始公式与流程复刻，未做规则学上的纠偏或优化，仅做 Python 语法层面等价实现。
"""

import sys
import random
from datetime import datetime

# 选项常量
singleGame      = 1  # 单项赛(淘汰赛)
singleGameLoop  = 2  # 单项赛(循环赛)
teamGame        = 3  # 团体赛(淘汰赛)
teamGameLoop    = 4  # 团体赛(循环赛)


def count_non_empty(strings):
    return sum(1 for s in strings if s)


class Draw:
    def __init__(self):
        # 基本参数
        self.number = 0           # 非种子人数/队伍数（初始值；若设种子，后续会累加）
        self.groupNumber = 0      # 分组数
        self.seededNumber = 0     # 种子数

        # 计算中间量
        self.roundOneNumber = 0
        self.byeRoundNumber = 0

        # 名单与索引
        self.name = []            # 总名单（先录入非种子，若设种子则在末尾追加）
        self.seededName = []      # 种子名单（与 name 结构一致，只在设种子时使用）
        self.seededArray = []     # 种子在总名单中的索引
        self.groupArray = []      # 总分组（首轮对阵 + 轮空合并）
        self.byeRoundArray = []   # 首轮轮空名单（按组分配）
        self.roundOneArray = []   # 首轮对阵名单（按组分配）

    @staticmethod
    def _divide_array(nums, m):
        """
        将一维列表 nums 按顺序均匀切成 m 份，任意相邻两份的元素数最多相差 1。
        等价于原 C++: divideArray(nums, m)
        """
        n = len(nums)
        res = [[] for _ in range(m)]
        i = 0
        for j in range(m):
            take = n // m + (1 if j < (n % m) else 0)
            for _ in range(take):
                res[j].append(nums[i])
                i += 1
        return res

    @staticmethod
    def _find_in_vec(num, vec):
        return any(v == num for v in vec)

    @staticmethod
    def _delete_same_elements(temp, bye_arr):
        """
        等价于原 C++: deleteSameElements
        对每一行做 temp[i] - bye_arr[i]（集合差，但保序且逐元素判断）
        """
        result = [[] for _ in range(len(temp))]
        for i in range(len(temp)):
            if len(temp[i]) != len(bye_arr[i]):
                for x in temp[i]:
                    if not Draw._find_in_vec(x, bye_arr[i]):
                        result[i].append(x)
        return result

    @staticmethod
    def _select_evenly(tempNameArray, byeRoundNumber):
        """
        等价于原 C++: Select
        从每一行的前若干元素“均匀地”取数，行与行之间尽量平均分配。
        注意：该函数严格按照原实现，按行头部顺位抽取，并非完全随机采样。
        """
        rows = len(tempNameArray)
        base = byeRoundNumber // rows
        remainder = byeRoundNumber % rows
        res = []
        for i in range(rows):
            row_take = base + (1 if i < remainder else 0)
            # 取该行前 row_take 个元素（若不足，由调用侧保证 byeRoundNumber 合理）
            res.append(list(tempNameArray[i][:row_take]))
        return res

    @staticmethod
    def _shuffle_in_place(row):
        random.shuffle(row)

    def _distribute_seeded(self, seeded_indices, tempNameArray):
        """
        等价于原 C++: distributeElements
        按行循环均匀追加种子，再对每行做一次洗牌。
        """
        num_rows = len(tempNameArray)
        for i, idx in enumerate(seeded_indices):
            row_index = i % num_rows
            tempNameArray[row_index].append(idx)
        for i in range(num_rows):
            Draw._shuffle_in_place(tempNameArray[i])

    @staticmethod
    def _now_str():
        return datetime.now().strftime("%c")

    def _print_list(self, out_f, note, arr):
        """
        等价于原 C++: printList
        将索引转为姓名，按组打印到控制台和文件；当 arr 是最终 groupArray 时，提供 Excel 友好格式的额外输出。
        """
        # 将索引换成姓名
        list_str = []
        for group in arr:
            list_str.append([self.name[idx] for idx in group])

        # 分隔线
        print("_" * 90)
        print(note)
        out_f.write(note + "\n")

        # 逐组打印
        for i, vec in enumerate(list_str, start=1):
            header = f"第 {i} 组({count_non_empty(vec)})"
            print(f"{header}: ", end="")
            out_f.write(f"{header}: ")
            for s in vec:
                print(s, end=" ")
                out_f.write(s + " ")
            print()
            out_f.write("\n")

        # 若是最终分组，提供 Excel 友好格式（逐名独占一行）
        if arr is self.groupArray:
            try:
                input()  # 吸收回车（与原程序交互一致）
            except EOFError:
                pass
            print("按任意键则以适合编排Excel对阵表的形式输出")
            try:
                input()
            except EOFError:
                pass
            for i, vec in enumerate(list_str, start=1):
                group_title = f"\n第 {i} 组({count_non_empty(vec)})\n"
                print(group_title, end="")
                out_f.write(group_title)
                for s in vec:
                    print(s + "\n")
                    out_f.write(s + "\n\n")
                print()
                out_f.write("\n")

        tail = f"生成于：{self._now_str()}"
        print(tail)
        out_f.write(tail + "\n")

    def generation(self, option):
        """
        等价于原 C++: generation
        生成分组、计算首轮对阵/轮空并输出。
        """
        with open("抽签结果.txt", "w", encoding="utf-8") as out_f:
            # 1) 生成非种子索引（0..number-1 的乱序不重复）
            random_array = random.sample(range(0, self.number), self.number)

            # 2) 若有种子：为其分配位于 [原number, 原number+seededNumber-1] 的乱序索引；
            #    然后把种子姓名追加到 name 尾部，并更新 self.number。
            if self.seededNumber != 0:
                orig_number = self.number
                self.seededArray = random.sample(range(orig_number, orig_number + self.seededNumber), self.seededNumber)
                for nm in self.seededName:
                    self.name.append(nm)
                self.number += self.seededNumber

            # 3) 将非种子索引均匀分到 groupNumber 份
            tempNameArray = Draw._divide_array(random_array, self.groupNumber)

            # 4) 按组大小升序排序
            tempNameArray.sort(key=len)

            # 5) 将种子均匀追加到各组，并对每组洗牌，再次按组大小升序
            if self.seededNumber != 0:
                self._distribute_seeded(self.seededArray, tempNameArray)
                tempNameArray.sort(key=len)

            # 6) 循环赛：同时填充数组，便于GUI直接读取（不再只打印）
            if option in (singleGameLoop, teamGameLoop):
                # 将索引行保存为最终分组；为保持兼容，roundOne/bye 也填同样数据
                self.groupArray = [list(row) for row in tempNameArray]
                self.roundOneArray = [list(row) for row in tempNameArray]
                self.byeRoundArray = [list(row) for row in tempNameArray]
                # 统计：循环赛没有首轮，设为0；轮空人数设为总人数，便于显示
                self.roundOneNumber = 0
                self.byeRoundNumber = self.number
                self._print_list(out_f, "\n总分组结果如下：", self.groupArray)
                return

            # 7) 淘汰赛：计算奇偶组的数量与“某个奇数组/偶数组的人数”
            i = 0
            oddGroup = evenGroup = 0
            oddGroupNum = evenGroupNum = 0
            for i_row, vec in enumerate(tempNameArray):
                if len(vec) % 2 != 0:
                    oddGroup += 1
                    oddGroupNum = len(vec)
                else:
                    evenGroup += 1
                    evenGroupNum = len(vec)

            # 8) 根据原始算法计算首轮上场人数（附加赛人数）roundOneNumber
            #    找到 2^(i-1) <= evenGroupNum < 2^i
            i = 0
            while (2 ** i) <= evenGroupNum:
                i += 1
            gap = evenGroupNum - (2 ** (i - 1))

            if gap != 0:
                if oddGroupNum < evenGroupNum:
                    self.roundOneNumber = gap * 2 * evenGroup + (gap - 1) * 2 * oddGroup
                else:
                    self.roundOneNumber = gap * 2 * evenGroup + (gap + 1) * 2 * oddGroup
            else:
                if oddGroupNum < evenGroupNum:
                    self.roundOneNumber = 2 * oddGroup * (oddGroupNum - (2 ** (i - 2)))
                else:
                    self.roundOneNumber = oddGroup * 2

            self.byeRoundNumber = self.number - self.roundOneNumber

            # 9) 生成轮空名单、首轮对阵名单
            self.byeRoundArray = Draw._select_evenly(tempNameArray, self.byeRoundNumber)
            self.roundOneArray = Draw._delete_same_elements(tempNameArray, self.byeRoundArray)

            # 10) 合并得到总分组（对阵 + 轮空）
            self.groupArray = [list(row) for row in self.roundOneArray]
            for i in range(min(len(self.groupArray), len(self.byeRoundArray))):
                self.groupArray[i].extend(self.byeRoundArray[i])

            # 11) 打印三份：轮空、对阵、总分组
            self._print_list(out_f, "\n第一轮轮空名单如下：", self.byeRoundArray)
            self._print_list(out_f, "\n第一轮对阵名单如下：", self.roundOneArray)
            self._print_list(out_f, "\n总分组结果如下：", self.groupArray)


def main():
    # 尽量保持与原 C++ 的交互一致
    print("本程序设计时不考虑任何错误输入的情况，如果有错误输入请关闭并重新运行")
    print("请输入对应数字选择项目: 1 单项赛(淘汰赛) 2 单项赛(循环赛) 3 团体赛(淘汰赛) 4 团体赛(循环赛) 其余任意键 结束")
    try:
        gameOption = int(input().strip())
    except Exception:
        return

    if gameOption in (singleGame, singleGameLoop):
        print("请输入对应数字选择项目: 1 单打 2双打 其余任意键 结束")
        try:
            eventOption = int(input().strip())
        except Exception:
            return

        if eventOption == 1:
            print("请输入单打人数(在设立种子时为非种子数)：", end="")
        elif eventOption == 2:
            print("请输入双打组合数(在设立种子时为非种子数)：", end="")
        else:
            return
    elif gameOption in (teamGameLoop, teamGame):
        eventOption = 1  # 团体不区分单双
        print("请输入队伍数(在设立种子时为非种子数)：", end="")
    else:
        return

    dr = Draw()
    dr.number = int(input().strip())

    print("\n请输入种子数（若不设立则输入0）：", end="")
    dr.seededNumber = int(input().strip())

    dr.name = [""] * dr.number
    dr.seededName = [""] * dr.seededNumber

    if eventOption != 2:  # 非双打：逐行录入姓名
        print("请 按列 输入名单：")
        for i in range(dr.number):
            dr.name[i] = input().rstrip("\n")
        if dr.seededNumber != 0:
            print("请 按列 输入种子名单：")
            for i in range(dr.seededNumber):
                dr.seededName[i] = input().rstrip("\n")
    else:
        # 双打：两列合并为 [A B]
        temp = [""] * dr.number
        print("请 按列 输入双打第一列选手名单：")
        for i in range(dr.number):
            dr.name[i] = input().rstrip("\n")
        print("请 按列 输入双打第一列选手的队友名单：")
        for i in range(dr.number):
            temp[i] = input().rstrip("\n")
            dr.name[i] = f"[{dr.name[i]} {temp[i]}]"

        if dr.seededNumber != 0:
            temp = [""] * dr.seededNumber
            print("请 按列 输入双打种子第一列选手名单：")
            for i in range(dr.seededNumber):
                temp[i] = input().rstrip("\n")
            print("请 按列 输入双打种子第一列选手的队友名单：")
            for i in range(dr.seededNumber):
                mate = input().rstrip("\n")
                dr.seededName[i] = f"[{mate} {temp[i]}]"

    print("请输入小组的个数：", end="")
    dr.groupNumber = int(input().strip())

    # 执行生成
    dr.generation(gameOption)

    try:
        input("按回车键退出...")
    except EOFError:
        pass


if __name__ == "__main__":
    # 兼容 Windows 控制台中文输出
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
