import json
import math
import os
import sys

import qtmodern.styles
import qtmodern.windows
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QGroupBox, \
    QGridLayout, QDialog, QDialogButtonBox


# 计算两点间的距离
def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# 计算夹角
def calculate_angle(x1, y1, x2, y2, base_x, base_y):
    vector1_x = x1 - base_x
    vector1_y = y1 - base_y
    vector2_x = x2 - base_x
    vector2_y = y2 - base_y

    dot_product = vector1_x * vector2_x + vector1_y * vector2_y
    magnitude1 = math.sqrt(vector1_x ** 2 + vector1_y ** 2)
    magnitude2 = math.sqrt(vector2_x ** 2 + vector2_y ** 2)

    cos_theta = dot_product / (magnitude1 * magnitude2)
    return math.degrees(math.acos(cos_theta))


# 计算弦长、角度和半径
def calculate_chord_length_or_angle_or_radius(chord_length=None, angle=None, radius=None):
    if chord_length is None and angle is None:
        return None, "Both chord length and angle are required"
    if chord_length is None:  # 计算弦长
        return 2 * radius * math.sin(math.radians(angle) / 2), "Chord length"
    if angle is None:  # 计算角度
        return 2 * math.asin(chord_length / (2 * radius)) * 180 / math.pi, "Angle"
    if radius is None:  # 计算半径
        return chord_length / (2 * math.sin(math.radians(angle) / 2)), "Radius"
    return None, "Invalid input"


# 保存历史记录
def save_history(record):
    if not os.path.exists("history.json"):
        with open("history.json", 'w') as file:
            json.dump([], file)

    with open("history.json", 'r+') as file:
        history = json.load(file)
        history.append(record)
        file.seek(0)
        json.dump(history, file)


# 读取历史记录
def load_history():
    if os.path.exists("history.json"):
        with open("history.json", 'r') as file:
            return json.load(file)
    return []


# UI设计
class GeometryCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Geometry Calculator")
        self.setGeometry(100, 100, 600, 600)

        # UI组件初始化
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.create_distance_calculator()
        self.create_angle_calculator()
        self.create_chord_calculator()

        self.history_button = QPushButton("Show History", self)
        self.history_button.clicked.connect(self.show_history)
        self.layout.addWidget(self.history_button)

        self.update_history()

    def create_distance_calculator(self):
        # 距离计算模块
        self.distance_group = QGroupBox("Distance Calculator")
        self.distance_layout = QGridLayout()

        # X1和Y1的标签与输入框
        self.x1_label = QLabel("X1:")
        self.x1_input = QLineEdit(self)
        self.distance_layout.addWidget(self.x1_label, 0, 0)
        self.distance_layout.addWidget(self.x1_input, 0, 1)

        self.y1_label = QLabel("Y1:")
        self.y1_input = QLineEdit(self)
        self.distance_layout.addWidget(self.y1_label, 1, 0)
        self.distance_layout.addWidget(self.y1_input, 1, 1)

        # X2和Y2的标签与输入框
        self.x2_label = QLabel("X2:")
        self.x2_input = QLineEdit(self)
        self.distance_layout.addWidget(self.x2_label, 2, 0)
        self.distance_layout.addWidget(self.x2_input, 2, 1)

        self.y2_label = QLabel("Y2:")
        self.y2_input = QLineEdit(self)
        self.distance_layout.addWidget(self.y2_label, 3, 0)
        self.distance_layout.addWidget(self.y2_input, 3, 1)

        # 计算按钮
        self.calculate_distance_button = QPushButton("Calculate Distance", self)
        self.calculate_distance_button.clicked.connect(self.calculate_distance)
        self.distance_layout.addWidget(self.calculate_distance_button, 4, 0, 1, 2)

        # 显示结果
        self.distance_result_label = QLabel("Result: ")
        self.distance_layout.addWidget(self.distance_result_label, 5, 0, 1, 2)

        self.distance_group.setLayout(self.distance_layout)
        self.layout.addWidget(self.distance_group)

    def create_angle_calculator(self):
        # 角度计算模块
        self.angle_group = QGroupBox("Angle Calculator")
        self.angle_layout = QGridLayout()

        # 坐标A X 和 Y
        self.angle_x_label = QLabel("X for A:")
        self.angle_x_input = QLineEdit(self)
        self.angle_layout.addWidget(self.angle_x_label, 0, 0)
        self.angle_layout.addWidget(self.angle_x_input, 0, 1)

        self.angle_y_label = QLabel("Y for A:")
        self.angle_y_input = QLineEdit(self)
        self.angle_layout.addWidget(self.angle_y_label, 1, 0)
        self.angle_layout.addWidget(self.angle_y_input, 1, 1)

        # 坐标B X 和 Y
        self.base_x_label = QLabel("X for B:")
        self.base_x_input = QLineEdit(self)
        self.angle_layout.addWidget(self.base_x_label, 2, 0)
        self.angle_layout.addWidget(self.base_x_input, 2, 1)

        self.base_y_label = QLabel("Y for B:")
        self.base_y_input = QLineEdit(self)
        self.angle_layout.addWidget(self.base_y_label, 3, 0)
        self.angle_layout.addWidget(self.base_y_input, 3, 1)

        # 基准点坐标 X 和 Y
        self.base_point_x_label = QLabel("Base X:")
        self.base_point_x_input = QLineEdit(self)
        self.angle_layout.addWidget(self.base_point_x_label, 4, 0)
        self.angle_layout.addWidget(self.base_point_x_input, 4, 1)

        self.base_point_y_label = QLabel("Base Y:")
        self.base_point_y_input = QLineEdit(self)
        self.angle_layout.addWidget(self.base_point_y_label, 5, 0)
        self.angle_layout.addWidget(self.base_point_y_input, 5, 1)

        # 计算按钮
        self.calculate_angle_button = QPushButton("Calculate Angle", self)
        self.calculate_angle_button.clicked.connect(self.calculate_angle)
        self.angle_layout.addWidget(self.calculate_angle_button, 6, 0, 1, 2)

        # 显示结果
        self.angle_result_label = QLabel("Result: ")
        self.angle_layout.addWidget(self.angle_result_label, 7, 0, 1, 2)

        self.angle_group.setLayout(self.angle_layout)
        self.layout.addWidget(self.angle_group)

    def create_chord_calculator(self):
        # 弦长、角度、半径计算模块
        self.chord_group = QGroupBox("Chord/Angle/Radius Calculator")
        self.chord_layout = QGridLayout()

        # 弦长、角度、半径输入框
        self.chord_length_label = QLabel("Chord Length:")
        self.chord_length_input = QLineEdit(self)
        self.chord_layout.addWidget(self.chord_length_label, 0, 0)
        self.chord_layout.addWidget(self.chord_length_input, 0, 1)

        self.angle_label = QLabel("Angle:")
        self.angle_input = QLineEdit(self)
        self.chord_layout.addWidget(self.angle_label, 1, 0)
        self.chord_layout.addWidget(self.angle_input, 1, 1)

        self.radius_label = QLabel("Radius:")
        self.radius_input = QLineEdit(self)
        self.chord_layout.addWidget(self.radius_label, 2, 0)
        self.chord_layout.addWidget(self.radius_input, 2, 1)

        # 计算按钮
        self.calculate_chord_button = QPushButton("Calculate Chord/Angle/Radius", self)
        self.calculate_chord_button.clicked.connect(self.calculate_chord)
        self.chord_layout.addWidget(self.calculate_chord_button, 3, 0, 1, 2)

        # 显示结果
        self.chord_result_label = QLabel("Result: ")
        self.chord_layout.addWidget(self.chord_result_label, 4, 0, 1, 2)

        self.chord_group.setLayout(self.chord_layout)
        self.layout.addWidget(self.chord_group)

    def calculate_distance(self):
        x1 = float(self.x1_input.text())
        y1 = float(self.y1_input.text())
        x2 = float(self.x2_input.text())
        y2 = float(self.y2_input.text())
        distance = calculate_distance(x1, y1, x2, y2)
        self.distance_result_label.setText(f"Distance: {distance}")
        save_history(f"Distance between ({x1}, {y1}) and ({x2}, {y2}): {distance}")
        self.update_history()

    def calculate_angle(self):
        x1 = float(self.angle_x_input.text())
        y1 = float(self.angle_y_input.text())
        x2 = float(self.base_x_input.text())
        y2 = float(self.base_y_input.text())
        base_x = float(self.base_point_x_input.text())
        base_y = float(self.base_point_y_input.text())
        angle = calculate_angle(x1, y1, x2, y2, base_x, base_y)
        self.angle_result_label.setText(f"Angle: {angle}")
        save_history(f"Angle between ({x1}, {y1}), ({x2}, {y2}) with base ({base_x}, {base_y}): {angle}")
        self.update_history()

    def calculate_chord(self):
        chord_length = self.chord_length_input.text()
        angle = self.angle_input.text()
        radius = self.radius_input.text()

        # 输入验证
        if not chord_length and not angle:
            self.chord_result_label.setText("Please provide either chord length or angle.")
            return

        chord_length = float(chord_length) if chord_length else None
        angle = float(angle) if angle else None
        radius = float(radius) if radius else None

        result, result_type = calculate_chord_length_or_angle_or_radius(chord_length=chord_length, angle=angle,
                                                                        radius=radius)

        if result is None:
            self.chord_result_label.setText(result_type)
        else:
            self.chord_result_label.setText(f"{result_type}: {result}")

        # 保存历史记录
        save_history(f"{result_type}: {result}")
        self.update_history()

    def update_history(self):
        history = load_history()

    def show_history(self):
        history = load_history()
        history_dialog = QDialog(self)
        history_dialog.setWindowTitle("History")
        layout = QVBoxLayout()

        history_text = QLabel("\n".join(history))
        layout.addWidget(history_text)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(history_dialog.close)  # 修复关闭按钮
        layout.addWidget(buttons)

        history_dialog.setLayout(layout)
        history_dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    qtmodern.styles.dark(app)
    window = GeometryCalculator()
    mw = qtmodern.windows.ModernWindow(window)
    mw.show()
    sys.exit(app.exec_())
