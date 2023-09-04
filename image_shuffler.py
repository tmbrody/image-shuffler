import os
import random
import sys
import configparser
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QToolButton, QVBoxLayout, QHBoxLayout, QWidget, QAction
from PyQt5.QtGui import QPixmap, QKeySequence, QIcon

class ImageViewer(QMainWindow):
    def __init__(self, image_path):
        super().__init__()

        self.next_arrow_button = QIcon("icons/next_arrow.png")
        self.previous_arrow_button = QIcon("icons/previous_arrow.png")
        self.shuffle_on_button = QIcon("icons/shuffle.png")
        self.shuffle_off_button = QIcon("icons/shuffle_off.png")

        self.config = configparser.ConfigParser()
        self.config.read("config.ini", encoding="utf-8")

        if self.config.has_option("Settings", "width") and self.config.has_option("Settings", "height"):
            self.width = int(self.config.get("Settings", "width"))
            self.height = int(self.config.get("Settings", "height"))
        else:
            self.width = 1280
            self.height = 720

        self.setGeometry(100, 100, self.width, self.height)
        self.setWindowTitle("Image Shuffler")

        self.image_width = 800
        self.image_height = 600

        self.resizeEvent = self.on_resize

        self.image_dir = image_path
        self.image_paths = []
        self.shuffling = False
        self.current_index = 0

        self.viewed_images = [self.current_index]
        self.viewed_images_index = -1

        self.display_image()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        central_layout = QVBoxLayout()


        top_layout = QHBoxLayout()

        self.shuffle_button = QToolButton(self)
        self.shuffle_button.clicked.connect(self.shuffle_images)
        self.shuffle_button.setAutoRaise(True)
        self.shuffle_button.setIconSize(QSize(100, 100))
        self.shuffle_button.setIcon(self.shuffle_off_button)

        self.s_shortcut = QAction(self)
        self.s_shortcut.setShortcut(QKeySequence("s"))
        self.s_shortcut.triggered.connect(self.shuffle_images)
        self.addAction(self.s_shortcut)

        self.shuffle_button.setFixedHeight(100)

        top_layout.addWidget(self.shuffle_button)

        central_layout.addLayout(top_layout)


        canvas_layout = QHBoxLayout()
        self.canvas = QLabel()
        canvas_layout.addWidget(self.canvas)
        central_layout.addLayout(canvas_layout)

        
        next_and_previous_button_layout = QHBoxLayout()

        self.previous_button = QToolButton(self)
        self.previous_button.clicked.connect(self.previous_image)
        self.previous_button.setAutoRaise(True)
        self.previous_button.setIconSize(QSize(100, 100))
        self.previous_button.setIcon(self.previous_arrow_button)

        self.left_shortcut = QAction(self)
        self.left_shortcut.setShortcut(QKeySequence("Left"))
        self.left_shortcut.triggered.connect(self.previous_image)
        self.addAction(self.left_shortcut)

        next_and_previous_button_layout.addWidget(self.previous_button)

        self.next_button = QToolButton(self)
        self.next_button.clicked.connect(self.next_image)
        self.next_button.setAutoRaise(True)
        self.next_button.setIconSize(QSize(100, 100))
        self.next_button.setIcon(self.next_arrow_button)

        self.right_shortcut = QAction(self)
        self.right_shortcut.setShortcut(QKeySequence("Right"))
        self.right_shortcut.triggered.connect(self.next_image)
        self.addAction(self.right_shortcut)

        next_and_previous_button_layout.addStretch()
        next_and_previous_button_layout.addWidget(self.next_button)

        central_layout.addLayout(next_and_previous_button_layout)


        self.central_widget.setLayout(central_layout)

        self.load_images()
        self.display_image()
    
    def load_images(self):
        self.image_paths = [os.path.join(self.image_dir, file) for file in os.listdir(self.image_dir) 
                            if file.endswith(('.jpg', '.jpeg', '.png'))]

    def shuffle_images(self, event=None):
        self.shuffling = not self.shuffling

        current_pixmap = self.shuffle_button.icon().pixmap(QSize(32, 32))
        shuffle_off_pixmap = self.shuffle_off_button.pixmap(QSize(32, 32))

        if current_pixmap and shuffle_off_pixmap:
            if current_pixmap.toImage() == shuffle_off_pixmap.toImage():
                new_icon = self.shuffle_on_button
            else:
                new_icon = self.shuffle_off_button
            self.shuffle_button.setIcon(new_icon)

    def next_image(self, event=None):
        if self.viewed_images_index != -1:
            self.current_index = self.viewed_images[self.viewed_images_index + 1]
            self.viewed_images_index += 1
        else:
            if self.shuffling:
                increase_by = random.randint(1, len(self.image_paths) - 1)
            else:
                increase_by = 1

            self.current_index = (self.current_index + increase_by) % len(self.image_paths)
            self.viewed_images.append(self.current_index)

        self.display_image()

    def previous_image(self, event=None):
        if self.current_index != 0:
            try:
                self.viewed_images_index -= 1

                self.current_index = self.viewed_images[self.viewed_images_index]
            except IndexError:
                self.viewed_images_index = -1
                self.current_index = self.viewed_images[self.viewed_images_index]

            self.display_image()

    def display_image(self):
        if self.image_paths:
            image_path = self.image_paths[self.current_index]

            end_index = image_path.rfind("\\")
            file_name = image_path[(end_index + 1):]

            self.setWindowTitle(f"Image Shuffler - {file_name}")

            image = QPixmap(image_path)
            image = image.scaled(self.image_width, self.image_height, Qt.KeepAspectRatio)

            self.canvas.setPixmap(image)
            self.canvas.setAlignment(Qt.AlignCenter)

    def wheelEvent(self, event):
        max_image_width = self.width - 300
        max_image_height = self.height - 300

        delta = event.angleDelta().y()

        if delta > 0:
            self.image_width = min(self.image_width + 100, max_image_width)
            self.image_height = min(self.image_height + 100, max_image_height)
        else:
            self.image_width = max(self.image_width - 100, 100)
            self.image_height = max(self.image_height - 100, 100)
        
        self.display_image()

    def on_resize(self, event):
        self.width = event.size().width()
        self.height = event.size().height()

    def closeEvent(self, event):
        if not self.config.has_section("Settings"):
            self.config.add_section("Settings")

        self.config.set("Settings", "width", str(self.width))
        self.config.set("Settings", "height", str(self.height))

        with open("config.ini", "w", encoding="utf-8") as configfile:
            self.config.write(configfile)
        
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    home_dir = os.path.expanduser("~")
    image_dir = os.path.join(home_dir, "Pictures")
    viewer = ImageViewer(image_dir)
    viewer.show()
    sys.exit(app.exec_())
