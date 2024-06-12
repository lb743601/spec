# import time
# import numpy as np
# import serial
# import serial.tools.list_ports
# import threading
# class serial_class:
#     def __init__(self):
#         self.spec_data=None
#         self.num=0
#         self.ser=None
#         self.receive_thread = None
#         self.stop_event = threading.Event()
#         self.stop_event.set()
#         self.ports=None
#         self.port_parameters = {
#             "baudrate": 115200,
#             "bytesize": serial.EIGHTBITS,
#             "parity": serial.PARITY_NONE,
#             "stopbits": serial.STOPBITS_ONE,
#             "timeout": 1
#         }
#
#     def scan_ports(self):
#         self.ports = list(serial.tools.list_ports.comports())
#         # for i, port in enumerate(self.ports):
#         #     print(f"{i}: {port.device}")
#
#     def set_port_parameters(self, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1):
#         """设置串口参数"""
#         if baudrate:
#             self.port_parameters["baudrate"] = baudrate
#         if bytesize:
#             self.port_parameters["bytesize"] = bytesize
#         if parity:
#             self.port_parameters["parity"] = parity
#         if stopbits:
#             self.port_parameters["stopbits"] = stopbits
#         if timeout:
#             self.port_parameters["timeout"] = timeout
#         print("串口参数已设置为:", self.port_parameters)
#     def open_port(self,port_number=0):
#         port = self.ports[port_number].device
#         self.ser = serial.Serial(
#             port,
#             baudrate=self.port_parameters["baudrate"],
#             bytesize=self.port_parameters["bytesize"],
#             parity=self.port_parameters["parity"],
#             stopbits=self.port_parameters["stopbits"],
#             timeout=self.port_parameters["timeout"]
#         )
#         if self.ser.is_open:
#             print(f"串口 {port} 已打开")
#             return 1
#         return 0
#
#     def send_data(self, data):
#         """发送数据到串口"""
#         if self.ser:
#             data=data+"\r\n"
#             self.ser.write(data.encode('utf-8'))
#             print(f"发送数据: {data}")
#         else:
#             print("未打开串口")
#
#     def receive_data(self,target_num):
#         """从串口接收数据并打印"""
#         while self.num<target_num:
#             if self.ser:
#                 data = self.ser.readline().decode('gbk').rstrip()
#                 if data:
#                     print(f"接收到的数据: {data}")
#                     if len(data)>1 and data[1]=='.':
#                         self.spec_data[self.num]=float(data)
#                         self.num+=1
#         self.stop_event.set()
#         print("扫描完成\n")
#     def spec_scan(self,target_num):
#         print(1)
#         if self.receive_thread is None or not self.receive_thread.is_alive():
#             self.spec_data=np.zeros(target_num)
#             self.num=0
#             self.stop_event.clear()
#             self.receive_thread = threading.Thread(target=self.receive_data,args=(target_num,))
#             self.receive_thread.start()
#             print("开始接收\n")
#             time.sleep(1)
#             self.send_data("spe_scan(1)")
#         else:
#             print("扫描程序正在运行\n")
#     def start_receiving(self):
#         """启动接收数据的线程"""
#         self.stop_event.clear()
#         self.receive_thread = threading.Thread(target=self.receive_data)
#         self.receive_thread.start()
#         print("开始接收\n")
#
#     def stop_receiving(self):
#         """停止接收数据的线程"""
#         if self.receive_thread:
#             self.stop_event.set()
#             self.receive_thread.join()
#             print("停止接收\n")
#     def close_port(self):
#         """关闭串口"""
#         if self.ser:
#             self.ser.close()
#             if not self.ser.is_open:
#                 print("串口已关闭")
#             self.ser=None
#             return 1
#         else:
#             print("未打开串口")
#             return 0
import time
import numpy as np
import serial
import serial.tools.list_ports
import threading
from PyQt5.QtCore import pyqtSignal, QObject

class SerialClass(QObject):
    data_received = pyqtSignal(float)
    scan_complete = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.spec_data = None
        self.num = 0
        self.ser = None
        self.receive_thread = None
        self.stop_event = threading.Event()
        self.stop_event.set()
        self.ports = None
        self.port_parameters = {
            "baudrate": 115200,
            "bytesize": serial.EIGHTBITS,
            "parity": serial.PARITY_NONE,
            "stopbits": serial.STOPBITS_ONE,
            "timeout": 1
        }

    def scan_ports(self):
        self.ports = list(serial.tools.list_ports.comports())

    def set_port_parameters(self, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1):
        if baudrate:
            self.port_parameters["baudrate"] = baudrate
        if bytesize:
            self.port_parameters["bytesize"] = bytesize
        if parity:
            self.port_parameters["parity"] = parity
        if stopbits:
            self.port_parameters["stopbits"] = stopbits
        if timeout:
            self.port_parameters["timeout"] = timeout
        print("串口参数已设置为:", self.port_parameters)

    def open_port(self, port_number=0):
        port = self.ports[port_number].device
        self.ser = serial.Serial(
            port,
            baudrate=self.port_parameters["baudrate"],
            bytesize=self.port_parameters["bytesize"],
            parity=self.port_parameters["parity"],
            stopbits=self.port_parameters["stopbits"],
            timeout=self.port_parameters["timeout"]
        )
        if self.ser.is_open:
            print(f"串口 {port} 已打开")
            return 1
        return 0

    def send_data(self, data):
        if self.ser:
            data = data + "\r\n"
            self.ser.write(data.encode('utf-8'))
            print(f"发送数据: {data}")
        else:
            print("未打开串口")

    def receive_data(self, target_num):
        while not self.stop_event.is_set() and self.num < target_num:
            if self.ser:
                data = self.ser.readline().decode('gbk').rstrip()
                if data:
                    print(f"接收到的数据: {data}")
                    if len(data) > 1 and data[1] == '.':
                        self.spec_data[self.num] = float(data)
                        self.num += 1
                        self.data_received.emit(float(data))
        self.scan_complete.emit()
        print("扫描完成\n")

    def spec_scan(self, target_num):
        if self.receive_thread is None or not self.receive_thread.is_alive():
            if(target_num==1):
                self.spec_data = np.zeros(301)
                x=301
            else:
                self.spec_data=np.zeros((301 // target_num) + 1)
                x=(301 // target_num) + 1
            self.num = 0
            self.stop_event.clear()
            self.receive_thread = threading.Thread(target=self.receive_data, args=(x,))
            self.receive_thread.start()
            print("开始接收\n")
            time.sleep(1)
            sdata="spe_scan("+str(target_num)+")"
            self.send_data(sdata)
        else:
            print("扫描程序正在运行\n")

    def close_port(self):
        if self.ser:
            self.stop_event.set()
            self.receive_thread.join()
            self.ser.close()
            if not self.ser.is_open:
                print("串口已关闭")
            self.ser = None
            return 1
        else:
            print("未打开串口")
            return 0
