# Vim宏
#### Vim-Macro

> [!NOTE] Macro
> . 命令用它来重复小的修改确实有效，但想重复更大规模的改动时， Vim的宏就派上用场了。
> 如果宏执行某个动作命令失败了，Vim将中止执行宏的其余命令。

> [!NOTE] 黄金法则
> **在录制一个宏时，要确保每条命令都可被重复执行。**
> **录制宏时，面向单词的动作命令，如 w、b、e和 ge，与面向字符的动作命令hjkl相比更具灵活和准确性。推荐用查找命令定位或者用文本对象操作。**

> [!NOTE] 在宏的结尾添加命令
> 在输入qa时，Vim将开始录制接下来的按键操作，并将它们保存到寄存器 a中，这会覆盖该寄存器原有的内容。如果输入的是 qA，Vim也会录制按键操作，但会把它们附加到寄存器a原有的内容之后。

> [!NOTE] [编辑宏的内容](../../../files/books/Tools/Vim.pdf#page=281&selection=3,0,3,6)
> 简单来说就是将寄存器的内容粘贴(:put a)出来之后更改，之后再写回寄存器("ay$)。

> [!NOTE] 给列表编号
> 方法1:[使用表达式寄存器](../../../files/books/Tools/Vim.pdf#page=279&selection=45,0,45,3)
> 方法2:`I1.<ESC>qa^yf.jP^<C-a>q`(使用1.形式的列表)

| 操作               | 效果              |
| ---------------- | --------------- |
| q{register}/q    | 开始/停止录制         |
| @{register}      | 执行指定寄存器的内容      |
| @@               | 重复最近调用过的宏       |
| :reg a           | 查看寄存器a的内容       |
| 100@a            | 执行100次宏a        |
| :argdo normal @a | 对参数列表内的所有缓冲区执行宏 |

> [!example] 这些范例都很有价值，请执行类似操作前学习一下
> [把命令序列录制成宏](../../../files/books/Tools/Vim.pdf#page=255&selection=10,0,10,9)
> [用动作命令来判断该宏是否应该在当前上下文中继续执行](../../../files/books/Tools/Vim.pdf#page=260&selection=69,0,71,1)
> [宏与dot范式相结合](../../../files/books/Tools/Vim.pdf#page=262&selection=8,0,10,14)
> [宏的串行与并行](../../../files/books/Tools/Vim.pdf#page=265&selection=0,0,3,12)
> [在一组文件中执行宏](../../../files/books/Tools/Vim.pdf#page=273&selection=7,0,7,8)