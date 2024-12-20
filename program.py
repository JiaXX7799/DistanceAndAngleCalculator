import csv
import math
import sys

import matplotlib.patches as patches
from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QGroupBox, QMessageBox, QTabWidget, QTextEdit, QFileDialog,
    QComboBox, QSizePolicy, QDoubleSpinBox, QGridLayout
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class DistanceAndAngleCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.history = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("二维坐标距离与角度计算器")
        self.setMinimumSize(1200, 900)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 语言选择
        language_layout = QHBoxLayout()
        language_label = QLabel("语言选择:")
        language_label.setFont(QFont("Arial", 12))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["中文", "English"])
        self.language_combo.currentIndexChanged.connect(self.change_language)
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        language_layout.addStretch()
        main_layout.addLayout(language_layout)

        # 标签页
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Arial", 12))

        # 计算页
        self.calculation_tab = QWidget()
        self.init_calculation_tab()
        self.tabs.addTab(self.calculation_tab, "计算")

        # 历史记录页
        self.history_tab = QWidget()
        self.init_history_tab()
        self.tabs.addTab(self.history_tab, "历史记录")

        main_layout.addWidget(self.tabs)

        self.setLayout(main_layout)

    def init_calculation_tab(self):
        layout = QVBoxLayout()

        # --- 二维坐标距离计算部分 ---
        distance_group = QGroupBox("二维坐标距离计算")
        distance_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        distance_layout = QGridLayout()

        # 点A输入
        label_a = QLabel("点A (x1, y1):")
        label_a.setFont(QFont("Arial", 12))
        self.input_x1 = QLineEdit()
        self.input_x1.setPlaceholderText("x1")
        self.input_x1.setValidator(QDoubleValidator())
        self.input_y1 = QLineEdit()
        self.input_y1.setPlaceholderText("y1")
        self.input_y1.setValidator(QDoubleValidator())
        distance_layout.addWidget(label_a, 0, 0)
        distance_layout.addWidget(self.input_x1, 0, 1)
        distance_layout.addWidget(self.input_y1, 0, 2)

        # 点B输入
        label_b = QLabel("点B (x2, y2):")
        label_b.setFont(QFont("Arial", 12))
        self.input_x2 = QLineEdit()
        self.input_x2.setPlaceholderText("x2")
        self.input_x2.setValidator(QDoubleValidator())
        self.input_y2 = QLineEdit()
        self.input_y2.setPlaceholderText("y2")
        self.input_y2.setValidator(QDoubleValidator())
        distance_layout.addWidget(label_b, 1, 0)
        distance_layout.addWidget(self.input_x2, 1, 1)
        distance_layout.addWidget(self.input_y2, 1, 2)

        # 计算距离按钮
        self.button_calculate_distance = QPushButton("计算距离")
        self.button_calculate_distance.setFont(QFont("Arial", 12))
        self.button_calculate_distance.clicked.connect(self.calculate_distance)
        distance_layout.addWidget(self.button_calculate_distance, 2, 0, 1, 3)

        # 距离结果显示
        self.label_distance_result = QLabel("距离: ")
        self.label_distance_result.setFont(QFont("Arial", 12))
        distance_layout.addWidget(self.label_distance_result, 3, 0, 1, 3)

        distance_group.setLayout(distance_layout)
        layout.addWidget(distance_group)

        # --- 原点和Y轴设置部分 ---
        origin_group = QGroupBox("原点和Y轴设置")
        origin_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        origin_layout = QGridLayout()

        # 原点输入
        label_origin = QLabel("原点 (x0, y0):")
        label_origin.setFont(QFont("Arial", 12))
        self.input_x0 = QLineEdit()
        self.input_x0.setPlaceholderText("x0")
        self.input_x0.setValidator(QDoubleValidator())
        self.input_y0 = QLineEdit()
        self.input_y0.setPlaceholderText("y0")
        self.input_y0.setValidator(QDoubleValidator())
        origin_layout.addWidget(label_origin, 0, 0)
        origin_layout.addWidget(self.input_x0, 0, 1)
        origin_layout.addWidget(self.input_y0, 0, 2)

        # Y轴方向偏移角度输入
        label_y_axis = QLabel("Y轴方向偏移角度 (°):")
        label_y_axis.setFont(QFont("Arial", 12))
        self.input_y_axis_angle = QDoubleSpinBox()
        self.input_y_axis_angle.setRange(-360.0, 360.0)
        self.input_y_axis_angle.setSingleStep(1.0)
        self.input_y_axis_angle.setValue(0.0)
        self.input_y_axis_angle.valueChanged.connect(self.update_plot)
        origin_layout.addWidget(label_y_axis, 1, 0)
        origin_layout.addWidget(self.input_y_axis_angle, 1, 1, 1, 2)

        origin_group.setLayout(origin_layout)
        layout.addWidget(origin_group)

        # --- 手动旋转半径部分 ---
        rotation_group = QGroupBox("手动旋转半径设置")
        rotation_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        rotation_layout = QGridLayout()

        # 第一根半径与Y轴偏移角度
        label_rotation = QLabel("第一根半径与Y轴偏移角度 (°):")
        label_rotation.setFont(QFont("Arial", 12))
        self.input_rotation_angle = QDoubleSpinBox()
        self.input_rotation_angle.setRange(-360.0, 360.0)
        self.input_rotation_angle.setSingleStep(1.0)
        self.input_rotation_angle.setValue(0.0)
        self.input_rotation_angle.valueChanged.connect(self.update_plot)
        rotation_layout.addWidget(label_rotation, 0, 0)
        rotation_layout.addWidget(self.input_rotation_angle, 0, 1, 1, 2)

        rotation_group.setLayout(rotation_layout)
        layout.addWidget(rotation_group)

        # --- 角度与弦长计算部分 ---
        angle_chord_group = QGroupBox("角度与弦长计算")
        angle_chord_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        angle_chord_layout = QGridLayout()

        # 根据半径和弦长计算角度
        label_radius_c = QLabel("半径 (r):")
        label_radius_c.setFont(QFont("Arial", 12))
        self.input_radius_c = QLineEdit()
        self.input_radius_c.setPlaceholderText("请输入半径")
        self.input_radius_c.setValidator(QDoubleValidator())
        label_chord_c = QLabel("弦长 (c):")
        label_chord_c.setFont(QFont("Arial", 12))
        self.input_chord_c = QLineEdit()
        self.input_chord_c.setPlaceholderText("请输入弦长")
        self.input_chord_c.setValidator(QDoubleValidator())
        angle_chord_layout.addWidget(label_radius_c, 0, 0)
        angle_chord_layout.addWidget(self.input_radius_c, 0, 1)
        angle_chord_layout.addWidget(label_chord_c, 0, 2)
        angle_chord_layout.addWidget(self.input_chord_c, 0, 3)

        self.button_calculate_angle = QPushButton("计算角度")
        self.button_calculate_angle.setFont(QFont("Arial", 12))
        self.button_calculate_angle.clicked.connect(self.calculate_angle)
        angle_chord_layout.addWidget(self.button_calculate_angle, 1, 0, 1, 4)

        self.label_angle_result = QLabel("角度: ")
        self.label_angle_result.setFont(QFont("Arial", 12))
        angle_chord_layout.addWidget(self.label_angle_result, 2, 0, 1, 4)

        # 根据半径和角度计算弦长
        label_radius_a = QLabel("半径 (r):")
        label_radius_a.setFont(QFont("Arial", 12))
        self.input_radius_a = QLineEdit()
        self.input_radius_a.setPlaceholderText("请输入半径")
        self.input_radius_a.setValidator(QDoubleValidator())
        label_angle_a = QLabel("角度 (°):")
        label_angle_a.setFont(QFont("Arial", 12))
        self.input_angle_a = QLineEdit()
        self.input_angle_a.setPlaceholderText("请输入角度")
        self.input_angle_a.setValidator(QDoubleValidator())
        angle_chord_layout.addWidget(label_radius_a, 3, 0)
        angle_chord_layout.addWidget(self.input_radius_a, 3, 1)
        angle_chord_layout.addWidget(label_angle_a, 3, 2)
        angle_chord_layout.addWidget(self.input_angle_a, 3, 3)

        self.button_calculate_chord = QPushButton("计算弦长")
        self.button_calculate_chord.setFont(QFont("Arial", 12))
        self.button_calculate_chord.clicked.connect(self.calculate_chord)
        angle_chord_layout.addWidget(self.button_calculate_chord, 4, 0, 1, 4)

        self.label_chord_result = QLabel("弦长: ")
        self.label_chord_result.setFont(QFont("Arial", 12))
        angle_chord_layout.addWidget(self.label_chord_result, 5, 0, 1, 4)

        angle_chord_group.setLayout(angle_chord_layout)
        layout.addWidget(angle_chord_group)

        # --- 图形展示部分 ---
        plot_group = QGroupBox("图形展示")
        plot_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        plot_layout = QVBoxLayout()

        self.figure = Figure(figsize=(6, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.updateGeometry()
        plot_layout.addWidget(self.canvas)

        plot_group.setLayout(plot_layout)
        layout.addWidget(plot_group)

        # --- 导出结果按钮 ---
        export_layout = QHBoxLayout()
        self.button_export = QPushButton("导出历史记录")
        self.button_export.setFont(QFont("Arial", 12))
        self.button_export.clicked.connect(self.export_history)
        export_layout.addStretch()
        export_layout.addWidget(self.button_export)
        layout.addLayout(export_layout)

        self.calculation_tab.setLayout(layout)

    def init_history_tab(self):
        layout = QVBoxLayout()

        # 历史记录显示
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        layout.addWidget(self.history_text)

        self.history_tab.setLayout(layout)

    def change_language(self):
        language = self.language_combo.currentText()
        if language == "中文":
            self.tabs.setTabText(0, "计算")
            self.tabs.setTabText(1, "历史记录")
            self.update_ui_language("中文")
        else:
            self.tabs.setTabText(0, "Calculate")
            self.tabs.setTabText(1, "History")
            self.update_ui_language("English")

    def update_ui_language(self, language):
        if language == "中文":
            # 二维坐标距离计算
            distance_group = self.calculation_tab.findChild(QGroupBox, "二维坐标距离计算")
            distance_group.setTitle("二维坐标距离计算")

            label_a = distance_group.layout().itemAt(0).widget()
            label_a.setText("点A (x1, y1):")
            label_b = distance_group.layout().itemAt(3).widget()
            label_b.setText("点B (x2, y2):")
            self.button_calculate_distance.setText("计算距离")
            self.label_distance_result.setText("距离: ")

            # 原点和Y轴设置
            origin_group = self.calculation_tab.findChild(QGroupBox, "原点和Y轴设置")
            origin_group.setTitle("原点和Y轴设置")
            origin_layout = origin_group.layout()
            label_origin = origin_layout.itemAt(0).widget()
            label_origin.setText("原点 (x0, y0):")
            label_y_axis = origin_layout.itemAt(3).widget()
            label_y_axis.setText("Y轴方向偏移角度 (°):")

            # 手动旋转半径设置
            rotation_group = self.calculation_tab.findChild(QGroupBox, "手动旋转半径设置")
            rotation_group.setTitle("手动旋转半径设置")
            rotation_layout = rotation_group.layout()
            label_rotation = rotation_layout.itemAt(0).widget()
            label_rotation.setText("第一根半径与Y轴偏移角度 (°):")

            # 角度与弦长计算
            angle_chord_group = self.calculation_tab.findChild(QGroupBox, "角度与弦长计算")
            angle_chord_group.setTitle("角度与弦长计算")

            angle_chord_layout = angle_chord_group.layout()
            label_radius_c = angle_chord_layout.itemAt(0).widget()
            label_radius_c.setText("半径 (r):")
            label_chord_c = angle_chord_layout.itemAt(2).widget()
            label_chord_c.setText("弦长 (c):")
            self.button_calculate_angle.setText("计算角度")
            self.label_angle_result.setText("角度: ")

            label_radius_a = angle_chord_layout.itemAt(6).widget()
            label_radius_a.setText("半径 (r):")
            label_angle_a = angle_chord_layout.itemAt(8).widget()
            label_angle_a.setText("角度 (°):")
            self.button_calculate_chord.setText("计算弦长")
            self.label_chord_result.setText("弦长: ")

            # 图形展示
            plot_group = self.calculation_tab.findChild(QGroupBox, "图形展示")
            plot_group.setTitle("图形展示")

            # 导出按钮
            self.button_export.setText("导出历史记录")

        else:
            # 二维坐标距离计算
            distance_group = self.calculation_tab.findChild(QGroupBox, "二维坐标距离计算")
            distance_group.setTitle("2D Distance Calculation")

            label_a = distance_group.layout().itemAt(0).widget()
            label_a.setText("Point A (x1, y1):")
            label_b = distance_group.layout().itemAt(3).widget()
            label_b.setText("Point B (x2, y2):")
            self.button_calculate_distance.setText("Calculate Distance")
            self.label_distance_result.setText("Distance: ")

            # 原点和Y轴设置
            origin_group = self.calculation_tab.findChild(QGroupBox, "原点和Y轴设置")
            origin_group.setTitle("Origin and Y-Axis Settings")
            origin_layout = origin_group.layout()
            label_origin = origin_layout.itemAt(0).widget()
            label_origin.setText("Origin (x0, y0):")
            label_y_axis = origin_layout.itemAt(3).widget()
            label_y_axis.setText("Y-Axis Offset Angle (°):")

            # 手动旋转半径设置
            rotation_group = self.calculation_tab.findChild(QGroupBox, "手动旋转半径设置")
            rotation_group.setTitle("Manual Rotation of Radius")
            rotation_layout = rotation_group.layout()
            label_rotation = rotation_layout.itemAt(0).widget()
            label_rotation.setText("First Radius Offset Angle from Y-Axis (°):")

            # 角度与弦长计算
            angle_chord_group = self.calculation_tab.findChild(QGroupBox, "角度与弦长计算")
            angle_chord_group.setTitle("Angle and Chord Calculation")

            angle_chord_layout = angle_chord_group.layout()
            label_radius_c = angle_chord_layout.itemAt(0).widget()
            label_radius_c.setText("Radius (r):")
            label_chord_c = angle_chord_layout.itemAt(2).widget()
            label_chord_c.setText("Chord (c):")
            self.button_calculate_angle.setText("Calculate Angle")
            self.label_angle_result.setText("Angle: ")

            label_radius_a = angle_chord_layout.itemAt(6).widget()
            label_radius_a.setText("Radius (r):")
            label_angle_a = angle_chord_layout.itemAt(8).widget()
            label_angle_a.setText("Angle (°):")
            self.button_calculate_chord.setText("Calculate Chord")
            self.label_chord_result.setText("Chord: ")

            # 图形展示
            plot_group = self.calculation_tab.findChild(QGroupBox, "图形展示")
            plot_group.setTitle("Graphical Display")

            # 导出按钮
            self.button_export.setText("Export History")

    def calculate_distance(self):
        try:
            x1_text = self.input_x1.text()
            y1_text = self.input_y1.text()
            x2_text = self.input_x2.text()
            y2_text = self.input_y2.text()

            if not all([x1_text, y1_text, x2_text, y2_text]):
                raise ValueError("请填写所有坐标输入。")

            x1 = float(x1_text)
            y1 = float(y1_text)
            x2 = float(x2_text)
            y2 = float(y2_text)

            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            self.label_distance_result.setText(f"距离: {distance:.2f}")

            # 记录历史
            self.history.append(f"计算距离: 点A({x1}, {y1}) 点B({x2}, {y2}) -> 距离: {distance:.2f}")
            self.update_history()

            # 绘制图形
            self.plot_graph(x1=x1, y1=y1, x2=x2, y2=y2, radius=None, angle=None)
        except ValueError as ve:
            QMessageBox.critical(self, "输入错误", str(ve))
            self.label_distance_result.setText("距离: ")

    def calculate_angle(self):
        try:
            radius_text = self.input_radius_c.text()
            chord_text = self.input_chord_c.text()

            if not all([radius_text, chord_text]):
                raise ValueError("请填写半径和弦长的输入。")

            radius = float(radius_text)
            chord = float(chord_text)

            if radius <= 0:
                raise ValueError("半径必须大于零。")
            if chord <= 0:
                raise ValueError("弦长必须大于零。")
            if chord > 2 * radius:
                raise ValueError("弦长不能大于直径（2 * 半径）。")

            # 计算角度（弧度）
            theta_rad = 2 * math.asin(chord / (2 * radius))
            # 转换为度
            theta_deg = math.degrees(theta_rad)
            self.label_angle_result.setText(f"角度: {theta_deg:.2f}°")

            # 记录历史
            self.history.append(f"计算角度: 半径={radius}, 弦长={chord} -> 角度={theta_deg:.2f}°")
            self.update_history()

            # 绘制图形
            self.plot_graph(x1=None, y1=None, x2=None, y2=None, radius=radius, angle=theta_deg)
        except ValueError as ve:
            QMessageBox.critical(self, "输入错误", str(ve))
            self.label_angle_result.setText("角度: ")

    def calculate_chord(self):
        try:
            radius_text = self.input_radius_a.text()
            angle_text = self.input_angle_a.text()

            if not all([radius_text, angle_text]):
                raise ValueError("请填写半径和角度的输入。")

            radius = float(radius_text)
            angle_deg = float(angle_text)

            if radius <= 0:
                raise ValueError("半径必须大于零。")
            if angle_deg <= 0 or angle_deg >= 360:
                raise ValueError("角度必须在 (0, 360) 度之间。")

            # 转换角度为弧度
            theta_rad = math.radians(angle_deg)
            # 计算弦长
            chord = 2 * radius * math.sin(theta_rad / 2)
            self.label_chord_result.setText(f"弦长: {chord:.2f}")

            # 记录历史
            self.history.append(f"计算弦长: 半径={radius}, 角度={angle_deg}° -> 弦长={chord:.2f}")
            self.update_history()

            # 绘制图形
            self.plot_graph(x1=None, y1=None, x2=None, y2=None, radius=radius, angle=angle_deg, calculate_chord=True)
        except ValueError as ve:
            QMessageBox.critical(self, "输入错误", str(ve))
            self.label_chord_result.setText("弦长: ")

    def plot_graph(self, x1=None, y1=None, x2=None, y2=None, radius=None, angle=None, calculate_chord=False):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_aspect('equal')
        ax.grid(True)

        # 获取原点和Y轴方向
        try:
            x0 = float(self.input_x0.text()) if self.input_x0.text() else 0.0
            y0 = float(self.input_y0.text()) if self.input_y0.text() else 0.0
        except ValueError:
            x0, y0 = 0.0, 0.0

        y_axis_offset = self.input_y_axis_angle.value()

        # 旋转Y轴
        y_axis_rad = math.radians(y_axis_offset)
        y_axis_end_x = x0 + math.sin(y_axis_rad)
        y_axis_end_y = y0 + math.cos(y_axis_rad)
        ax.plot([x0, y_axis_end_x], [y0, y_axis_end_y], 'k-', linewidth=2, label='Y-Axis')

        # 绘制点A和点B及距离
        if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
            ax.plot([x1, x2], [y1, y2], 'bo-', label='Points A & B')
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            ax.text(mid_x, mid_y, f"{distance:.2f}", fontsize=10, color='blue')
            ax.legend()
            self.draw_origin(ax, x0, y0)
            self.canvas.draw()
            return

        # 绘制圆
        if radius is not None:
            circle = patches.Circle((x0, y0), radius, linewidth=2, edgecolor='g', facecolor='none', label='Circle')
            ax.add_patch(circle)

        # 手动旋转半径
        rotation_angle = self.input_rotation_angle.value()
        rotation_rad = math.radians(rotation_angle)

        # 第一根半径
        r1_x = x0 + radius * math.sin(y_axis_rad + rotation_rad)
        r1_y = y0 + radius * math.cos(y_axis_rad + rotation_rad)
        ax.plot([x0, r1_x], [y0, r1_y], 'r-', linewidth=2, label='Radius 1')

        if angle is not None:
            if calculate_chord:
                theta_rad = math.radians(angle)
            else:
                theta_rad = math.radians(angle)

            # 第二根半径
            r2_x = x0 + radius * math.sin(y_axis_rad + rotation_rad + theta_rad)
            r2_y = y0 + radius * math.cos(y_axis_rad + rotation_rad + theta_rad)
            ax.plot([x0, r2_x], [y0, r2_y], 'b-', linewidth=2, label='Radius 2')

            # 绘制弦长
            ax.plot([r1_x, r2_x], [r1_y, r2_y], 'k--', linewidth=2, label='Chord')

            # 标注角度
            angle_patch = patches.Arc((x0, y0), radius*0.6, radius*0.6, angle=0, theta1=math.degrees(rotation_rad), theta2=math.degrees(rotation_rad + theta_rad), color='m')
            ax.add_patch(angle_patch)
            ax.text(x0 + radius*0.4*math.sin(y_axis_rad + rotation_rad + theta_rad/2),
                    y0 + radius*0.4*math.cos(y_axis_rad + rotation_rad + theta_rad/2),
                    f"{math.degrees(theta_rad):.2f}°", color='m', fontsize=10)

            # 标注弦长
            chord_length = math.sqrt((r2_x - r1_x)**2 + (r2_y - r1_y)**2)
            mid_chord_x = (r1_x + r2_x) / 2
            mid_chord_y = (r1_y + r2_y) / 2
            ax.text(mid_chord_x, mid_chord_y, f"c={chord_length:.2f}", fontsize=10, color='k')

            # 计算并标注交点坐标
            intersection1 = (r1_x, r1_y)
            intersection2 = (r2_x, r2_y)
            ax.plot(*intersection1, 'go')
            ax.plot(*intersection2, 'go')
            ax.text(intersection1[0], intersection1[1], f"({intersection1[0]:.2f}, {intersection1[1]:.2f})", fontsize=8, color='g')
            ax.text(intersection2[0], intersection2[1], f"({intersection2[0]:.2f}, {intersection2[1]:.2f})", fontsize=8, color='g')

            ax.legend()

        self.draw_origin(ax, x0, y0)
        ax.set_xlim(x0 - radius*1.5 if radius else -10, x0 + radius*1.5 if radius else 10)
        ax.set_ylim(y0 - radius*1.5 if radius else -10, y0 + radius*1.5 if radius else 10)
        self.canvas.draw()

    def draw_origin(self, ax, x0, y0):
        ax.plot(x0, y0, 'ko', label='Origin')
        ax.text(x0, y0, f" Origin ({x0:.2f}, {y0:.2f})", fontsize=10, verticalalignment='bottom')

    def update_plot(self):
        self.plot_graph()

    def update_history(self):
        self.history_text.clear()
        for record in self.history[-100:]:
            self.history_text.append(record)

    def export_history(self):
        if not self.history:
            QMessageBox.information(self, "信息", "没有历史记录可导出。")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "保存历史记录", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["历史记录"])
                    for record in self.history:
                        writer.writerow([record])
                QMessageBox.information(self, "成功", "历史记录已成功导出。")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {e}")

    def plot_graph(self, x1=None, y1=None, x2=None, y2=None, radius=None, angle=None, calculate_chord=False):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_aspect('equal')
        ax.grid(True)

        # 获取原点和Y轴方向
        try:
            x0 = float(self.input_x0.text()) if self.input_x0.text() else 0.0
            y0 = float(self.input_y0.text()) if self.input_y0.text() else 0.0
        except ValueError:
            x0, y0 = 0.0, 0.0

        y_axis_offset = self.input_y_axis_angle.value()

        # 旋转Y轴
        y_axis_rad = math.radians(y_axis_offset)
        y_axis_end_x = x0 + math.sin(y_axis_rad)
        y_axis_end_y = y0 + math.cos(y_axis_rad)
        ax.plot([x0, y_axis_end_x], [y0, y_axis_end_y], 'k-', linewidth=2, label='Y-Axis')

        # 绘制点A和点B及距离
        if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
            ax.plot([x1, x2], [y1, y2], 'bo-', label='Points A & B')
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            ax.text(mid_x, mid_y, f"{distance:.2f}", fontsize=10, color='blue')
            ax.legend()
            self.draw_origin(ax, x0, y0)
            self.canvas.draw()
            return

        # 绘制圆
        if radius is not None:
            circle = patches.Circle((x0, y0), radius, linewidth=2, edgecolor='g', facecolor='none', label='Circle')
            ax.add_patch(circle)

        # 手动旋转半径
        rotation_angle = self.input_rotation_angle.value()
        rotation_rad = math.radians(rotation_angle)

        # 第一根半径
        r1_x = x0 + radius * math.sin(y_axis_rad + rotation_rad)
        r1_y = y0 + radius * math.cos(y_axis_rad + rotation_rad)
        ax.plot([x0, r1_x], [y0, r1_y], 'r-', linewidth=2, label='Radius 1')

        if angle is not None:
            if calculate_chord:
                theta_rad = math.radians(angle)
            else:
                theta_rad = math.radians(angle)

            # 第二根半径
            r2_x = x0 + radius * math.sin(y_axis_rad + rotation_rad + theta_rad)
            r2_y = y0 + radius * math.cos(y_axis_rad + rotation_rad + theta_rad)
            ax.plot([x0, r2_x], [y0, r2_y], 'b-', linewidth=2, label='Radius 2')

            # 绘制弦长
            ax.plot([r1_x, r2_x], [r1_y, r2_y], 'k--', linewidth=2, label='Chord')

            # 标注角度
            angle_patch = patches.Arc((x0, y0), radius*0.6, radius*0.6, angle=0,
                                      theta1=math.degrees(rotation_rad),
                                      theta2=math.degrees(rotation_rad + theta_rad),
                                      color='m')
            ax.add_patch(angle_patch)
            ax.text(x0 + radius*0.4*math.sin(y_axis_rad + rotation_rad + theta_rad/2),
                    y0 + radius*0.4*math.cos(y_axis_rad + rotation_rad + theta_rad/2),
                    f"{math.degrees(theta_rad):.2f}°", color='m', fontsize=10)

            # 标注弦长
            chord_length = math.sqrt((r2_x - r1_x)**2 + (r2_y - r1_y)**2)
            mid_chord_x = (r1_x + r2_x) / 2
            mid_chord_y = (r1_y + r2_y) / 2
            ax.text(mid_chord_x, mid_chord_y, f"c={chord_length:.2f}", fontsize=10, color='k')

            # 计算并标注交点坐标
            intersection1 = (r1_x, r1_y)
            intersection2 = (r2_x, r2_y)
            ax.plot(*intersection1, 'go')
            ax.plot(*intersection2, 'go')
            ax.text(intersection1[0], intersection1[1], f"({intersection1[0]:.2f}, {intersection1[1]:.2f})",
                    fontsize=8, color='g')
            ax.text(intersection2[0], intersection2[1], f"({intersection2[0]:.2f}, {intersection2[1]:.2f})",
                    fontsize=8, color='g')

            ax.legend()

        self.draw_origin(ax, x0, y0)

        # 动态轴范围
        if radius is not None:
            limit = radius * 1.5
        else:
            points = []
            if x1 is not None and y1 is not None:
                points.append(math.sqrt((x1 - x0)**2 + (y1 - y0)**2))
            if x2 is not None and y2 is not None:
                points.append(math.sqrt((x2 - x0)**2 + (y2 - y0)**2))
            if points:
                limit = max(points) * 1.5
            else:
                limit = 10
        ax.set_xlim(x0 - limit, x0 + limit)
        ax.set_ylim(y0 - limit, y0 + limit)

        self.canvas.draw()

    def draw_origin(self, ax, x0, y0):
        ax.plot(x0, y0, 'ko', label='Origin')
        ax.text(x0, y0, f" Origin ({x0:.2f}, {y0:.2f})", fontsize=10, verticalalignment='bottom')

    def update_plot(self):
        self.plot_graph()

    def update_history(self):
        self.history_text.clear()
        for record in self.history[-100:]:
            self.history_text.append(record)

    def export_history(self):
        if not self.history:
            QMessageBox.information(self, "信息", "没有历史记录可导出。")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "保存历史记录", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["历史记录"])
                    for record in self.history:
                        writer.writerow([record])
                QMessageBox.information(self, "成功", "历史记录已成功导出。")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    calculator = DistanceAndAngleCalculator()
    calculator.show()
    sys.exit(app.exec_())
