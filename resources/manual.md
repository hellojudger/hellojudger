# Hello Judger 第三代用户文档重制版 By xiezheyuan

## 目录 - Contents

[TOC]

## 前言

Hello Judger 是开源程序，遵循 GPL v3 协议。您可以自由地修改，分发本程序，但是修改后的程序必须开源，且必须遵从 GPL v3 协议。

**由于本程序操作十分简单（傻瓜式），因此本文档仅介绍一些高级操作。**

## Hello Judger 定制化

### 主题切换

有两种方法设置主题：

- 【设置(P)】->【界面主题配置(T)】进行选择，或者在界面下按下 `Ctrl+Shift+T` 快捷键。

- 修改程序目录的 `settings/ui_theme.json` 的 `theme` 字段

主题支持三种：

- `light` 浅色主题（推荐）
- `dark` 深色主题
- `auto` 根据系统设置，自动更换主题。

> 注意：`dark` 主题的 Markdown 预览是基于 CSS3 的颜色翻转，因此对图片或其他样式过多的文档可能显示质量不高。

### 评测配色

有两种方法设置评测配色：

- 【设置(P)】->【评测配色设置(J)】进行更改。
- 修改程序目录的 `settings/status.colorful.json`。键为状态去掉空格的字符串，值为 RGB 颜色数组。

需要特别说明的是：

- 再评测配色编辑器中颜色不能手动编辑，只能通过点击右侧的 `...` 后弹出的颜色选择对话框进行选择。
- Unaccepted 仅显示在【提交记录】中。

请注意默认的 TLE/Internal Error/Fail 配色在深色主题下可能不清楚。

### 中文状态

有两种方法设置中文状态：

- 【设置(P)】->【中文状态设置(Z)】进行更改。
- 修改程序目录的 `settings/status.chinese.json`。`enabled` 为是否启用，`content` 为翻译。具体请自己探索。

您可以选择是否启用中文状态，和修改英文状态对应的中文状态翻译。请注意提交记录的状态无论如何都显示成英文。

### 主页布局

主页布局使用 Splitter 技术，也就是说，你可以拖动 Markdown 预览与右侧标签页的交界处（如果拖动位置正确，会在拖动位置显示蓝色竖纹）来达到更改主页布局比例的效果。

### 编译配置

有两种方法设置编译配置：

- 【设置(P)】->【编译配置(C)】进行更改。
- 修改程序目录的 `settings/compile.json`。

默认编译配置：

```json
{
    "compiler": "g++",
    "arguments": [],
    "versions": [
        {
            "name": "C++ 98",
            "argument": "-std=c++98"
        },
        {
            "name": "C++ 11",
            "argument": "-std=c++11"
        },
        {
            "name": "C++ 14",
            "argument": "-std=c++14"
        },
        {
            "name": "C++ 17",
            "argument": "-std=c++17"
        },
        {
            "name": "C++ 20",
            "argument": "-std=c++20"
        }
    ],
    "optimizations": [
        {
            "name": "无",
            "argument": "-O0"
        },
        {
            "name": "O1",
            "argument": "-O1"
        },
        {
            "name": "O2",
            "argument": "-O2"
        },
        {
            "name": "O3",
            "argument": "-O3"
        },
        {
            "name": "Ofast",
            "argument": "-Ofast"
        }
    ]
}
```

下面将介绍编译配置的 JSON 格式：

- `compiler` 编译器的命令，注意是命令而不是地址，因此请确保 `compiler` 对应的值可以在命令行 / 终端 下运行。
- `arguments` 编译器的附加参数列表。
- `versions` 对应提交代码中的语言列表。每一项是一个对象，`name` 字段代表名称，`argument` 代表其对应的参数。
- `optimizations` 对应提交代码中的优化列表。每一项是一个对象，`name` 字段代表名称，`argument` 代表其对应的参数。

## 实用工具

### 清理缓存

Hello Judger 在评测时会产生大量缓存文件（有的是源代码，有的是可执行程序）。一般位于程序目录的 `compiling` 和 `checking` 子目录下。您可以手动清理，也可以在【工具(T)】->【清理缓存(C)】或按下 `Ctrl+Shift+Del` 快捷键进行清理。

### OJ 题面搜索

OJ 题面搜索使用 $128$ 位相似哈希（SimHash）算法完成高效匹配。并使用 jieba 全分词和去停用词技术来保证准确率。您可以使用这个功能来：

- 离线寻找 OJ 原题
- 离线题目查重

功能入口：【功能(T)】->【OJ 题面搜索(S)】或者按下 `Ctrl+Shift+F1` 快捷键。

### 从 Hydro 导入

【工具(T)】->【从 Hydro 导入】可以导入 Hydro 压缩包。实际上就是解压。因为 Hello Judger 的题目设计参考了 Hydro。但是还是有一些细节不同，需要您自行修改。

这个功能正在实验。

## 题目

### 提交记录

提交的所有结果会保存在提交记录中，实际上是存在题目目录下的 `submissions.json` 。

您可以在右侧切换到【提交记录】标签页进行查看，并点击对应行的【详细信息】列的按钮查看本行所代表的的提交记录的详细信息。

如果你想清空提交记录，仅需删除 `submissions.json` 即可。

### 题面

题面使用 Markdown 格式，位于题目目录的 `problem_zh.md`。