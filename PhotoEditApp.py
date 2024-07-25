import sys
import cv2
import numpy as np

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout, QHBoxLayout,
    QTabWidget,
    QWidget,
    QPushButton,
    QFileDialog,
    QSlider
)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.filepath = None
        self.pic_height = 500
        self.slider_value = 0

        # original pic
        self.ori_picture = QLabel()
        self.ori_picture.setFixedSize(self.pic_height, 600)
        #self.ori_picture.setPixmap(QPixmap(self.filepath).scaledToHeight(self.pic_height))
        self.ori_picture.setAlignment(Qt.AlignHCenter)

        ori_container = QWidget()
        ori_layout = QVBoxLayout()
        ori_layout.addWidget(self.ori_picture)
        ori_layout.setAlignment(Qt.AlignCenter| Qt.AlignTop)
        ori_container.setLayout(ori_layout)

        # 仮の編集後画像を表示する
        self.mod_picture = QLabel()
        self.mod_picture.setFixedSize(self.pic_height, 600)
        #self.mod_picture.setPixmap(QPixmap(self.filepath).scaledToHeight(self.pic_height))
        self.mod_picture.setAlignment(Qt.AlignHCenter)

        mod_container = QWidget()
        mod_layout = QVBoxLayout()
        mod_layout.addWidget(self.mod_picture)
        mod_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        mod_container.setLayout(mod_layout)

        # tabでoriginal picとmodified picをチェック
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setFixedSize(800, 550)
        self.tabs.setMovable(True)

        self.tabs.addTab(mod_container, "modified")
        self.tabs.addTab(ori_container, "original")

        tab_bar = self.tabs.tabBar()
        tab_bar.setStyleSheet("""
            QTabBar::tab {
                min-width: 300px;
                height: 20px;
                padding: 5px;
                font-size: 10.5px;
                background-color: #F5F5F5
            }
            QTabBar::tab:hover {
                background-color: #E0E0E0; /* ホバー時の淡いグレー（色調整可能） */
            }
            QTabBar::tab:selected {
                color: #FFFFFF;
                background-color: #0078D7;  /* 選択されたタブの背景色を青に設定 */
            }
        """)

        # choose fileボタン
        btn_stylesheet = """
                    QPushButton {
                        background-color: #F5F5F5; /* 押していない時のミルキーな白色 */
                        border-radius: 10px; /* ボタンの角を丸くする */
                        font-size: 10.5px; /* フォントサイズ */
                        padding: 10px; /* 内側の余白 */
                    }
                    QPushButton:hover {
                        background-color: #E0E0E0; /* ホバー時の淡いグレー（色調整可能） */
                    }
                    QPushButton:pressed, QPushButton:checked {
                        background-color: #0078D7; /* 押した時の青色 */
                        color: #FFFFFF; /* 文字色を白にする */
                    }
                """

        self.btn_file = QPushButton("File")
        self.btn_file.setFixedSize(QSize(120, 50))
        self.btn_file.setCheckable(True)
        self.btn_file.clicked.connect(self.open_file)

        self.btn_file.setStyleSheet(btn_stylesheet)

        # フィルタ選択
        self.btn_mosaic = QPushButton("mosaic")
        self.btn_mosaic.setFixedSize(QSize(120, 50))
        self.btn_mosaic.setCheckable(True)
        self.btn_mosaic.toggled.connect(self.mosaic_toggle)

        self.btn_mosaic.setStyleSheet(btn_stylesheet)

        self.btn_hist = QPushButton("contrast\nequalization")
        self.btn_hist.setFixedSize(QSize(120, 50))
        self.btn_hist.setCheckable(True)
        self.btn_hist.toggled.connect(self.hist_toggle)

        self.btn_hist.setStyleSheet(btn_stylesheet)

        # color correction button
        correction_btn_stylesheet = """
                            QPushButton {
                                background-color: #F5F5F5; /* 押していない時のミルキーな白色 */
                                border-radius: 10px; /* ボタンの角を丸くする */
                                font-size: 9px; /* フォントサイズ */
                                padding: 5px; /* 内側の余白 */
                            }
                            QPushButton:hover {
                                background-color: #E0E0E0; /* ホバー時の淡いグレー（色調整可能） */
                            }
                            QPushButton:pressed, QPushButton:checked {
                                background-color: #0078D7; /* 押した時の青色 */
                                color: #FFFFFF; /* 文字色を白にする */
                            }
                        """

        self.correct_label = QLabel("color correction")
        self.correct_label.setFixedSize(120, 20)
        self.correct_label.setAlignment(Qt.AlignHCenter)
        self.correct_label.setStyleSheet("""
                            QLabel {
                                font-size: 10.5px; /* フォントサイズ */
                            }
        """)

        self.btn_correct_r = QPushButton("RED")
        self.btn_correct_r.setFixedSize(QSize(40, 50))
        self.btn_correct_r.setCheckable(True)
        self.btn_correct_r.toggled.connect(self.red_toggle)

        self.btn_correct_r.setStyleSheet(correction_btn_stylesheet)

        self.btn_correct_g = QPushButton("GREEN")
        self.btn_correct_g.setFixedSize(QSize(40, 50))
        self.btn_correct_g.setCheckable(True)
        self.btn_correct_g.toggled.connect(self.green_toggle)

        self.btn_correct_g.setStyleSheet(correction_btn_stylesheet)

        self.btn_correct_b = QPushButton("BLUE")
        self.btn_correct_b.setFixedSize(QSize(40, 50))
        self.btn_correct_b.setCheckable(True)
        self.btn_correct_b.toggled.connect(self.blue_toggle)

        self.btn_correct_b.setStyleSheet(correction_btn_stylesheet)

        self.correction_buttons = [
            self.btn_correct_r, self.btn_correct_g,
            self.btn_correct_b
        ]

        # color correction layout
        self.layout_rgb = QHBoxLayout()
        for btn in self.correction_buttons:
            self.layout_rgb.addWidget(btn)
        self.layout_label_rgb = QVBoxLayout()
        self.layout_label_rgb.addWidget(self.correct_label)
        self.layout_label_rgb.addLayout(self.layout_rgb)
        self.layout_label_rgb.setSpacing(0)

        # denoising
        self.btn_denoising = QPushButton("denoising")
        self.btn_denoising.setFixedSize(QSize(120, 50))
        self.btn_denoising.setCheckable(True)
        self.btn_denoising.toggled.connect(self.denoising_toggle)
        self.btn_denoising.setStyleSheet(btn_stylesheet)

        self.buttons = [
            self.btn_mosaic, self.btn_hist, self.btn_denoising
        ]

        # button layout
        self.layout_btn = QVBoxLayout()
        self.layout_btn.addWidget(self.btn_file)
        for btn in self.buttons:
            self.layout_btn.addWidget(btn)
        self.layout_btn.addLayout(self.layout_label_rgb)

        # sliders

        self.sliders = QSlider()
        self.sliders.setVisible(False)
        self.sliders.valueChanged.connect(self.mosaic)

        self.slider_container = QWidget()
        self.slider_container.setFixedSize(20, 200)
        slider_layout = QVBoxLayout()
        slider_layout.addWidget(self.sliders)
        slider_layout.setAlignment(Qt.AlignCenter)
        self.slider_container.setLayout(slider_layout)

        # layout
        self.layout_v = QVBoxLayout()
        self.layout_v.addWidget(self.tabs)

        self.layout_h = QHBoxLayout()
        self.layout_h.addLayout(self.layout_v)
        self.layout_h.addWidget(self.slider_container)
        self.layout_h.addLayout(self.layout_btn)

        # widget
        self.widget = QWidget()
        self.widget.setLayout(self.layout_h)
        self.setCentralWidget(self.widget)

        self.setFixedSize(QSize(1000, 600))
        self.setWindowTitle("Photo soup")

    def open_file(self):
        options = QFileDialog.Options()
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_dialog.setNameFilter("Images (*.png *.xpm *.jpg *.jpeg *.bmp)")
        if file_dialog.exec_() == QFileDialog.Accepted:
            self.filepath = file_dialog.selectedFiles()[0]
            self.update_image()
        self.btn_file.setChecked(False)

    def update_image(self):
        for btn in self.buttons:
            btn.setChecked(False)
        # QPixmapで読み込んだ画像が横向きになるケースあったため、opencvで読み込む。
        im = cv2.imread(self.filepath)  # 色の順番はRGBではなくBGR
        im = im[:, :, [2, 1, 0]]
        height, width, channel = im.shape
        bytes_per_line = 3 * width
        im_bytes = im.tobytes()
        modified = QImage(im_bytes, width, height, bytes_per_line, QImage.Format_RGB888)
        self.ori_picture.setPixmap(QPixmap(modified).scaledToHeight(self.pic_height))
        self.mod_picture.setPixmap(QPixmap(modified).scaledToHeight(self.pic_height))

    def mosaic_toggle(self, checked):
        if self.filepath is not None:
            if checked:
                self.check_mosaic_btn()
            else:
                self.releasebtn()
        else:
            self.btn_mosaic.setChecked(False)
            self.mod_picture.setText("Please choose a file first!")

    def hist_toggle(self, checked):
        if self.filepath is not None:
            if checked:
                self.equal_hist()
            else:
                self.releasebtn()
        else:
            self.btn_hist.setChecked(False)
            self.mod_picture.setText("Please choose a file first!")

    def red_toggle(self, checked):
        if self.filepath is not None:
            if checked:
                self.color_correction_r()
            else:
                self.releasebtn()
        else:
            self.btn_correct_r.setChecked(False)
            self.mod_picture.setText("Please choose a file first!")

    def green_toggle(self, checked):
        if self.filepath is not None:
            if checked:
                self.color_correction_g()
            else:
                self.releasebtn()
        else:
            self.btn_correct_g.setChecked(False)
            self.mod_picture.setText("Please choose a file first!")

    def blue_toggle(self, checked):
        if self.filepath is not None:
            if checked:
                self.color_correction_b()
            else:
                self.releasebtn()
        else:
            self.btn_correct_b.setChecked(False)
            self.mod_picture.setText("Please choose a file first!")

    def denoising_toggle(self, checked):
        if self.filepath is not None:
            if checked:
                self.denoising()
            else:
                self.releasebtn()
        else:
            self.btn_denoising.setChecked(False)
            self.mod_picture.setText("Please choose a file first!")

    def update_sliders(self, mi, ma, steps):
        self.sliders.setMinimum(mi)
        self.sliders.setMaximum(ma)
        self.sliders.setSingleStep(steps)
        self.sliders.setVisible(True)

    #def slider_value_changed(self, i):
    #    self.slider_value = float(i)
    #    print(self.slider_value)

    def check_mosaic_btn(self):
        for btn in self.buttons:
            if btn is not self.btn_mosaic:
                btn.setChecked(False)
        for btn in self.correction_buttons:
            if btn is not self.btn_mosaic:
                btn.setChecked(False)
        self.update_sliders(1, 20, 20)
        #print(self.btn_mosaic.isChecked())

    def mosaic(self, value):
        im = cv2.imread(self.filepath) # 色の順番はRGBではなくBGR
        im = im[:, :, [2, 1, 0]]
        #print(value)
        ratio = value/100
        #print(ratio)
        small = cv2.resize(im, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_NEAREST)
        mod = cv2.resize(small, im.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)

        height, width, channel = mod.shape
        bytes_per_line = 3 * width
        modified = QImage(mod.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.mod_picture.setPixmap(QPixmap(modified).scaledToHeight(self.pic_height))

    def equal_hist(self):
        # 他のボタンをfalseにする
        for btn in self.buttons:
            if btn is not self.btn_hist:
                btn.setChecked(False)
        for btn in self.correction_buttons:
            if btn is not self.btn_hist:
                btn.setChecked(False)
        self.sliders.setVisible(False)

        bgr_im = cv2.imread(self.filepath)
        yuv_im = cv2.cvtColor(bgr_im, cv2.COLOR_BGR2YUV)
        yuv_im[:, :, 0] = cv2.equalizeHist(yuv_im[:, :, 0])
        mod = cv2.cvtColor(yuv_im, cv2.COLOR_YUV2BGR)
        mod = mod[:, :, [2, 1, 0]]

        height, width, channel = mod.shape
        bytes_per_line = 3 * width
        mod_bytes = mod.tobytes()
        modified = QImage(mod_bytes, width, height, bytes_per_line, QImage.Format_RGB888)
        self.mod_picture.setPixmap(QPixmap(modified).scaledToHeight(self.pic_height))

    def color_correction_r(self):
        # 他のボタンをfalseにする
        for btn in self.buttons:
            if btn is not self.btn_correct_r:
                btn.setChecked(False)
        for btn in self.correction_buttons:
            if btn is not self.btn_correct_r:
                btn.setChecked(False)
        self.sliders.setVisible(False)

        bgr_im = cv2.imread(self.filepath)
        b, g, r = cv2.split(bgr_im)

        # ルックアップテーブルの生成
        gamma = 2
        look_up_table = np.zeros((256, 1), dtype=np.uint8)
        for i in range(256):
            look_up_table[i][0] = (i / 255) ** (1.0 / gamma) * 255

        r_lut = cv2.LUT(r, look_up_table)  # Rに対してルックアップテーブル適用
        mod = cv2.merge([b, g, r_lut])  # B,G,変換後Rをマージ
        mod = mod[:, :, [2, 1, 0]]
        height, width, channel = mod.shape
        bytes_per_line = 3 * width
        mod_bytes = mod.tobytes()
        modified = QImage(mod_bytes, width, height, bytes_per_line, QImage.Format_RGB888)
        self.mod_picture.setPixmap(QPixmap(modified).scaledToHeight(self.pic_height))

    def color_correction_g(self):
        # 他のボタンをfalseにする
        for btn in self.buttons:
            if btn is not self.btn_correct_g:
                btn.setChecked(False)
        for btn in self.correction_buttons:
            if btn is not self.btn_correct_g:
                btn.setChecked(False)

        self.sliders.setVisible(False)

        bgr_im = cv2.imread(self.filepath)
        b, g, r = cv2.split(bgr_im)

        # ルックアップテーブルの生成
        gamma = 2
        look_up_table = np.zeros((256, 1), dtype=np.uint8)
        for i in range(256):
            look_up_table[i][0] = (i / 255) ** (1.0 / gamma) * 255

        g_lut = cv2.LUT(g, look_up_table)  # Rに対してルックアップテーブル適用
        mod = cv2.merge([b, g_lut, r])  # B,G,変換後Rをマージ
        mod = mod[:, :, [2, 1, 0]]
        height, width, channel = mod.shape
        bytes_per_line = 3 * width
        mod_bytes = mod.tobytes()
        modified = QImage(mod_bytes, width, height, bytes_per_line, QImage.Format_RGB888)
        self.mod_picture.setPixmap(QPixmap(modified).scaledToHeight(self.pic_height))

    def color_correction_b(self):
        # 他のボタンをfalseにする
        for btn in self.buttons:
            if btn is not self.btn_correct_b:
                btn.setChecked(False)
        for btn in self.correction_buttons:
            if btn is not self.btn_correct_b:
                btn.setChecked(False)

        self.sliders.setVisible(False)

        bgr_im = cv2.imread(self.filepath)
        b, g, r = cv2.split(bgr_im)

        # ルックアップテーブルの生成
        gamma = 2
        look_up_table = np.zeros((256, 1), dtype=np.uint8)
        for i in range(256):
            look_up_table[i][0] = (i / 255) ** (1.0 / gamma) * 255

        b_lut = cv2.LUT(b, look_up_table)  # Rに対してルックアップテーブル適用
        mod = cv2.merge([b_lut, g, r])  # B,G,変換後Rをマージ
        mod = mod[:, :, [2, 1, 0]]
        height, width, channel = mod.shape
        bytes_per_line = 3 * width
        mod_bytes = mod.tobytes()
        modified = QImage(mod_bytes, width, height, bytes_per_line, QImage.Format_RGB888)
        self.mod_picture.setPixmap(QPixmap(modified).scaledToHeight(self.pic_height))

    def denoising(self):
        # 他のボタンをfalseにする
        for btn in self.buttons:
            if btn is not self.btn_denoising:
                btn.setChecked(False)
        for btn in self.correction_buttons:
            if btn is not self.btn_denoising:
                btn.setChecked(False)

        self.sliders.setVisible(False)

        im = cv2.imread(self.filepath) # 色の順番はRGBではなくBGR
        im = im[:, :, [2, 1, 0]]

        kernel_size = 11
        mod = cv2.medianBlur(im, kernel_size)
        height, width, channel = mod.shape
        bytes_per_line = 3 * width
        mod_bytes = mod.tobytes()
        modified = QImage(mod_bytes, width, height, bytes_per_line, QImage.Format_RGB888)
        self.mod_picture.setPixmap(QPixmap(modified).scaledToHeight(self.pic_height))

    def releasebtn(self):
        im = cv2.imread(self.filepath)  # 色の順番はRGBではなくBGR
        im = im[:, :, [2, 1, 0]]
        height, width, channel = im.shape
        bytes_per_line = 3 * width
        im_bytes = im.tobytes()
        modified = QImage(im_bytes, width, height, bytes_per_line, QImage.Format_RGB888)
        self.mod_picture.setPixmap(QPixmap(modified).scaledToHeight(self.pic_height))

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
