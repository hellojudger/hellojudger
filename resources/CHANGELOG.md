# 说明

下文中【后端】特指评测核心，【前端】特指 GUI。

# v1.4 更新内容

**前端**

- 提交代码：添加独立窗口编辑代码功能。
- 评测颜色配置：添加更加友好的编辑工具。


**后端**

- Special Judge ：彻底解决 Testlib 问题。这时您无需手动导入 Testlib，我们会帮您导入。
- 编译：修复了语言设置无用的 Bug


# v1.3 更新内容

**前端**

- 评测：双击评测的状态所在的单元格可以查看评测具体信息。
- 许可证预览：从 Text Browser 改为 Markdown 预览。[Markdown 来源：Github TheFox/GPLv3.md ](https://github.com/TheFox/GPLv3.md)
- Markdown 预览：链接跳转禁用逻辑被轻微修改。具体来说，现在的链接拥有链接样式但却不能响应点击，链接地址将会以鼠标 Tooltip 的方式展示。
- 界面美化：将 QtModern 改为 Fusion。

**后端**

- 评测：修复了 Linux 在特定情况没有权限的 Bug
- 评测：修复了提交死循环程序系统无法结束的 Bug。

# v1.2 更新内容

**前端**

- 右侧卡片改为 Tab Widget，并添加 【附加信息】和【通过量统计】两个页面。
- 修复了上一个版本过度精简 Monaco Editor 导致 Java Script 错误的 Bug
- 给文档添加了【OK】按钮。
- 添加了【清理缓存】功能。
- 添加了【重新打开题目】功能。
- 添加图标 <a href="https://www.flaticon.com/free-icons/exam" title="exam icons">Exam icons created by Freepik - Flaticon</a>
- 添加了【OJ 题面搜索】功能，目前支持 UOJ。
- 添加了题目评测结果配色功能。

**后端**

- 评测：添加【是否 AC】统计，以便统计通过量。

# v1.1 更新内容

**前端**

- 代码编辑器(Monaco Editor)：汉化
- Markdown 预览：关闭了英文上下文菜单
- 配置、题面编辑：新增内部编辑器
- 关于：新增多项栏目以便快速了解 Hello Judger。
- LICENSE：新增内部查看器

**后端**

- 评测：修复了 Linux 因权限不足而无法评测的 Bug。
- Special Judge：修复了多项 Bug，并改为了源代码。由内部编译。目前尚在测试。

**其他**

- 精简了 Monaco Editor 包
- 删除了示例题目 【CSP/S 2022 策略游戏】
