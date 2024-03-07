from machine import Pin, Timer, UART
import time

# 初始化LED灯和定时器
led = Pin("LED", Pin.OUT)

# 初始化输入输出串口
#uart1 = UART(1, baudrate=9600, tx=33, rx=32)  # 输入串口
#uart2 = UART(2, baudrate=9600, tx=17, rx=16)  # 输出串口
uart1 = UART(1, baudrate=115200, tx=Pin(8), rx=Pin(9))
uart2 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
from machine import Timer, UART

# 使用字节列表作为队列来存储待发送的字节
queue = []

# 用于暂存接收到的可能是UTF-8多字节字符的字节
temp_bytes = bytearray()

def process_received_data(data):
    """
    处理接收到的数据，如果是ASCII则直接放入队列，否则判断是否UTF-8，确认完整后放入队列并打印。
    """
    global temp_bytes

    for byte in data:
        if 0x00 <= byte <= 0x7F:
            # 字节是ASCII字符，直接添加到队列
            queue.append(byte)
        else:
            # 字节可能是UTF-8的一部分，暂存以待进一步处理
            temp_bytes.append(byte)
            try:
                # 尝试解码为UTF-8，如果成功，说明是完整的字符
                temp_str = temp_bytes.decode('utf-8')
                # 解码成功，说明temp_bytes中存储的是完整的UTF-8字符
                # 将temp_bytes中的字节逐个放入队列
                #queue.extend(temp_bytes)
                print(temp_str,end='')  # 打印解码成功的字符串
                temp_bytes = bytearray()  # 清空暂存区
            except Exception as e:
                # 解码失败，说明不是完整的UTF-8字符，继续接收
                pass

# 定义定时器中断回调函数，用于发送数据
def send_data(timer):
    if queue:
        # 从队列中取出一个字节并发送
        byte_to_send = queue.pop(0)
        # 检查是否为\n（0x0A），如果是，则替换为\r（0x0D）
        if byte_to_send == 0x0A:
            byte_to_send = 0x0D
            led.toggle()
        uart2.write(bytearray([byte_to_send]))

# 设置定时器，定期调用send_data函数发送数据
tim = Timer()
tim.init(freq=100, mode=Timer.PERIODIC, callback=send_data)  # 设置发送频率

# 主循环
while True:
    # 读取输入串口的数据
    if uart1.any():
        data = uart1.read()
        process_received_data(data)