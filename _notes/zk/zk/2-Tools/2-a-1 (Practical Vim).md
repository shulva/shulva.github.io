# Practical Vim
#vim

> [!Abstract] Vim 解决问题的方式
> 
> ###### dot范式
> 尽量使用 Vim 中的精髓部分——dot(.)，不停地执行 - 重复[^1]
> ###### 控制撤销命令的粒度 
> 在 Vim 中，我们自己可以控制撤销命令的粒度。从进入插入模式开始，直到返回普通模式为止，在此期间输入或删除的任何内容都被当成一次修改。这样我们的 undo 便能更加灵活[^2]
> ###### 尽量构造简易可重复的修改
> 可重复的操作可以最大限度发挥 dot 的威力[^3]
> ###### 能够重复，就别用次数
> 能够重复，就别用次数去重复执行命令。因为这是基于 dot 范式的[^4]
> ###### 如果可以，最好使用操作符命令，而不是可视模式
> 操作符命令修改文本时在 dot 范式下的表现优于可视模式[^5]
> ###### 命令行模式复制更高效
> 在复制距离较远的行时，:t 命令通常比 yyp 更加高效（减少了移动的次数）[^6]
> 
> > [!Example] 实战示例
> >
> >  [R -- 进入替换模式 ](../../../files/books/Tools/Vim.pdf#page=87)
> 推荐使用 gR 进入虚拟替换模式，详见链接。
> >
> > [不离开插入模式粘贴寄存器中的文本](../../../files/books/Tools/Vim.pdf#page=80)
> > [列块编辑表格](../../../files/books/Tools/Vim.pdf#page=101&selection=3,3,4,2)
> >[修改整列块的文本](../../../files/books/Tools/Vim.pdf#page=104&selection=3,0,3,5)
> > [在长短不一的高亮块后添加文本](../../../files/books/Tools/Vim.pdf#page=106&selection=3,0,3,14)
> > [用高亮选区指定命令行模式范围](../../../files/books/Tools/Vim.pdf#page=116&selection=75,0,75,9)

> [!Abstract] 跳转
> [hjkl 是低效的移动方式](../../../files/books/Tools/Vim.pdf#page=186&selection=113,0,131,3)
> 
> >[!example]
> > [动作 + 查找](../../../files/books/Tools/Vim.pdf#page=203&selection=53,0,53,16)

[^1]: [dot 范式](../../../files/books/Tools/Vim.pdf#page=54)
[^2]: [控制撤销命令的粒度](../../../files/books/Tools/Vim.pdf#page=58)
[^3]: [尽量构造简易可重复的修改](../../../files/books/Tools/Vim.pdf#page=60)
[^4]: [能够重复，就别用次数](../../../files/books/Tools/Vim.pdf#page=67)
[^5]: [如果可以，最好使用操作符命令，而不是可视模式](../../../files/books/Tools/Vim.pdf#page=98)
[^6]: [命令行模式复制更高效](../../../files/books/Tools/Vim.pdf#page=122&selection=0,0,37,2) 
[^7]: [控制撤销命令的粒度](../../../files/books/Tools/Vim.pdf#page=58)