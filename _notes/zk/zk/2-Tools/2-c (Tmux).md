# Tmux

> [!NOTE] tutorial
> [A Quick and Easy Guide to tmux ](https://hamvocke.com/blog/a-quick-and-easy-guide-to-tmux/)

#### Sessions
 a session is an independent workspace with one or more windows

| 命令               | 效果              |
| ---------------- | --------------- |
| tmux             | 开启一个新的会话        |
| tmux new -s NAME | 开启一个以NAME为名的新会话 |
| tmux ls          | 列出所有会话          |
| \<C-b> d         | 分离现有会话          |
| tmux a           | attach上一个会话     |
| tmux -t          | attac指定的会话      |
#### Windows
Equivalent to tabs in editors or browsers, they are visually separate parts of the same session

| 命令       | 效果       |
| :------- | :------- |
| \<C-b> c | 创建新窗口    |
| \<C-b> N | 去往第N个窗口  |
| \<C-b> p | 去往上一个窗口  |
| \<C-b> n | 去往下一个窗口  |
| \<C-b> , | 重命名现在的窗口 |
| \<C-b> w | 列出现有窗口   |
| \<C-d>   | 关闭       |

#### Panes
 Like vim splits, panes let you have multiple shells in the same visual display.

| 命令              | 效果                       |
| :-------------- | :----------------------- |
| \<C-b> "        | 水平分裂                     |
| \<C-b> %        | 垂直分裂                     |
| \<C-b> 方向键/hijk | 前往指定方向的窗格                |
| \<C-b> z        | make pane go full screen |
| \<C-b> \<space> | 切换窗格的布局                  |
| \<C-b> x        | 关闭当前窗格                   |
