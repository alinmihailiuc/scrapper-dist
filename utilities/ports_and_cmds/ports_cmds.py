import socket
import subprocess
import os
from time import sleep
from psutil import process_iter
from signal import SIGTERM


class Commands(object):

    def get_free_tcp_port(self):
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.bind(('', 0))
        tcp.listen(1)
        port = tcp.getsockname()[1]
        tcp.close()
        return port

    def send_shell_command(self, cmd):
        print("Sending shell command {}".format(cmd))
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sleep(5)

    def get_parent_dir(self, current_path, levels=1):
        current_new = current_path
        for i in range(levels + 1):
            current_new = os.path.abspath(os.path.join(current_new, os.pardir))

        return current_new

    def kill_process_on_port(self, desired_port):
        try:
            for proc in process_iter():
                for conns in proc.connections(kind='inet'):
                    if conns.laddr.port == desired_port:
                        print("Try to kill port : "+ desired_port)
                        proc.send_signal(SIGTERM)  # or SIGKILL
        except:
            print("Error in killing localserver on port : " + str(desired_port))

    def start_npm_plugin(self):
        free_tcp_port = self.get_free_tcp_port()
        path_npm_server = os.path.join(os.getcwd(), "plugin", "server.js")
        print("Starting node npm server located at: {}".format(path_npm_server))
        npm_cmd = ["node", str(path_npm_server), str(free_tcp_port)]
        self.send_shell_command(npm_cmd)

        return free_tcp_port