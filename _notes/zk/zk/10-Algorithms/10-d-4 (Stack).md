# Stack

![04.Stack + Queue, 页面 2](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=2)

[Stack-ADT](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=3):各种接口函数的定义及功能
[Stack](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=4):实现与接口(push,pop,top),直接基于向量或列表的接口派生

[Steap](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=93):栈堆，使用两个栈构成的数据结构，P栈中每个元素都是S栈中对应前缀里的最大者

## 栈的应用

> [!example] 函数调用栈
> ![Stack](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=10)

> [!example] 进制转换
> [Stack](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=21):给定任一10进制非负整数，将其转换为n进制表示形式
> >[!faq] 难点
> > - 转换后的位数在事先不能简便地确定，辅助空间如何才能既足够，亦不浪费？
> > - 转换后的各数位是自低而高得到的，如何自高而低输出？
> > - 若使用向量，则扩容策略必须得当；若使用列表，则多数接口均被闲置
> 
>  [代码实现](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=24):短除法：整商 + 余数

> [!example] 括号匹配
> [Stack](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=28):匹配左右括号
> [代码实现](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=29):顺序扫描表达式，用栈记录已扫描的部分(实际上只需记录左括号)。反复迭代,凡遇(，则进栈；凡遇)，则出栈
> >[!faq] 扩展
> > - 多种括号:[如法炮制](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=31)

> [!example] 中缀表达式计算:infix
> ![演示](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=37)
>
> - [思路](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=34):优先级高的局部执行计算，并被代以其数值。运算符渐少，直至得到最终结果
> - [代码实现及执行过程示例](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=39):运算数栈和运算符栈两者配合处理
>
> >[!example] 示例
> > [手工中缀表达式计算](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=51)
>

> [!example] 逆波兰表达式RPN:postfix
>
> ![执行过程示例](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=58)
> - [思路](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=57):在由运算符（operator）和操作数（operand）组成的表达式中，不使用括号（parenthesis-free）即可表示带优先级的运算关系
> - [代码实现中缀表达式转换RPN](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=63)
>
> >[!example] 示例
> > [手工转换RPN](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=61)
>
> >[!faq] PostScript
> > [PostScript](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=65)语言深深地影响了现代印刷业，其便使用了RPN语法。

> [!example] 栈混洗
>
> ![执行过程示例](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=68)
> - [混洗总数SP(n)=?](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=69):catalan(n)
> - [判断序列是否为栈混洗](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=72):任何$1 \le i \le j \le k \le n，[ ..., k , ..., i , ..., j , ... ]$的序列必非栈混洗
> - [括号匹配](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=74):每一个栈混洗，都对应于栈S的n次push与n次pop操作构成的某一序列；反之亦然
>
> >[!faq] 卡特兰数
> >[catalan](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=70)

> [!example] 直方图内最大矩形
>
>  ![执行过程示例](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=84)
> - 可知$maxRect(r) = H[r]* (t(r)-s(r))$
> - $s(r) = max\{k\ | 0 \le k \le r \ and\ H[k-1] < H[r]\}$
> - $t(r) = min\{k\ | r \le k \le n \ and\ H[r] > H[k]\}$
> - 简单来说，就是选择左区间中小于矩形高度的横坐标中的最大者和右区间中大于矩形高度的最大者以获得长度
>  
> 对于所有的 r 来说，我们可以使用[暴力算法](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=86)来获得所有的s(r)与t(r)，但是复杂度太高了。
> 在[栈的帮助](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=87)下，通过s[]数组便可以找到对应的区间。
> 我们甚至可以[一趟扫描](files/slides/Tsinghua-DSA-2024Fall-chapter/04.Stack%20+%20Queue.pdf#page=90)便完成任务。
> > [!quote] exercise
> > [leetcode 84](https://leetcode.cn/problems/largest-rectangle-in-histogram/description/) 
> > [leetcode 42](https://leetcode.cn/problems/trapping-rain-water/)