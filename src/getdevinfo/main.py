import subprocess
import re
import platform
import uuid
import os


def get_mac_address():
    mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    return mac


def get_all_mac_addresses():
    try:
        # 获取所有网络接口的信息
        result = subprocess.check_output("ip link show", shell=True).decode()

        # 使用正则表达式提取所有 MAC 地址
        mac_addresses = re.findall(r'link/ether ([\da-fA-F:]{17})', result)
        if len(mac_addresses) == 1:
            return mac_addresses[0]

        if len(mac_addresses) > 1:
            formatted_items = [f"{index + 1}, {v}" for index, v in enumerate(mac_addresses)]

            # 将格式化的字符串列表连接成一个多行字符串
            result = "\n".join(formatted_items)
            input_index_str = input('检测到有个多 Mac 地址：\n{0}\n请输入对应的序号后摁回车键\n'.format(result))
            while True:

                if input_index_str.isdigit() and int(input_index_str) in range(1, len(mac_addresses) + 1):
                    return mac_addresses[int(input_index_str) - 1]
                else:
                    input_index_str = input('输入无效，请重新输入：\n')
                    continue
        return None
    except subprocess.CalledProcessError as e:
        return [f"Error occurred: {e}"]


def get_linux_info():
    info = {}

    # 品牌和制造商
    try:
        with open("/sys/class/dmi/id/sys_vendor", "r") as f:
            info["品牌"] = f.read().strip()
    except Exception as e:
        info["品牌"] = str(e)

    # 型号
    try:
        with open("/sys/class/dmi/id/product_name", "r") as f:
            info["型号"] = f.read().strip()
    except Exception as e:
        info["型号"] = str(e)

    # 系列
    try:
        with open("/sys/class/dmi/id/product_version", "r") as f:
            info["系列"] = f.read().strip()
    except Exception as e:
        info["系列"] = str(e)

    # 硬盘容量
    try:
        disk_info = subprocess.check_output("lsblk -dn -o SIZE", shell=True)
        num_str = disk_info.decode().strip()
        number_str = num_str.replace('G', '').strip()

        # 将提取的字符串转换为浮点数
        number = float(number_str)

        # 四舍五入到最近的整数
        rounded_number = round(number)
        info["硬盘容量"] = rounded_number
    except Exception as e:
        info["硬盘容量"] = str(e)

    # 内存
    try:
        mem_info = subprocess.check_output("grep MemTotal /proc/meminfo", shell=True)
        mem_total = int(re.findall(r'\d+', mem_info.decode())[0]) // 1024 // 1024
        info["内存"] = f"{mem_total}"
    except Exception as e:
        info["内存"] = str(e)

    # CPU主频和核数
    try:
        cpu_info_hz = subprocess.check_output("lscpu | grep 'CPU MHz'", shell=True)
        print(cpu_info_hz)
        hz = cpu_info_hz.decode().split(":")[1].strip()
        # MHz 转 GHz
        info["cpu主频"] = round(float(hz) / 1024, 1)

        cpu_info_core = subprocess.check_output("lscpu | grep '^CPU(s)'", shell=True)
        print(cpu_info_core)
        info["cpu核数"] = cpu_info_core.decode().split(":")[1].strip()

        cpu_info_name = subprocess.check_output("lscpu | grep 'Model name'", shell=True)
        print(cpu_info_name)
        info["cpu型号"] = cpu_info_name.decode().split(":")[1].strip()
    except Exception as e:
        info["cpu"] = str(e)

    # 显卡型号
    try:
        gpu_info = subprocess.check_output("lspci | grep VGA", shell=True)
        info["显卡型号"] = gpu_info.decode().split(":")[2].strip()
    except Exception as e:
        info["显卡型号"] = str(e)

    # 设备生产日期
    try:
        with open("/sys/class/dmi/id/bios_date", "r") as f:
            info["出厂日期"] = f.read().strip()
    except Exception as e:
        info["出厂日期"] = "Unknown"

    # 出厂序列号
    try:
        with open("/sys/class/dmi/id/product_serial", "r") as f:
            serial_number = f.read().strip()
            info["出厂序列号"] = serial_number if serial_number else "Not Available"
    except Exception as e:
        info["出厂序列号"] = "Not Available"

    # 操作系统
    info["操作系统"] = platform.system() + " " + platform.release()

    return info


def format_mac_address(mac):
    # 去掉 MAC 地址中的冒号或短横线
    mac = mac.replace(':', '').replace('-', '')

    # 将字母转换为大写
    mac = mac.upper()

    # 格式化为 xxxx-xxxx-xxxx
    formatted_mac = '-'.join([mac[i:i + 4] for i in range(0, len(mac), 4)])

    return formatted_mac


# 获取MAC地址
mac_address = get_all_mac_addresses()

# 获取系统硬件信息
system_info = {"MAC地址": format_mac_address(mac_address)}
system_info.update(get_linux_info())
system_info['制造商'] = system_info.get('品牌')


def write_data_to_file(d, filename='output.dat'):
    # 获取当前工作目录
    current_dir = os.getcwd()

    # 生成文件路径
    f_path = os.path.join(current_dir, filename)

    # 写入数据到文件
    with open(f_path, 'w') as file:
        file.write(d)

    # 返回文件路径
    return f_path


data = '\n'.join([f"{k}={v}" for k, v in system_info.items()])
file_path = write_data_to_file(data)
print('系统信息已获取，内容保存于:{0}'.format(file_path))
