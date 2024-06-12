from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
import pyqtgraph as pg

class PlotWidget(QGraphicsView):
    def __init__(self, parent=None):
        super(PlotWidget, self).__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.plot_widget = pg.PlotWidget()
        self.scene.addWidget(self.plot_widget)
        self.plot_data_item = self.plot_widget.plot()

        # 设置背景为白色，线条和文字为黑色
        self.plot_widget.setBackground('w')
        self.plot_widget.getAxis('left').setPen(pg.mkPen(color='k'))
        self.plot_widget.getAxis('bottom').setPen(pg.mkPen(color='k'))
        self.plot_data_item.setPen(pg.mkPen(color='k'))

        # 设置坐标轴标签
        self.plot_widget.setLabel('left', 'Intensity')
        self.plot_widget.setLabel('bottom', 'Wavelength', units='nm')

    # def update_plot(self, data):
    #     x = range(1550, 1550 + len(data))  # 生成从 1550 开始的横坐标
    #     self.plot_data_item.setData(x, data)
    #     self.plot_widget.setXRange(1550, 1850)  # 设置横坐标范围
    #     self.plot_widget.getAxis('bottom').setTicks([[(i, str(i)) for i in range(1550, 1851, 50)]])  # 设置横坐标刻度

    # def update_plot(self, data, interval):
    #     x = [1550 + i * interval for i in range(len(data))]  # 根据间隔生成横坐标
    #     self.plot_data_item.setData(x, data)
    #     self.plot_widget.setXRange(1550, 1550 + interval * (len(data) - 1))  # 设置横坐标范围
    #     ticks = [(1550 + i * interval, str(1550 + i * interval)) for i in
    #              range((1850 - 1550) // interval + 1)]  # 设置横坐标刻度
    #     self.plot_widget.getAxis('bottom').setTicks([ticks])

    def update_plot(self, data, interval):
        x = [1550 + i * interval for i in range(len(data))]  # 根据间隔生成横坐标
        self.plot_data_item.setData(x, data)
        self.plot_widget.setXRange(1550, 1550 + interval * (len(data) - 1))  # 设置横坐标范围
        # 设置横坐标刻度，只显示每隔50个单位的刻度
        ticks = [(i, str(i)) for i in range(1550, 1550 + interval * (len(data) - 1) + 1) if (i - 1550) % 50 == 0]
        self.plot_widget.getAxis('bottom').setTicks([ticks])
