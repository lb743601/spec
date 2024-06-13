import sys
import time
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from ui import Ui_MainWindow
from serial_class import SerialClass
from plot_widget import PlotWidget
from scipy.signal import savgol_filter
import numpy as np
import datetime
def sf(data):
    outdata = savgol_filter(data, window_length=21, polyorder=10)
    return outdata
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        self.mode=1
        super().__init__()
        self.setupUi(self)
        self.ser = SerialClass()
        self.ser.set_port_parameters(baudrate=115200)
        self.pushButton.clicked.connect(self.scan_serial)
        self.pushButton_4.clicked.connect(self.open_port)
        self.pushButton_2.clicked.connect(self.spec_scan)
        # self.pushButton_5.clicked.connect(self.smooth_data)
        self.ser.data_received.connect(self.update_text_browser)
        self.ser.scan_complete.connect(self.scan_complete)
        self.pushButton_6.clicked.connect(self.dark_scan)
        self.pushButton_7.clicked.connect(self.back_scan)
        self.pushButton_8.clicked.connect(self.dis_dark)
        self.pushButton_9.clicked.connect(self.dis_back)
        self.pushButton_10.clicked.connect(self.dis_spec)
        self.pushButton_5.clicked.connect(self.caculate)
        self.pushButton_3.clicked.connect(self.save_data)
        # 创建并添加 PlotWidget 到界面中
        self.plot_widget = PlotWidget(self.centralwidget)
        self.plot_widget.setGeometry(self.graphicsView.geometry())
        self.plot_widget.setParent(self.centralwidget)
        self.graphicsView.setVisible(False)  # 隐藏原始的 QGraphicsView 占位符
        self.spec_data=None
        self.dark_data=None
        self.back_data=None
        self.spec_data_smooth = None
        self.dark_data_smooth = None
        self.back_data_smooth = None
    def scan_serial(self):
        self.ser.scan_ports()
        self.comboBox.clear()
        for i, port in enumerate(self.ser.ports):
            self.comboBox.addItem(f"{i}: {port.device}")

    def open_port(self):
        if self.pushButton_4.text() == "打开":
            if self.comboBox.count() > 0:
                current_data = self.comboBox.currentText()
                if self.ser.open_port(int(current_data.split(":")[0])):
                    self.textBrowser.append("已打开串口")
                    self.pushButton_4.setText("关闭")
                else:
                    self.textBrowser.append("打开串口失败")
            else:
                self.textBrowser.append("未选中串口")
        else:
            if self.ser.close_port():
                self.textBrowser.append("已关闭串口")
                self.pushButton_4.setText("打开")

    def spec_scan(self):
        if self.pushButton_4.text() == "关闭":
            text = self.textEdit.toPlainText()
            if text and text.isdigit():
                if self.pushButton_2.text()=="开始" and self.pushButton_6.text()!="扫描中" and self.pushButton_7.text()!="扫描中":
                    self.textBrowser.append("开始扫描")
                    self.pushButton_2.setText("扫描中")
                    self.mode=1
                    text = int(text)

                    self.ser.spec_scan(text)
            else:
                self.textBrowser.append("非法输入")
        else:
            self.textBrowser.append("未打开串口")

    def update_text_browser(self, data):
        self.textBrowser.append(f"接收到的数据: {data}")

    def scan_complete(self):
        if self.mode==1:
            QMessageBox.information(self, "信息", "扫描完成")
            if self.pushButton_2.text()=="扫描中":
                self.spec_data=self.ser.spec_data
                self.spec_data_smooth=sf(self.spec_data)
                self.pushButton_2.setText("开始")
            if self.pushButton_6.text()=="扫描中":
                self.dark_data[2]=self.ser.spec_data
                self.pushButton_6.setText("暗电流")
                for i in range(3):
                    self.dark_data_smooth[i]=sf(self.dark_data[i])
            if self.pushButton_7.text()=="扫描中":
                self.back_data[2]=self.ser.spec_data
                for i in range(3):
                    self.back_data_smooth[i]=sf(self.back_data[i])
                self.pushButton_7.setText("背景光谱")
            # 绘制曲线
            # self.plot_widget.update_plot(self.ser.spec_data)
        else:
            if self.pushButton_6.text()=="扫描中":
                self.dark_data[3-self.mode]=self.ser.spec_data
            if self.pushButton_7.text()=="扫描中":
                self.back_data[3-self.mode]=self.ser.spec_data
            self.mode-=1
            time.sleep(1)
            text = self.textEdit.toPlainText()
            text = int(text)
            self.ser.spec_scan(text)

    def back_scan(self):
        if self.pushButton_4.text() == "关闭":
            text = self.textEdit.toPlainText()
            if text and text.isdigit():
                if self.pushButton_7.text()=="背景光谱" and self.pushButton_6.text()!="扫描中" and self.pushButton_2.text()!="扫描中":
                    self.textBrowser.append("开始扫描")
                    self.pushButton_7.setText("扫描中")
                    self.mode=3
                    text = int(text)
                    num = (301 // text) + 1
                    if text==1:
                        num=301
                    self.back_data = np.zeros((3,num))
                    self.back_data_smooth = np.zeros((3, num))
                    self.ser.spec_scan(text)
            else:
                self.textBrowser.append("非法输入")
        else:
            self.textBrowser.append("未打开串口")
    def dark_scan(self):
        if self.pushButton_4.text() == "关闭":
            text = self.textEdit.toPlainText()
            if text and text.isdigit():
                if self.pushButton_6.text()=="暗电流"and self.pushButton_2.text()!="扫描中"and self.pushButton_7.text()!="扫描中":
                    self.textBrowser.append("开始扫描")
                    self.pushButton_6.setText("扫描中")
                    self.mode=3
                    text = int(text)
                    num = (301 // text) + 1
                    if text==1:
                        num=301
                    self.dark_data = np.zeros((3,num))
                    self.dark_data_smooth = np.zeros((3, num))
                    self.ser.spec_scan(text)
            else:
                self.textBrowser.append("非法输入")
        else:
            self.textBrowser.append("未打开串口")
    def dis_dark(self):
        if self.dark_data is not None:
            if self.pushButton_8.text()=="暗电流曲线":
                output=(self.dark_data[0]+self.dark_data[1]+self.dark_data[2])/3
                self.plot_widget.update_plot(output,int(self.textEdit.toPlainText()))
                self.pushButton_8.setText("平滑化暗电流")
            else:
                output = (self.dark_data_smooth[0] + self.dark_data_smooth[1] + self.dark_data_smooth[2]) / 3
                self.plot_widget.update_plot(output,int(self.textEdit.toPlainText()))
                self.pushButton_8.setText("暗电流曲线")
        else:
            self.textBrowser.append("未采集暗电流曲线")
    def dis_back(self):
        if self.back_data is not None:
            if self.pushButton_9.text()=="背景曲线":
                output=(self.back_data[0]+self.back_data[1]+self.back_data[2])/3
                self.plot_widget.update_plot(output,int(self.textEdit.toPlainText()))
                self.pushButton_9.setText("平滑化背景")
            else:
                output = (self.back_data_smooth[0] + self.back_data_smooth[1] + self.back_data_smooth[2]) / 3
                self.plot_widget.update_plot(output,int(self.textEdit.toPlainText()))
                self.pushButton_9.setText("背景曲线")
        else:
            self.textBrowser.append("未采集背景曲线")
    def dis_spec(self):
        if self.spec_data is not None:
            if self.pushButton_10.text()=="光谱曲线":
                self.plot_widget.update_plot(self.spec_data,int(self.textEdit.toPlainText()))
                self.pushButton_10.setText("平滑化光谱")
            else:
                self.plot_widget.update_plot(self.spec_data_smooth,int(self.textEdit.toPlainText()))
                self.pushButton_10.setText("光谱曲线")
        else:
            self.textBrowser.append("未采集光谱曲线")
    def save_data(self):
        if self.back_data is not None and self.dark_data is not None and self.spec_data is not None:
            time_str="./data/"+"interval_"+self.textEdit.toPlainText()+"_"+datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')
            back_data_str=time_str+"_back"
            back_data_smooth_str=time_str+"_back_smooth"
            dark_data_str = time_str + "_dark"
            dark_data_smooth_str = time_str + "_dark_smooth"
            spec_data_str=time_str+"_spec"
            spec_data_smooth_str=time_str+"_spec_smooth"
            np.save(back_data_str,self.back_data)
            np.save(back_data_smooth_str,self.back_data_smooth)
            np.save(dark_data_str, self.dark_data)
            np.save(dark_data_smooth_str, self.dark_data_smooth)
            np.save(spec_data_str, self.spec_data)
            np.save(spec_data_smooth_str, self.spec_data_smooth)
            self.textBrowser.append("保存成功")
        else:
            self.textBrowser.append("数据未采集完全")
    def caculate(self):
        if self.spec_data is not None and self.dark_data is not None and self.back_data is not None and self.spec_data.shape==self.back_data[0].shape and self.spec_data.shape==self.dark_data[0].shape:

            back = (self.back_data_smooth[0] + self.back_data_smooth[1] + self.back_data_smooth[2]) / 3
            dark=  (self.dark_data_smooth[0] + self.dark_data_smooth[1] + self.dark_data_smooth[2]) / 3
            out=(self.spec_data_smooth-dark)/(back-dark)
            out = sf(out)
            out=-np.log10(out)
            self.plot_widget.update_plot(out,int(self.textEdit.toPlainText()))

        else:
            self.textBrowser.append("数据未采集完全")
    def smooth_data(self):
        pass
        # if self.ser.spec_data is not None:
        #     smooth_data = savgol_filter(self.ser.spec_data, window_length=51, polyorder=3)
        #     self.plot_widget.update_plot(smooth_data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
