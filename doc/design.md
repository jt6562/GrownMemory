# 架构设计

## 整体架构

```{viz}
engine:dot
digraph overview {
    K = 0.6;
    size = "8,5";
    center = true;
    node [shape=record];
    edge [minlen=2];

    // define
    subgraph cluster_watchers{
        label = "Watchers";
        DirectoryWatcher [label="{DirectoryWatcher|<port> zmq}"];
        WechatWatcher [label="{WechatWatcher|<port> zmq}"];
    }

    Importer [label="{<inport> zmq 5556|<parser> Importer|<outport> zmq 5557}"];

    subgraph cluster_exporters{
        label = "Exporters";
        DirectoryExporter [label="{<inport> zmq|DirExporter}"];
        QNAPExporter [label="{<inport> zmq|QNAPExporter}"];
    }

    # Watcher -> Importer
    {DirectoryWatcher:port, WechatWatcher:port} -> Importer:inport [label="pic info" headlabel="pull", taillabel=push];

    # Picture process
    {rank=same;Importer,MySQL,"Web Server"}
    Importer -> MySQL [dir="both", label="update pic info"]
    MySQL -> "Web Server"

    # Importer -> Exporter
    Importer:outport -> {DirectoryExporter:inport,  QNAPExporter:inport} [label="pic content", taillabel="pub",headlabel=sub]

}
```

## 模块功能说明

### 启动器 Starter

加载配置文件，并按照配置启动各个模块实例。每个模块都可能有多个实例：

1. 对于Watcher来说，每个实例的配置不能完全相同，否则可能会导致重复导入的情况发生。
2. 对于Importer，设计为父子进程模型，父进程接收时间通知，子进程进行处理。

### 监听器 Watcher

监听数据源的变化，实时获取最新图片。包括：

1. directory_watcher，负责监听某个目录及其子目录的文件变化。每个实例负责一个目录及其子目录。注意：**多个实例监听的目录和子目录不能有交集**，也就是是说，一个实例监听的目录不能是另一个实例监听目录的子目录。
2. wechat_watcher，负责监听一个或多个微信联系人(群)的目录变化。鉴于微信网页版一个账号只能在一个地方登陆，所以只能有一个实例，但监听目标可以有多个。

### 导入器 Importer

监听内部 import 时间，分析导入的图片，获取图片信息，并保存到数据库中。将结果pub到exporter中。Importer支持多实例并行。

### 导出器 Exporter

保存图片文件，包括：

1. 保存图片到本地目录
2. 保存图片到QNAP，使用QNAP接口

## 启动器 Starter

使用supervisor管理多个实例进程。

# 协议说明
## Watcher -> Importer
{
    "source": "[directory|wechat|web]",
    "type": "file",
    "name": "file name",
    "content": "file content"
}

## Import -> Exporter
{
    "name": "sha1 of file content",
    "content": "file content"
}
