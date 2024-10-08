import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QMessageBox, QLabel, QDesktopWidget, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_RIGHT
import subprocess

# 한글 폰트 등록
pdfmetrics.registerFont(TTFont('NanumGothic', 'NanumGothic.ttf'))
pdfmetrics.registerFont(TTFont('NanumGothicBold', 'NanumGothicBold.ttf'))

def create_labels(output_filename, data):
    page_width, page_height = A4
    label_width, label_height = 99.1 * mm, 38.1 * mm
    margin_top = margin_bottom = 15.5 * mm
    margin_left = margin_right = 5 * mm
    gap_horizontal, gap_vertical = 2.5 * mm, 0 * mm
    labels_per_row, labels_per_column = 2, 7

    c = canvas.Canvas(output_filename, pagesize=A4)

    normal_style = ParagraphStyle('Normal', fontName='NanumGothic', fontSize=10)
    bold_style = ParagraphStyle('Bold', fontName='NanumGothicBold', fontSize=11)
    right_style = ParagraphStyle('Right', fontName='NanumGothicBold', fontSize=11, alignment=TA_RIGHT)

    for i, row in data.iterrows():
        page_num = i // (labels_per_row * labels_per_column)
        if page_num > 0 and i % (labels_per_row * labels_per_column) == 0:
            c.showPage()
        
        row_on_page = (i % (labels_per_row * labels_per_column)) // labels_per_row
        col = i % labels_per_row

        x = margin_left + col * (label_width + gap_horizontal)
        y = page_height - margin_top - (row_on_page + 1) * label_height

        # 라벨 외곽선 컬러 변경
        c.setStrokeColorRGB(177/255, 179/255, 177/255)  # #b1b3b1
        c.rect(x, y, label_width, label_height)

        text_x = x + 2 * mm
        text_y = y + label_height - 5 * mm

        p = Paragraph(f"{row['이름']}{row['직분']}님 귀하", bold_style)
        p.wrapOn(c, label_width - 4*mm, label_height)
        p.drawOn(c, text_x, text_y - 5*mm)

        p = Paragraph(row['교회'], normal_style)
        p.wrapOn(c, label_width - 4*mm, label_height)
        p.drawOn(c, text_x, text_y - 11*mm)

        p = Paragraph(row['주소'], normal_style)
        p.wrapOn(c, label_width - 4*mm, label_height)
        p.drawOn(c, text_x, text_y - 17*mm)

        p = Paragraph(f"(우) {row['우편번호']}", right_style)
        p.wrapOn(c, label_width - 4*mm, label_height)
        p.drawOn(c, text_x, text_y - 23*mm)

    c.save()


class LabelPrinterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('남경기노회 주소라벨 프로그램')
        self.setFixedSize(530, 500)

        layout = QVBoxLayout()

        # Title Section
        title_label = QLabel('남경기노회 주소라벨 프로그램', self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('NanumGothic', 15, QFont.Bold))
        title_label.setFixedHeight(30)
        layout.addWidget(title_label)

        # About Section
        about_label = QLabel('사용방법을 숙지해 주세요!', self)
        about_label.setAlignment(Qt.AlignCenter)
        about_label.setStyleSheet(
            "background-color: #f7dcad; border-radius: 10px; font-weight: bold;")
        about_label.setFixedHeight(35)
        layout.addWidget(about_label)

        about_content = QTextEdit(self)
        about_content.setHtml("""
        <h3>사용방법</h3>
        <ol>
            <li><strong>"라벨규격"</strong>: <strong>A4용지 14칸짜리</strong> 라벨입니다.<br>(라벨한장규격:가로:99.1mm, 세로: 38.1mm)</li>
            <li><strong>"라벨생성" 버튼</strong>을 먼저 클릭한 후 확인창을 종료하세요.</li>
            <li><strong>"인쇄하기" 버튼</strong>을 클릭하시면 PDF 인쇄 옵션 창이 실행된 후 
               반드시 <strong>단면인쇄</strong>를 선택하신 후 인쇄 실행하시면 됩니다.</li>
            <li>PDF 프로그램이 컴퓨터에 설치되어 있지 않다면 
               <strong>"알PDF v4.0"</strong>를 "https://altools.co.kr/product/ALPDF"에서 다운로드 후 
               설치하신 후 <strong>"라벨생성"</strong>과 <strong>"인쇄하기"</strong>를 실행하세요.</li>
        </ol>
        """)
        about_content.setReadOnly(True)
        about_content.setFixedHeight(290)
        layout.addWidget(about_content)

        # Button Section
        button_layout = QHBoxLayout()

        self.generate_btn = QPushButton('라벨 생성', self)
        self.generate_btn.clicked.connect(self.generate_labels)
        self.generate_btn.setStyleSheet(
            "background-color: #FFB3BA; font-weight: bold;")
        button_layout.addWidget(self.generate_btn)

        self.print_btn = QPushButton('인쇄하기', self)
        self.print_btn.clicked.connect(self.print_labels)
        self.print_btn.setStyleSheet(
            "background-color: #BAFFC9; font-weight: bold;")
        button_layout.addWidget(self.print_btn)

        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        button_widget.setFixedHeight(80)
        layout.addWidget(button_widget)

        # Quote Section
        quote_label = QLabel('made by 나종춘(2024)', self)
        quote_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        quote_label.setFixedHeight(20)
        layout.addWidget(quote_label)

        self.setLayout(layout)

        # 창을 화면 중앙에 위치
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def generate_labels(self):
        try:
            data = pd.read_excel('members.xlsx')
            create_labels("labels_output.pdf", data)
            QMessageBox.information(self, '성공', 'PDF 파일이 생성되었습니다.')
        except Exception as e:
            QMessageBox.critical(self, '오류', f'PDF 생성 중 오류 발생: {str(e)}')

    def print_labels(self):
        if not os.path.exists("labels_output.pdf"):
            QMessageBox.warning(self, '경고', 'PDF 파일이 없습니다. 먼저 라벨을 생성해주세요.')
            return

        try:
            if sys.platform.startswith('win'):
                os.startfile("labels_output.pdf", "print")
            elif sys.platform.startswith('darwin'):  # macOS
                subprocess.call(('open', "labels_output.pdf"))
            else:  # linux
                subprocess.call(('xdg-open', "labels_output.pdf"))
            QMessageBox.information(self, '성공', '인쇄 작업이 시작되었습니다.')
        except Exception as e:
            QMessageBox.critical(self, '오류', f'인쇄 중 오류 발생: {str(e)}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LabelPrinterApp()
    ex.show()
    sys.exit(app.exec_())
