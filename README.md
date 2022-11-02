# gpu_monitor
refer to https://github.com/zhangwenxiao/GPU-Manager

clients: gpu5-14
server: your own pc or one gpu

在每个gpu上运行`client.py`，指定server IP 为本机IP或者某个服务器IP，在本机/某个服务器 运行`server.py`，
因为本机IP为动态分配，可能每次都需要更改server IP，server指定为服务器IP比较方便，但多人使用时有可能发生地址冲突。