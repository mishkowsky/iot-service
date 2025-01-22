import sys

from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider

from src.data_simulator.manager import DeviceManager, MAX_DEVICES_COUNT
from loguru import logger


class DeviceSimulatorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.device_manager = DeviceManager()

        self.setWindowTitle("Настройка устройств и частоты сообщений")
        self.setGeometry(100, 100, 400, 200)

        # Создание вертикального layout
        layout = QVBoxLayout()

        # Слайдер для количества устройств
        self.device_slider = QSlider()
        self.device_slider.setOrientation(QtCore.Qt.Orientation.Horizontal)  # Горизонтальный слайдер
        self.device_slider.setRange(0, MAX_DEVICES_COUNT)  # Устанавливаем диапазон от 1 до 100
        self.device_slider.setValue(0)  # Устанавливаем значение по умолчанию
        self.device_slider.valueChanged.connect(self.update_device_label)
        self.device_slider.valueChanged.connect(self.on_device_slider_change)  # Обработчик события

        self.device_label = QLabel("Количество устройств: 0")

        # Слайдер для частоты отправки сообщений
        self.frequency_slider = QSlider()
        self.frequency_slider.setOrientation(QtCore.Qt.Orientation.Horizontal)  # Горизонтальный слайдер
        self.frequency_slider.setRange(1, 120)  # Устанавливаем диапазон от 1 до 10
        self.frequency_slider.setValue(1)  # Устанавливаем значение по умолчанию
        self.frequency_slider.valueChanged.connect(self.update_frequency_label)
        self.frequency_slider.valueChanged.connect(self.on_frequency_slider_change)  # Обработчик события

        self.frequency_label = QLabel("Частота отправки сообщений: 1 раз в минуту")

        # Добавление элементов в layout
        layout.addWidget(self.device_label)
        layout.addWidget(self.device_slider)
        layout.addWidget(self.frequency_label)
        layout.addWidget(self.frequency_slider)

        self.setLayout(layout)

    def update_device_label(self, value):
        self.device_label.setText(f"Количество устройств: {value}")

    def update_frequency_label(self, value):
        self.frequency_label.setText(f"Частота отправки сообщений: {value} раз в минуту")

    def on_device_slider_change(self, value):
        if self.device_manager.active_device_count != int(value):
            logger.debug(f'NEW DEVICE COUNT: {value}')
            self.device_manager.update_terminating(int(value), self.device_manager.delay)

    def on_frequency_slider_change(self, value):
        delay_beetwen_requests = 60 / int(value)
        if self.device_manager.delay != delay_beetwen_requests:
            logger.debug(f'NEW DELAY VALUE: {delay_beetwen_requests}')
            self.device_manager.update_terminating(self.device_manager.active_device_count, delay_beetwen_requests)

    def close(self):
        self.device_manager.terminate_all()
        super().close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeviceSimulatorApp()
    window.show()
    sys.exit(app.exec())
