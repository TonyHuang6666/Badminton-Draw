# -*- coding: utf-8 -*-
"""
基于 Qt (PySide6) 的抽签分组 GUI（单文件版）
— 通过导入并调用 `draw_lottery.py` 中的核心 Draw 类与常量 —

放置方式：
- 将本文件与 `draw_lottery.py` 放在同一目录下（或把该目录加入 PYTHONPATH）。
- 运行：  python draw_lottery_gui.py

依赖：
  pip install PySide6 pandas openpyxl

功能：
- 与原 CLI 一致的参数（单/团体、淘汰/循环、单双打、分组数、种子）。
- 表格录入名单（双打两列自动拼成「[A B]」）。
- 执行抽签后在界面显示：第一轮轮空/对阵/总分组 + 统计；可导出 TXT/XLSX；支持 CSV/Excel 导入及模板导出。
- 核心算法全部来自 draw_lottery.py：本 GUI 仅做数据收集与结果可视化，不复制算法逻辑。
"""
from __future__ import annotations
import sys
import os
import re
import csv
from typing import List, Tuple
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QSpinBox, QPushButton, QGroupBox, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox, QPlainTextEdit, QSplitter
)

# 可选依赖（导入/导出 Excel 用）。若缺失，会在使用时提示安装。
try:
    import pandas as pd  # type: ignore
except Exception:
    pd = None  # type: ignore

# ---------------------- 导入核心算法：来自 draw_lottery.py ----------------------
# 需要本文件与 draw_lottery.py 同目录。
try:
    from draw_lottery import Draw as CoreDraw, singleGame, singleGameLoop, teamGame, teamGameLoop
except Exception as e:
    # 若导入失败，给出明确提示（GUI 依然可启动，但无法运行抽签）
    CoreDraw = None  # type: ignore
    singleGame = 1   # 兜底值，仅用于界面初始化
    singleGameLoop = 2
    teamGame = 3
    teamGameLoop = 4
    _import_error = e
else:
    _import_error = None


# ---------------------- 工具：解析 draw_lottery 生成的 TXT ----------------------
_GROUP_LINE = re.compile(r'^第\\s*(\\d+)\\s*组\\([^)]*\\):\\s*(.*)$')

def _split_names_preserving_brackets(s: str) -> List[str]:
    """按空格切分，但保留 [A B] 作为一个整体。"""
    out = []
    i = 0
    n = len(s)
    while i < n:
        if s[i].isspace():
            i += 1
            continue
        if s[i] == '[':
            j = i + 1
            depth = 1
            while j < n and depth > 0:
                if s[j] == '[':
                    depth += 1
                elif s[j] == ']':
                    depth -= 1
                j += 1
            out.append(s[i:j].strip())
            i = j
        else:
            j = i + 1
            while j < n and not s[j].isspace():
                j += 1
            out.append(s[i:j])
            i = j
    return [t for t in (x.strip() for x in out) if t]

def parse_groups_from_txt(txt_path: str, header_keyword: str) -> List[List[str]]:
    """从抽签结果.txt 中解析某一块（例如“总分组结果如下：”）的组别行。"""
    if not os.path.exists(txt_path):
        return []
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = [ln.rstrip('\\n') for ln in f]
    groups: List[List[str]] = []
    active = False
    for line in lines:
        if header_keyword in line:
            active = True
            groups = []  # 重置，取该标题下最新一段
            continue
        if active:
            m = _GROUP_LINE.match(line.strip())
            if m:
                names_part = m.group(2).strip()
                tokens = _split_names_preserving_brackets(names_part)
                groups.append(tokens)
            elif line.strip().startswith('生成于：'):
                # 到了尾部时间戳，结束
                break
            elif line.strip() == '':
                # 空行不处理
                continue
            else:
                # 不是组别行，可能是下一个区块的标题
                if '名单如下' in line or '总分组结果如下' in line:
                    # 碰到另一个区块标题，结束
                    break
    return groups


# ---------------------- GUI ----------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("抽签分组（Qt GUI - 调用 draw_lottery.py）")
        self.resize(1180, 780)

        self.last_groups = {
            "bye": [],      # List[List[str]]
            "round1": [],   # List[List[str]]
            "all": [],      # List[List[str]]
        }
        self.last_stats = {"round_one": 0, "bye": 0}
        self.last_game_option: int | None = None

        # 菜单
        act_import = QAction("导入CSV/Excel", self)
        act_import.triggered.connect(self.on_import)
        act_export_txt = QAction("导出为TXT", self)
        act_export_txt.triggered.connect(self.on_export_txt)
        act_export_xlsx = QAction("导出为XLSX", self)
        act_export_xlsx.triggered.connect(self.on_export_xlsx)
        act_export_tpl = QAction("导出模板", self)
        act_export_tpl.triggered.connect(self.on_export_template)
        act_export_csvtpl = QAction("导出CSV模板", self)
        act_export_csvtpl.triggered.connect(self.on_export_csv_templates)
        menubar = self.menuBar()
        menubar.addAction(act_import)
        menubar.addAction(act_export_txt)
        menubar.addAction(act_export_xlsx)
        menubar.addAction(act_export_tpl)
        menubar.addAction(act_export_csvtpl)

        # 顶部参数区
        self.cboGame = QComboBox()
        self.cboGame.addItem("单项赛(淘汰)", singleGame)
        self.cboGame.addItem("单项赛(循环)", singleGameLoop)
        self.cboGame.addItem("团体赛(淘汰)", teamGame)
        self.cboGame.addItem("团体赛(循环)", teamGameLoop)
        self.cboGame.currentIndexChanged.connect(self.on_game_changed)

        self.cboEvent = QComboBox()
        self.cboEvent.addItem("单打", 1)
        self.cboEvent.addItem("双打", 2)
        self.cboEvent.currentIndexChanged.connect(self.apply_columns_by_event)

        self.spinNonSeed = QSpinBox(); self.spinNonSeed.setRange(1, 4096); self.spinNonSeed.setValue(16)
        self.spinSeed    = QSpinBox(); self.spinSeed.setRange(0, 4096); self.spinSeed.setValue(0)
        self.spinGroups  = QSpinBox(); self.spinGroups.setRange(1, 256);  self.spinGroups.setValue(4)

        self.btnApplyRows = QPushButton("应用到表格行数")
        self.btnApplyRows.clicked.connect(self.apply_rows_to_tables)

        top_form = QFormLayout()
        top_form.addRow(QLabel("项目类型"), self.cboGame)
        top_form.addRow(QLabel("比赛项目"), self.cboEvent)
        top_form.addRow(QLabel("非种子人数/队伍数"), self.spinNonSeed)
        top_form.addRow(QLabel("种子数"), self.spinSeed)
        top_form.addRow(QLabel("分组个数"), self.spinGroups)
        top_form.addRow(self.btnApplyRows)

        top_box = QGroupBox("基本设置"); top_box.setLayout(top_form)

        # 名单录入
        self.tblNonSeed = QTableWidget(16, 1)
        self.tblNonSeed.setHorizontalHeaderLabels(["姓名（单打） 或 左列（双打）"])
        self.tblNonSeed.verticalHeader().setVisible(False)
        self.tblNonSeed.setAlternatingRowColors(True)

        self.tblSeed = QTableWidget(0, 1)
        self.tblSeed.setHorizontalHeaderLabels(["种子姓名（单打） 或 左列（双打）"])
        self.tblSeed.verticalHeader().setVisible(False)
        self.tblSeed.setAlternatingRowColors(True)

        left_box1 = QGroupBox("非种子名单"); v1 = QVBoxLayout(); v1.addWidget(self.tblNonSeed); left_box1.setLayout(v1)
        left_box2 = QGroupBox("种子名单");   v2 = QVBoxLayout(); v2.addWidget(self.tblSeed);    left_box2.setLayout(v2)

        # 结果
        self.txtOut = QPlainTextEdit(); self.txtOut.setReadOnly(True)
        self.txtOut.setPlaceholderText("点击‘执行抽签’后在此显示结果…")
        right_box = QGroupBox("抽签结果"); rlayout = QVBoxLayout(); rlayout.addWidget(self.txtOut); right_box.setLayout(rlayout)

        splitter = QSplitter(Qt.Horizontal)
        left_wrap = QWidget(); lw = QVBoxLayout(left_wrap); lw.addWidget(left_box1); lw.addWidget(left_box2)
        splitter.addWidget(left_wrap); splitter.addWidget(right_box)
        splitter.setStretchFactor(0, 2); splitter.setStretchFactor(1, 3)

        # 底部按钮
        self.btnRun = QPushButton("执行抽签"); self.btnRun.clicked.connect(self.on_run)
        self.btnClear = QPushButton("清空结果"); self.btnClear.clicked.connect(lambda: self.txtOut.setPlainText(""))
        self.btnExportTxt = QPushButton("导出为TXT"); self.btnExportTxt.clicked.connect(self.on_export_txt)
        self.btnImport = QPushButton("导入CSV/Excel"); self.btnImport.clicked.connect(self.on_import)
        self.btnExportXlsx = QPushButton("导出为XLSX"); self.btnExportXlsx.clicked.connect(self.on_export_xlsx)
        self.btnExportTpl = QPushButton("导出模板"); self.btnExportTpl.clicked.connect(self.on_export_template)
        self.btnExportCsvTpl = QPushButton("导出CSV模板"); self.btnExportCsvTpl.clicked.connect(self.on_export_csv_templates)

        btn_bar = QHBoxLayout(); btn_bar.addStretch(1)
        for b in (self.btnImport, self.btnRun, self.btnClear, self.btnExportTxt, self.btnExportXlsx, self.btnExportTpl, self.btnExportCsvTpl):
            btn_bar.addWidget(b)

        central = QWidget(); root = QVBoxLayout(central)
        root.addWidget(top_box); root.addWidget(splitter); root.addLayout(btn_bar)
        self.setCentralWidget(central)

        self.on_game_changed()  # 初始化单双打列数

        # 若核心导入失败，在状态栏提示
        if _import_error is not None:
            self.statusBar().showMessage(f"警告：未能导入 draw_lottery.py：{_import_error}")

    # ---------- 事件 ----------
    def on_game_changed(self):
        game = self.cboGame.currentData()
        is_team = game in (teamGame, teamGameLoop)
        self.cboEvent.setEnabled(not is_team)
        if is_team:
            self.cboEvent.setCurrentIndex(0)
        self.apply_columns_by_event()

    def apply_columns_by_event(self):
        is_double = (self.cboEvent.currentData() == 2)
        cols = 2 if is_double else 1
        self.tblNonSeed.setColumnCount(cols)
        self.tblSeed.setColumnCount(cols)
        if is_double:
            self.tblNonSeed.setHorizontalHeaderLabels(["左列选手", "右列选手"])
            self.tblSeed.setHorizontalHeaderLabels(["左列选手(种子)", "右列选手(种子)"])
        else:
            self.tblNonSeed.setHorizontalHeaderLabels(["姓名（单打/团体）"])
            self.tblSeed.setHorizontalHeaderLabels(["种子姓名"])

    def apply_rows_to_tables(self):
        self.tblNonSeed.setRowCount(self.spinNonSeed.value())
        self.tblSeed.setRowCount(self.spinSeed.value())

    # ---------- 工具 ----------
    def _need_pandas(self) -> bool:
        if pd is None:
            QMessageBox.information(self, "缺少依赖", "此功能需要 pandas/openpyxl，\n请先安装：\n  pip install pandas openpyxl")
            return True
        return False

    def _get_cell(self, table: QTableWidget, r: int, c: int) -> str:
        it = table.item(r, c)
        return (it.text().strip() if it else "")

    def _collect_names(self, table: QTableWidget) -> List[str]:
        is_double = (self.cboEvent.currentData() == 2)
        rows = table.rowCount()
        names: List[str] = []
        if is_double:
            for r in range(rows):
                a = self._get_cell(table, r, 0)
                b = self._get_cell(table, r, 1)
                if a or b:
                    names.append(f"[{a} {b}]".strip())
        else:
            for r in range(rows):
                a = self._get_cell(table, r, 0)
                if a:
                    names.append(a)
        return names

    def _format_groups(self, title: str, groups: List[List[str]]) -> str:
        lines = [title]
        for i, g in enumerate(groups, 1):
            valid = [s for s in g if s]
            line = f"第 {i} 组({len(valid)}): " + " ".join(valid)
            lines.append(line)
        return "\n".join(lines) + "\n"

    def _format_excel_friendly(self, groups: List[List[str]]) -> str:
        lines = ["\n—— 适合Excel编排的逐行输出 ——"]
        for i, g in enumerate(groups, 1):
            valid = [s for s in g if s]
            lines.append(f"第 {i} 组({len(valid)})")
            for s in valid:
                lines.append(s)
            lines.append("")
        return "\n".join(lines) + "\n"

    # ---------- 抽签核心：调用 draw_lottery.Draw ----------
    def _run_core(self, game_option: int, nonseed: List[str], seed: List[str], groups: int):
        if CoreDraw is None:
            raise RuntimeError(f"无法导入 draw_lottery.py，请检查：{_import_error}")
        dr = CoreDraw()
        dr.number = len(nonseed)
        dr.groupNumber = groups
        dr.seededNumber = len(seed)
        dr.name = list(nonseed)
        dr.seededName = list(seed)
        # 调用核心生成：会写出 抽签结果.txt（循环赛不写数组时，我们将从TXT回退解析）
        dr.generation(game_option)

        # 生成后，dr.name 已把种子名单 append 到末尾
        full_names = dr.name

        def conv(idx_rows: List[List[int]]) -> List[List[str]]:
            return [[full_names[i] for i in row] for row in idx_rows]

        bye_groups = conv(dr.byeRoundArray) if getattr(dr, 'byeRoundArray', None) else []
        round1_groups = conv(dr.roundOneArray) if getattr(dr, 'roundOneArray', None) else []
        all_groups = conv(dr.groupArray) if getattr(dr, 'groupArray', None) else []

        # 循环赛兼容：若 groupArray 未填充，则从“抽签结果.txt”解析“总分组结果如下：”
        if not all_groups:
            txt_path = os.path.join(os.getcwd(), "抽签结果.txt")
            parsed = parse_groups_from_txt(txt_path, "总分组结果如下")
            if parsed:
                all_groups = parsed
                bye_groups = parsed
                round1_groups = parsed

        stats = {"round_one": getattr(dr, 'roundOneNumber', 0), "bye": getattr(dr, 'byeRoundNumber', 0)}
        return bye_groups, round1_groups, all_groups, stats

    # ---------- 动作：执行抽签 ----------
    def on_run(self):
        try:
            game = self.cboGame.currentData()
            names = self._collect_names(self.tblNonSeed)
            seeded = self._collect_names(self.tblSeed)
            groups = self.spinGroups.value()

            if len(names) == 0:
                QMessageBox.warning(self, "提示", "请至少输入1名非种子名单。")
                return
            if groups <= 0:
                QMessageBox.warning(self, "提示", "分组个数必须大于0。")
                return

            bye_g, r1_g, all_g, stats = self._run_core(game, names, seeded, groups)

            self.last_groups = {"bye": bye_g, "round1": r1_g, "all": all_g}
            self.last_stats = stats
            self.last_game_option = game

            out = []
            if game in (singleGameLoop, teamGameLoop):
                out.append(self._format_groups("总分组结果如下：", all_g))
            else:
                out.append(self._format_groups("第一轮轮空名单如下：", bye_g))
                out.append(self._format_groups("第一轮对阵名单如下：", r1_g))
                out.append(self._format_groups("总分组结果如下：", all_g))
            out.append(f"统计：首轮上场人数={stats['round_one']}，轮空人数={stats['bye']}")
            out.append(self._format_excel_friendly(all_g))
            self.txtOut.setPlainText("\n".join(out))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"执行失败：{e}")

    # ---------- 动作：导出TXT ----------
    def on_export_txt(self):
        text = self.txtOut.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "提示", "没有可导出的内容，请先执行抽签。")
            return
        path, _ = QFileDialog.getSaveFileName(self, "导出为TXT", f"抽签结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "文本文件 (*.txt)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            QMessageBox.information(self, "成功", f"已导出：{path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"写入失败：{e}")

    # ---------- 动作：导出XLSX ----------
    def on_export_xlsx(self):
        if not self.last_groups["all"]:
            QMessageBox.information(self, "提示", "请先执行抽签，再导出为XLSX。")
            return
        if pd is None:
            if self._need_pandas():
                return
        path, _ = QFileDialog.getSaveFileName(
            self, "导出为XLSX", f"抽签结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", "Excel 文件 (*.xlsx)"
        )
        if not path:
            return
        try:
            def groups_to_df(groups: List[List[str]]):
                rows = []
                for i, g in enumerate(groups, 1):
                    for member in g:
                        if member:
                            rows.append({"组别": i, "成员": member})
                return pd.DataFrame(rows)

            df_bye = groups_to_df(self.last_groups["bye"]) if self.last_groups["bye"] else pd.DataFrame(columns=["组别","成员"])
            df_r1  = groups_to_df(self.last_groups["round1"]) if self.last_groups["round1"] else pd.DataFrame(columns=["组别","成员"])
            df_all = groups_to_df(self.last_groups["all"]) if self.last_groups["all"] else pd.DataFrame(columns=["组别","成员"])
            df_stat = pd.DataFrame([
                {
                    "首轮上场人数": self.last_stats.get("round_one", 0),
                    "轮空人数": self.last_stats.get("bye", 0),
                    "导出时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            ])

            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                df_bye.to_excel(writer, sheet_name="轮空", index=False)
                df_r1.to_excel(writer, sheet_name="对阵", index=False)
                df_all.to_excel(writer, sheet_name="总分组", index=False)
                df_stat.to_excel(writer, sheet_name="统计", index=False)

            QMessageBox.information(self, "成功", f"已导出：{path}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"{e}")

    # ---------- 动作：导入CSV/Excel ----------
    def on_import(self):
        if pd is None:
            if self._need_pandas():
                return
        path, _ = QFileDialog.getOpenFileName(self, "导入CSV/Excel", "", "数据文件 (*.csv *.xlsx *.xls)")
        if not path:
            return
        try:
            ext = path.lower().rsplit('.', 1)[-1]
            if ext == 'csv':
                df = pd.read_csv(path)
                dfs = {'_single': df}
            else:
                xls = pd.ExcelFile(path)
                dfs = {name: xls.parse(name) for name in xls.sheet_names}

            # 优先识别双表（非种子/种子）
            nonseed_df = None
            seed_df = None
            for k, v in dfs.items():
                low = str(k).strip().lower()
                if low in {"nonseed", "非种子", "名单", "non-seed"}:
                    nonseed_df = v
                if low in {"seed", "种子"}:
                    seed_df = v

            if nonseed_df is None and seed_df is None:
                # 单表：从第一个 df 识别
                first_df = next(iter(dfs.values()))
                names_nonseed, names_seed, is_double = self._parse_df(first_df)
            else:
                # 双表：分别解析
                names_nonseed, _, is_double = self._parse_df(nonseed_df) if nonseed_df is not None else ([], [], False)
                seed_names_nonseed, _, is_double2 = self._parse_df(seed_df) if seed_df is not None else ([], [], is_double)
                names_seed = seed_names_nonseed
                is_double = is_double or is_double2

            # 应用到界面
            self._apply_import_to_ui(names_nonseed, names_seed, is_double)
            QMessageBox.information(self, "成功", f"已导入：{path}")
        except Exception as e:
            QMessageBox.critical(self, "导入失败", f"{e}")

    def _parse_df(self, df):
        if df is None or df.empty:
            return [], [], False
        # 规范列名
        cols = [str(c).strip() for c in df.columns]
        lower = {c.lower(): c for c in cols}

        def pick(aliases):
            for a in aliases:
                if a in lower:
                    return lower[a]
            return None

        # 识别单双打列
        c_left = pick(["left", "左", "左列", "a", "first"]) 
        c_right = pick(["right", "右", "右列", "b", "second", "mate", "队友"]) 
        c_name = pick(["name", "姓名", "选手", "队伍"]) 
        c_seed = pick(["is_seed", "seed", "种子"]) 

        if c_left and c_right:
            pairs = []
            seeds = []
            for _, row in df.iterrows():
                a = str(row.get(c_left, "")).strip()
                b = str(row.get(c_right, "")).strip()
                if not a and not b:
                    continue
                entry = f"[{a} {b}]".strip()
                flag = False
                if c_seed is not None:
                    val = row.get(c_seed)
                    try:
                        flag = bool(int(val))
                    except Exception:
                        flag = str(val).strip().lower() in {"1", "true", "是", "y"}
                (seeds if flag else pairs).append(entry)
            return pairs, seeds, True
        elif c_name:
            singles = []
            seeds = []
            for _, row in df.iterrows():
                a = str(row.get(c_name, "")).strip()
                if not a:
                    continue
                flag = False
                if c_seed is not None:
                    val = row.get(c_seed)
                    try:
                        flag = bool(int(val))
                    except Exception:
                        flag = str(val).strip().lower() in {"1", "true", "是", "y"}
                (seeds if flag else singles).append(a)
            return singles, seeds, False
        else:
            # 无法识别：默认取第一列为姓名
            first = df.columns[0]
            singles = [str(x).strip() for x in df[first].fillna("") if str(x).strip()]
            return singles, [], False

    def _apply_import_to_ui(self, nonseed: List[str], seed: List[str], is_double: bool):
        # 设置单双打
        self.cboEvent.setCurrentIndex(1 if is_double else 0)
        self.apply_columns_by_event()
        # 设置行数
        self.spinNonSeed.setValue(len(nonseed))
        self.spinSeed.setValue(len(seed))
        self.apply_rows_to_tables()
        # 写入表格
        def set_row_pair(table, r, text):
            t = text.strip().strip('[]')
            parts = t.split()
            a = parts[0] if len(parts) > 0 else ""
            b = parts[1] if len(parts) > 1 else ""
            table.setItem(r, 0, QTableWidgetItem(a))
            if table.columnCount() >= 2:
                table.setItem(r, 1, QTableWidgetItem(b))
        if self.cboEvent.currentData() == 2:
            for r, s in enumerate(nonseed):
                set_row_pair(self.tblNonSeed, r, s)
            for r, s in enumerate(seed):
                set_row_pair(self.tblSeed, r, s)
        else:
            for r, s in enumerate(nonseed):
                self.tblNonSeed.setItem(r, 0, QTableWidgetItem(s))
            for r, s in enumerate(seed):
                self.tblSeed.setItem(r, 0, QTableWidgetItem(s))

    # ---------- 动作：导出模板（XLSX，含说明） ----------
    def on_export_template(self):
        if pd is None:
            if self._need_pandas():
                return
        is_double = (self.cboEvent.currentData() == 2)
        default_name = f"抽签导入模板_{'双打' if is_double else '单打'}.xlsx"
        path, _ = QFileDialog.getSaveFileName(self, "导出模板", default_name, "Excel 文件 (*.xlsx)")
        if not path:
            return
        try:
            if is_double:
                df_non = pd.DataFrame({"左列": ["张三", "李四", "王五"], "右列": ["赵六", "孙七", "周八"]})
                df_seed = pd.DataFrame({"左列": ["种子甲", "种子乙"], "右列": ["搭档甲", "搭档乙"]})
                df_one = pd.DataFrame({"左列": ["张三", "种子甲"], "右列": ["赵六", "搭档甲"], "种子": [0, 1]})
            else:
                df_non = pd.DataFrame({"姓名": ["张三", "李四", "王五"]})
                df_seed = pd.DataFrame({"姓名": ["种子甲", "种子乙"]})
                df_one = pd.DataFrame({"姓名": ["张三", "种子甲"], "种子": [0, 1]})
            notes = [
                "【导入说明】列名大小写不敏感。",
                "单打/团体：姓名列可用 name/姓名/选手/队伍；可选列 种子/is_seed/seed=1 表示种子。",
                "双打：左列列名可用 left/左/左列/a/first；右列列名可用 right/右/右列/b/second/mate/队友。",
                "Excel多表导入：若存在工作表 ‘非种子’ 与 ‘种子’，分别读取；否则按单表自动识别‘种子’列。",
                "CSV导入：请保存为UTF-8或UTF-8-SIG编码，首行是列名。",
                "‘单表示例’工作表展示了单文件格式（含‘种子’列）的样例，可直接另存为CSV。",
            ]
            df_info = pd.DataFrame({"说明": notes})
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                df_non.to_excel(writer, sheet_name="非种子", index=False)
                df_seed.to_excel(writer, sheet_name="种子", index=False)
                df_one.to_excel(writer, sheet_name="单表示例", index=False)
                df_info.to_excel(writer, sheet_name="说明", index=False)
            QMessageBox.information(self, "成功", f"已导出模板：{path}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"{e}")

    # ---------- 动作：导出CSV模板（三个CSV） ----------
    def on_export_csv_templates(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择导出文件夹")
        if not dir_path:
            return
        try:
            is_double = (self.cboEvent.currentData() == 2)
            fn_non = os.path.join(dir_path, "非种子.csv")
            fn_seed = os.path.join(dir_path, "种子.csv")
            fn_one  = os.path.join(dir_path, "单表示例.csv")
            def write_csv(path, header, rows):
                with open(path, 'w', encoding='utf-8-sig', newline='') as f:
                    w = csv.writer(f); w.writerow(header); w.writerows(rows)
            if is_double:
                write_csv(fn_non, ["左列", "右列"], [["张三", "赵六"], ["李四", "孙七"], ["王五", "周八"]])
                write_csv(fn_seed, ["左列", "右列"], [["种子甲", "搭档甲"], ["种子乙", "搭档乙"]])
                write_csv(fn_one,  ["左列", "右列", "种子"], [["张三", "赵六", 0], ["种子甲", "搭档甲", 1]])
            else:
                write_csv(fn_non, ["姓名"], [["张三"], ["李四"], ["王五"]])
                write_csv(fn_seed, ["姓名"], [["种子甲"], ["种子乙"]])
                write_csv(fn_one,  ["姓名", "种子"], [["张三", 0], ["种子甲", 1]])
            QMessageBox.information(self, "成功", f"已导出至：\n{fn_non}\n{fn_seed}\n{fn_one}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"{e}")

    # ---------- 窗口事件 ----------
    def closeEvent(self, event: QCloseEvent):
        event.accept()


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
