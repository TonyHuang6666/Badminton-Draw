import sys
import random
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QMessageBox, QFileDialog)

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
        res = [[] for _ in range(m)]
        n = len(nums)
        for j in range(m):
            for k in range(n // m + (j < n % m)):
                res[j].append(nums.pop(0))
        return res

    def print_list(self, note, arr):
        result = f"{note}:\n"
        for i, group in enumerate(arr, 1):
            result += f"第 {i} 组({len(group)}): {', '.join([self.name[idx] for idx in group])}\n"
        return result

    def distribute_elements(self, seeded_array, temp_name_array):
        random.shuffle(seeded_array)
        for i, seeded in enumerate(seeded_array):
            temp_name_array[i % len(temp_name_array)].append(seeded)

        for group in temp_name_array:
            random.shuffle(group)

    def delete_same_elements(self, temp, bye_round_array):
        result = []
        for i, group in enumerate(temp):
            result.append([x for x in group if x not in bye_round_array[i]])
        return result

    def select(self, temp_name_array, bye_round_number):
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

        result = ""
        if option == 2:  # 循环赛模式
            result += self.print_list("\n总分组结果如下", temp_name_array)

        if option == 1:  # 淘汰赛模式
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

            result += self.print_list("\n第一轮轮空名单如下", self.byeRoundArray)
            result += self.print_list("\n第一轮对阵名单如下", self.roundOneArray)
            result += self.print_list("\n总分组结果如下", self.groupArray)
        
        return result


class DrawApp(QWidget):
    def __init__(self):
        super().__init__()

        self.draw = Draw()
        self.init_ui()

    def init_ui(self):
        # 输入标签
        self.number_label = QLabel('参赛人数:')
        self.group_label = QLabel('分组数:')
        self.seeded_label = QLabel('种子数:')
        self.name_label = QLabel('选手姓名(逗号分隔):')
        self.seeded_name_label = QLabel('种子选手姓名(逗号分隔):')

        # 输入框
        self.number_input = QLineEdit(self)
        self.group_input = QLineEdit(self)
        self.seeded_input = QLineEdit(self)
        self.name_input = QLineEdit(self)
        self.seeded_name_input = QLineEdit(self)

        # 按钮
        self.generate_button = QPushButton('生成结果', self)
        self.generate_button.clicked.connect(self.generate_result)

        self.load_excel_button = QPushButton('从Excel读取名单', self)
        self.load_excel_button.clicked.connect(self.load_from_excel)

        self.load_txt_button = QPushButton('从TXT读取名单', self)
        self.load_txt_button.clicked.connect(self.load_from_txt)

        # 显示结果
        self.result_display = QTextEdit(self)
        self.result_display.setReadOnly(True)

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.number_label)
        layout.addWidget(self.number_input)
        layout.addWidget(self.group_label)
        layout.addWidget(self.group_input)
        layout.addWidget(self.seeded_label)
        layout.addWidget(self.seeded_input)
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.seeded_name_label)
        layout.addWidget(self.seeded_name_input)

        # 文件读取按钮
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.load_excel_button)
        file_layout.addWidget(self.load_txt_button)

        layout.addLayout(file_layout)
        layout.addWidget(self.generate_button)
        layout.addWidget(self.result_display)

        self.setLayout(layout)
        self.setWindowTitle('抽签程序')
        self.show()

    def load_from_excel(self):
        # 打开文件对话框，选择Excel文件
        file_name, _ = QFileDialog.getOpenFileName(self, "打开Excel文件", "", "Excel Files (*.xlsx *.xls)")
        if file_name:
            try:
                # 读取Excel文件
                df = pd.read_excel(file_name)
                if 'name' in df.columns:
                    self.draw.name = df['name'].tolist()
                    self.name_input.setText(','.join(self.draw.name))
                if 'seeded' in df.columns:
                    self.draw.seededName = df['seeded'].tolist()
                    self.seeded_name_input.setText(','.join(self.draw.seededName))
                self.number_input.setText(str(len(self.draw.name)))
            except Exception as e:
                QMessageBox.warning(self, "读取错误", f"读取Excel文件失败: {str(e)}")

    def load_from_txt(self):
        # 打开文件对话框，选择TXT文件
        file_name, _ = QFileDialog.getOpenFileName(self, "打开TXT文件", "", "Text Files (*.txt)")
        if file_name:
            try:
                # 读取TXT文件
                with open(file_name, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    self.draw.name = [line.strip() for line in lines if line.strip()]
                    self.name_input.setText(','.join(self.draw.name))
                    self.number_input.setText(str(len(self.draw.name)))
            except Exception as e:
                QMessageBox.warning(self, "读取错误", f"读取TXT文件失败: {str(e)}")

    def generate_result(self):
        try:
            # 获取输入
            self.draw.number = int(self.number_input.text())
            self.draw.groupNumber = int(self.group_input.text())
            self.draw.seededNumber = int(self.seeded_input.text())

            # 处理姓名输入
            self.draw.name = self.name_input.text().split(',')
            self.draw.seededName = self.seeded_name_input.text().split(',')

            # 检查输入的正确性
            if len(self.draw.name) != self.draw.number:
                raise ValueError("选手姓名数量与参赛人数不一致！")
            if len(self.draw.seededName) != self.draw.seededNumber:
                raise ValueError("种子选手姓名数量与种子数不一致！")

            # 显示结果（淘汰赛模式）
            result = self.draw.generation(option=1)
            self.result_display.setText(result)

        except ValueError as e:
            QMessageBox.warning(self, "输入错误", str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DrawApp()
    sys.exit(app.exec_())