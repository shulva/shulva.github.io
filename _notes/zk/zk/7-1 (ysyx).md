# YSYX问题记录

## **预学习阶段**

> [!warning]
> 
> ###### 一生一芯的代码跟踪日志位于另一个分支
> 如果你参加"一生一芯", 请通过`git log tracer-ysyx`查看代码跟踪日志.
>
> ###### git commit 注意事项
> [manually commit after trace](https://ysyx.oscc.cc/docs/ics-pa/0.6.html#local-commit)
### PA0

> [!Question] 实验必做内容：[如何科学地提问](https://ysyx.oscc.cc/docs/2306/preliminary/0.1.html#%E5%A6%82%E4%BD%95%E7%A7%91%E5%AD%A6%E5%9C%B0%E6%8F%90%E9%97%AE)
> 
> ###### 阅读"提问的智慧"和"别像弱智一样提问", 编写读后感
> 读后感：[如何科学地提问-读后感](codetest/typst/report.pdf#page=1&selection=0,0,0,7)
> 一种推荐的提问方式如下:
> ```
> 我在xxx的时候遇到了xxx的错误. 这个错误可以通过以下步骤重现: (描述具体的现象)
> 1. 我的系统版本是xxx, 相关的工具版本是xxx
> 2. 我做了xxx (必要的时候贴个图)
> 3. 然后xxx (必要的时候贴个图)
> ...
> 为了排查这个错误, 我进行了以下尝试: (说明我很希望可以解决问题, 真的没办法才提问的)
> 1. 我做了xxx, 出现了xxx的结果 (必要的时候贴个图)
> 2. 我还做了xxx, 出现了xxx的结果 (必要的时候贴个图)
> ...
> 最后问题还没有解决, 请问我还需要做哪些事情?
> ```
> >
> ###### STFW, RTFM, RTFSC
> STFW: Search The Fuck Web
> RTFM: [Read The Fuck Manual](https://en.wikipedia.org/wiki/RTFM)
> RTFSC: Read The Fuck Source Code

> [!info] 实验选做内容：[First Exploration with GNU/Linux ](https://ysyx.oscc.cc/docs/ics-pa/0.2.html)
> 
> ###### Where is GUI?
> >Have you wondered if there is something that you can do it in CLI, but can not in GUI?
> 
> 例如寻找"shulva"文件夹下所有的jpg文件并在他们的文件名后加上按特定顺序排列的数字。更多示例请阅读[这里](https://www.reddit.com/r/linux/comments/2mur41/what_is_there_you_cannot_do_using_gui_what_you/)。
> 
> ###### Why executing the "poweroff" command requires superuser privilege in some Linux distributions?
> > Can you provide a scene where bad thing will happen if the `poweroff` command does not require superuser privilege?
> 
> Linux毕竟是multi-user的操作系统，poweroff会影响到其他的用户。你并不想在运行关键程序时被人关机打断吧？更详细的解释请阅读[这里](https://unix.stackexchange.com/questions/253767/why-does-reboot-and-poweroff-require-root-privileges)。

> [!info] 实验选做内容：[Linux入门教程](https://ysyx.oscc.cc/docs/ics-pa/linux.html#%E6%8E%A2%E7%B4%A2%E5%91%BD%E4%BB%A4%E8%A1%8C)
> 
> ###### 消失的cd
> > cd没有manpage, 这是为什么? 如果你思考后仍然感到困惑, 试着到互联网上寻找答案.
> 
> 确实不知道原因。所以...RTFM and STFW
> Macos上的man cd 会导向 bulit-in的 manpage,这里有一个[解释](https://superuser.com/questions/1487103/running-whatis-cd-always-returns-nothing-appropriate-on-ubuntu-18-04),但到底为什么会这样？
> 详见 [Why is cd not a program? ](https://unix.stackexchange.com/questions/38808/why-is-cd-not-a-program)and [Shell builtin](https://en.wikipedia.org/wiki/Shell_builtin)and 
> [What is the difference between a builtin command and one that is not? ](https://unix.stackexchange.com/questions/11454/what-is-the-difference-between-a-builtin-command-and-one-that-is-not)
> 
>
> > [!warning] My answer
> > 
> > [While some builtin commands may exist in	more than one shell, their operation may be different	under each shell which supports them.](https://man.freebsd.org/cgi/man.cgi?builtin#DESCRIPTION)
> > 也许是因为各个shell中built-in command的差异，所以这些built-in command没有一个统一的manpage?
> > [这里](https://unix.stackexchange.com/questions/167004/why-dont-shell-builtins-have-proper-man-pages)的讨论和我的观点有相似之处。

> [!Question] 实验必做内容：[More Exploration](https://ysyx.oscc.cc/docs/ics-pa/0.5.html)
> 
> ###### Write a "Hello World" program under GNU/Linux
> [hello.c](../../codetest/c&Makefile/hello.c)
> ###### Write a Makefile to compile the "Hello World" program
> [Makefile](../../codetest/c&Makefile/Makefile)
> ###### Learn to use GDB
> [retry_gdb](../../codetest/c&Makefile/retry.sh)
> [2-f-1 (debugger)](2-Tools/2-f-1%20(debugger).md)

> [!info] 实验选做内容：[More Exploration](https://ysyx.oscc.cc/docs/ics-pa/0.5.html)
> 
> ###### Things behind scrolling
> > why the original terminal can not be scrolled? 
> > How does `tmux` make the terminals scrollable? 
> > And last, do you know how to implement a scroll bar?
>
> [Terminal vs Terminal emulator](https://unix.stackexchange.com/questions/254359/terminal-vs-terminal-emulator)
> 假设original terminal指的是VGA text mode？
> 算了，这个思考题本身质量不高，很多问题中的定义较为模糊，我认为可以不回答

> [!info] 实验选做内容：[Getting Source Code for PAs](https://ysyx.oscc.cc/docs/ics-pa/0.6.html#compiling-and-running-nemu)
> 
> ###### What happened?
> > But do you have any idea about what happened when a bunch of information is output to the screen during `make` is executed?
> 
> make executes commands in the makefile to update one or more target *names*, where *name* is typically a program.
>

### Linux系统安装和基本使用

> [!Question] 实验必做内容：[Linux系统安装和基本使用 (oscc.cc)](https://ysyx.oscc.cc/docs/2306/preliminary/0.2.html)
> 
> ###### MIT The Missing Semester
> [missing semester en](../../files/slides/6.null/missing%20semester%20en.pdf)
> [计算机教育中缺失的一课-讲义及答案](https://missing-semester-cn.github.io/)
> [6.null_assignment](../../mooc/6.null)

### 复习C语言
