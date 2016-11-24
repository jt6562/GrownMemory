# Photo Collector

这是一个图片收集器，从多种数据源获取图片，去重后保存。

家里很多人为宝宝拍照片，这些照片分散的保存在各人的手机中。也有可能通过微信等工具互相交换图片。这些照片如果都放在一起的话，一定会有大量的重复照片。

这个项目就是为了解决照片的获取，解析，去重，保存而建立的。

# Features
[特性列表](doc/features.md)

# Design
[项目设计文档](doc/design.md)

# TODO

- [x] 实现通信框架
- [ ] 实现启动器
- [x] 实现Importer

  - [ ] 实现图片基本数据解析
  - [ ] 实现图片特征值计算
  - [ ] 实现图片去重

- [x] 实现Watchers

  - [x] 实现DirectoryWatcher
  - [x] 实现WechatWatcher

- [ ] 实现Exporter

  - [ ] 实现DirectoryExporter
  - [ ] 实现QNAPExporter

- [ ] 实现Web
