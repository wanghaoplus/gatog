# -*- coding:utf-8 -*-
__version__ = '2019-07-13'
__author__ = 'shaochanghong'
__summary__ = 'adb模块'

import os
import subprocess
import socket
import whichcraft
from collections import namedtuple
from components.device.android.adb.errors import AdbError

_OKAY = "OKAY"
_FAIL = "FAIL"
_DENT = "DENT"  # Directory Entity
_DONE = "DONE"
ForwardItem = namedtuple("ForwardItem", ["serial", "local", "remote"])


def where_adb():
    adb_path = whichcraft.which('adb')
    if adb_path is None:
        raise EnvironmentError("Can't find adb,please install adb first.")
    return adb_path


class _AdbStreamConnect(object):

    """
    连接adb服务
    即通过adb start-server在PC侧ANDROID_ADB_SERVER_PORT端口起的服务
    具体可以发送哪些命令需要查看adb.exe源码
    """

    def __init__(self, host=None, port=None):
        self.__host = host
        self.__port = port
        self.__conn = None

        self._connect()

    def _create_socket(self):
        adb_host = self.__host or os.environ.get('ANDROID_ADB_SERVER_HOST', '127.0.0.1')
        adb_port = self.__port or int(os.environ.get('ANDROID_ADB_SERVER_PORT', 7305))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect((adb_host, adb_port))
            return s
        except:
            s.close()
            raise

    @property
    def conn(self):
        return self.__conn

    def _connect(self):
        try:
            self.__conn = self._create_socket()
        except Exception as e:
            subprocess.run('adb kill-server')
            subprocess.run('adb start-server')
            self.__conn = self._create_socket()

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def send(self, cmd: str):
        # cmd: str表示期望cmd是字符串类型
        if not isinstance(cmd, str):
            cmd = str(cmd)
        self.conn.send("{:04x}{}".format(len(cmd), cmd).encode("utf-8"))

    def read(self, n) -> str:
        # -> str表示接口返回值为字符串
        return self.conn.recv(n).decode()

    def read_string(self) -> str:
        size = int(self.read(4), 16)
        return self.read(size)

    def read_until_close(self) -> str:
        content = ""
        while True:
            chunk = self.read(4096)
            if not chunk:
                break
            content += chunk
        return content

    def check_okay(self):
        # 前四位是状态码
        data = self.read(4)
        if data == _FAIL:
            raise AdbError(self.read_string())
        elif data == _OKAY:
            return
        raise AdbError("Unknown data: %s" % data)


class AdbClient(object):

    def __init__(self, host=None, port=None):
        self.__host = host
        self.__port = port

    def server_version(self):
        """
        @summary:获取adb版本号
        @return :版本号1.0.41中的41
        """
        with self._connect() as c:
            c.send("host:version")
            c.check_okay()
            return int(c.read_string(), 16)

    def _connect(self):
        return _AdbStreamConnect(self.__host, self.__port)

    def forward(self, serial, local, remote, norebind=False):
        """
        @summary:给adb服务端发送host-serial:<sn>:forward:tcp:<pc_port>;tcp:<phone_port>进行端口转发
        @param serial:手机sn号,sn为None时按默认连接一部手机处理
        @param local:PC侧socket客户端端口
        @param remote:手机侧socket服务端端口
        @param norebind:fail if already forwarded when set to true
        @attention :PC跟手机通过USB方式通信
        """
        with self._connect() as c:
            cmds = ["host", "forward"]
            if serial:
                cmds = ["host-serial", serial, "forward"]
            if norebind:
                cmds.append("norebind")
            cmds.append("tcp:%s;tcp:%s" % (local, remote))
            print(cmds)
            c.send(":".join(cmds))
            c.check_okay()

    def forward_list(self, serial=None):
        """
        @summary:查看端口转发是否成功
        @param serial:手机sn号
        @attention :PC跟手机通过USB方式通信
        """
        with self._connect() as c:
            list_cmd = "host:list-forward"
            if serial:
                list_cmd = "host-serial:{}:list-forward".format(serial)
            c.send(list_cmd)
            c.check_okay()
            content = c.read_string()
            for line in content.splitlines():
                parts = line.split()
                if len(parts) != 3:
                    continue
                if serial and parts[0] != serial:
                    continue
                yield ForwardItem(*parts)

    def shell(self, serial, command) -> str:
        """
        @summary:执行shell命令
        @param serial:手机sn号
        @param command:要执行的命令
        @attention :只能执行adb shell命令
        """
        with self._connect() as c:
            c.send("host:transport:" + serial)
            c.check_okay()
            c.send("shell:" + command)
            c.check_okay()
            return c.read_until_close()

    def device_list(self):
        """
        @summary:获取手机列表
        @attention :
        """
        device_list = []
        with self._connect() as c:
            c.send("host:devices")
            c.check_okay()
            output = c.read_string()
            for line in output.splitlines():
                parts = line.strip().split("\t")
                if len(parts) != 2:
                    continue
                if parts[1] == 'device':
                    device_list.append(parts[0])
        return device_list

    def must_one_device(self, serial):
        device_list = self.device_list()
        if len(device_list) == 0:
            raise RuntimeError(
                "Can't find any android device/emulator"
            )
        elif serial is None and len(device_list) > 1:
            raise RuntimeError(
                "more than one device/emulator, please specify the serial number"
            )


if __name__ == '__main__':
    client = AdbClient()
    devices = client.adb('XPU4C16C09001373','root')
    # print(devices)
    # for i in client.forward_list():
    #     print(i)
