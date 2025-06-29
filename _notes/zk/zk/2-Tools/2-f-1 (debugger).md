# debugger

> [!NOTE] gdb
> ###### gdb基础命令
> 1. `(l)ist` 命令用于显示当前执行位置附近的源代码。可以指定行号范围，如 `list 10, 20` 表示显示第 10 行到第 20 行的代码。
> 2. `(s)tep`  命令也用于单步执行，但遇到函数调用时会进入函数内部。
> 3. `(n)ext` 命令用于单步执行，遇到函数调用时会将其当作一步直接执行过去。
> 4. `c(ontinue)` 命令用于在程序暂停后继续执行，直到下一个断点或程序结束。
> 5. `(r)un` 命令用于启动程序的执行。可以在后面跟上命令行参数，如 `run arg1 arg2`。
> 6. `(b)reak <行号>` 命令用于在指定行号处设置断点。例如：`break 20`
> 7.  `(b)reak <函数名>` 命令用于在指定函数的入口处设置断点。例如：`break main`。
> 8.  `break <文件名>:<行号>` 命令用于在指定文件的指定行号处设置断点。例如：`break test.c:30`。
> 9. `finish` 命令用于执行完当前函数并返回到调用该函数的地方。
> 10. `(i)nfo (b)reakpoints` 命令用于查看当前设置的所有断点信息。
> 11. `delete <断点编号>` 命令用于删除指定编号的断点。如：`delete 2`
> 12. `disable <断点编号>` 命令用于禁用指定编号的断点
> 13. `(p)rint <变量名>` 命令用于打印指定变量的值。例如：`print num`
> 14. `whatis <变量名>` 命令用于查看指定变量的类型。例如：`whatis num`。
> 15. `set variable <变量名>=<值>` 命令用于修改指定变量的值。例如：`set variable num = 10`。
>
>
> ###### gdb core dump
> `core dump` 是程序在异常终止时生成的一个文件，它包含了程序崩溃时刻的内存状态、寄存器值等信息。借助 GDB（GNU Debugger）来分析 `core dump` 文件，能帮你找出程序崩溃的根源[^1]
>
>  在终端中执行如下命令，可临时允许生成`core dump` 文件。使用 GDB 分析 `core dump` 文件，需要同时提供可执行文件和 `core dump` 文件。
>```
> ulimit -c unlimited
> gdb executable core_file
>```
>
> - `<executable>` 是崩溃程序的可执行文件。
> - `<core_file>` 是生成的 `core dump` 文件。
> ```
> Program terminated with signal SIGFPE, Arithmetic exception.
> #0  0x000055c87f76013b in actual_calc (a=13, b=0) at testgdb.c:3
> 3         c=a/b;
> ```
> **SIGFPE**标明了终止信号
> **#0**则是gdb中**frame**的概念，可以简要理解成步骤/时间帧。`frame <栈帧编号>` 命令用于切换到指定编号的栈帧。
> ```
> (gdb) bt
>  #0  0x000055c87f76013b in actual_calc (a=13, b=0) at testgdb.c:3
>  #1  0x000055c87f760171 in calc () at testgdb.c:12
>  #2  0x000055c87f76018a in main () at testgdb.c:17
> 
> (gdb) f 1
>  #1  0x000055c87f760171 in calc () at testgdb.c:12
>  12        actual_calc(a, b);
> (gdb) p a
>  $1 = 13
> ```
> 你可以通过**bt (backtrace)**来追踪函数栈
> 可以通过 f 1跳到frame 1处（这很重要，因为f=2时a是未被定义的），再用p a来打印a的值
> > [!warning]
> > - Floating point Exception后面没有(core dumped)说明core dumped文件没有生成。
> > - GDB does _not_ check if there is a source code revision match! It is thus of paramount importance that you use the exact same source code revision as the one from which your binary was compiled.

> [!NOTE] pdb
> ###### Basic Command
> 1. `l(ist)` - 展示当前行附近的 11 行，或者是继续之前的展示。
> 2. `s(tep)` - 执行当前行，停在第一个可能停下的地方。
> 1. `n(ext)` - 继续执行程序到当前函数的下一行或者是直到它返回结果。
> 2. `b(reak)` - 设置程序断点 (取决于提供的参数)。
> 3. `r(eturn)` - 继续执行直到当前函数返回结果。
> 3. `c(ontinue)` - 执行到程序断点处。
> ###### Tutorial
> [6.null pdb](files/slides/6.null/missing%20semester%20en.pdf#page=64&selection=37,0,37,9)
> [pdb-tutorial](https://github.com/MartinLwx/pdb-tutorial?tab=readme-ov-file#pdb-101-pdb-%E4%BB%8B%E7%BB%8D)
> [Python Debugging With Pdb](https://realpython.com/python-debugging-pdb/#toc)

> [!NOTE] others
> [What is Reverse Debugging and Why Do We Need It? ](https://undo.io/resources/reverse-debugging-whitepaper)
> [rr: lightweight recording & deterministic debugging](https://rr-project.org/)
> [Debug C and C++ programs with rr ](https://developers.redhat.com/blog/2021/05/03/instant-replay-debugging-c-and-c-programs-with-rr#requirements_and_setup)
> 简单来说，reverse debugging通过记录程序的所有行为（eg:memory access,call to os)，从而通过倒回的方式去定位Bug。

[^1]:[GDB debugging tutorial for beginners](https://linuxconfig.org/gdb-debugging-tutorial-for-beginners)