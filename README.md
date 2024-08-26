# ygmr_log_collector

#### 介绍


#### 软件架构
  - 重写Logger对象的debug、info、warning、error、exception方法，在新方法内，除了原本的日志输出，还将信息入队并由消费者处理
  - 创建上述队列消费者线程，去发requests，上报信息

#### 安装说明
- 打包
    ```shell
    python setup.py sdist
    ```
- 安装
  ```shell
    pip install log_collector-*.*.*.tar.gz
    ```

#### 使用说明
```
from log_collector.initializer import start as start_log_collector
start_log_collector({Logger对象}, {webhook字符串}, {微服务名称字符串}, {运行日志级别(int)})
# `微服务名称字符串`参数，为可选。不赋值时，它将使用ygframe的Scope定义好的（项目没用ygframe时，它将是undefined）。
# `运行日志级别`参数的优先级低于项目自身的日志级别。例如项目INFO，本模块DEBUG，则本模块也只到INFO。
```
```
# 样例代码
"""
error、excepiton方法有三个参数：
    msg：日志内容（必选，字符串or异常对象）
    data：额外信息（可选，字典对象，默认None）
    do_print：是否输出日志（可选，boolean，默认True）

debug、info、warning方法有四个参数：
    前三个跟上述一样
    do_report：是否上报日志（可选，boolean，默认False）
"""

{Logger对象}.error("content...")
{Logger对象}.error("content...", data={'a': 123}, do_print=False)  # 将不会输出日志，仅上报，且kwargs={‘a’: 123}
{Logger对象}.exception(new Exception("occur error"))  # 第一个参数也可以是异常对象
{Logger对象}.warning("content...", do_report=True)  # 会输出日志，且上报
{Logger对象}.warning("content...", do_print=False, do_report=True)  # 不会输出日志，仅上报
```
#### 其他
  - webhook支持企业微信机器人或自有接口地址。当使用后者时，将发送如下数据
      ```shell
      POST {webhook}
      
      {
        "title": "Logger.Error",
        "content": "content...",
        "level": "error",
        "service": "ygai.webbackend | ygai-webbackend-b7ar2",
        "isp": "Hangzhou Alibaba Advertising Co | 120.77.159.31",
        "lineno": "/src/common/utils.py:resp_failure:138",
        "kwargs": {"a": 123},
        "ts": "2022-10-08 08:01:50+0000"
      }
      ```