# Vim global

## 基本形式

> [!NOTE] :global
> :global命令通常采用以下形式（参见 :h :g ）
> :[range] global[!] /{pattern}/ [cmd]
>
> **:global命令结合了Ex命令与Vim的模式匹配这两方面能力。凭借该命令，可以在某个指定模式的所有匹配行上运行Ex命令**。
> 
> 首先，在默认情况下，:global命令的作用范围是整个文件。
> 另外，[cmd]可以是除 :global命令之外的任何**Ex命令**。
>
> [当Ex命令与 :global一起组合使用时，也可以为[cmd]单独指定范围](../../../files/books/Tools/Vim.pdf#page=369&selection=8,0,16,5)

> [!NOTE] :global命令的广义形式
>  :g/{start}/ .,{finish} [cmd] 可以将其解读为“对从 {start} 开始，到 {finish} 结束的所有文本行，执行指定的 [cmd]”。
> . 符号通常表示光标所在行，但在 :global命令的上下文中，它则表示 {pattern} 的匹配行。

> [!NOTE] :v
> :vglobal或简写的 :v命令恰好与 :g命令的操作相反。也就是说，它用于在指定模式的非匹配行上执行Ex命令。
> ```
> :g/re/d 删除所有的匹配行
> :v/re/d 则只保留匹配行
> ```
## 其他

> [!NOTE] 重用上次的查找模式
> 与:substitute相同，:global也可以将查找域留空，从而重用最后一次的查找模式。

> [!NOTE] Grep一词的来历
> 请仔细琢磨一下 :global命令的简写形式： ➾ :g/re/p re表示regular expression，而p是 :print的缩写，它作为缺省的 [cmd]使用。如果我们把符号 / 忽略掉，便会发现单词“grep”已然呼之欲出了。

> [!NOTE] global与寄存器
> :g/TODO/yank A 会把所有包含TODO注释的行复制到a寄存器中。

> [!warning]
> The `:g` command starts positioning the cursor on line one, and goes down to $. 
> But if the commands change the current line, `:g` continues from there(the current line has changed).
> you can analyze an example below named "执行复数个命令"

![Vim-Ex命令](2-Tools/2-a-2-c%20（命令行模式）.md#Vim-Ex命令)