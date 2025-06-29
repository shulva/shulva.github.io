# Vector
#### 无序向量

![向量](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=6)

[向量ADT](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=7):各种接口函数的定义及功能
[向量类的构造及析构的实现](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=11):代码实现——[基于CopyFrom的构造](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=13)
[向量扩容算法 expand](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=17):代码实现——容量加倍策略
[Java中的Vector](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=69)
> [!faq] 为何采用容量加倍策略呢？其它策略是否也可行？
   [容量递增策略](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=19)vs[容量加倍策略](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=20)
>[对比](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=21):容量加倍策略的分摊扩容时间O(1)显著优于容量递增策略的O(n)

> [!NOTE] 向量操作
> [向量的元素访问get/put](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=24):重载下标操作符比原先的get和put更好(C++自带重载)
> [向量的插入 insert](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=25):插入位置的后继元素顺次后移一位，若有必要则扩容
> [向量的区间删除 remove](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=26):删除区间后的元素向前移，若有必要则缩容 [向量的单元素删除](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=27):借用区间删除，区间长度为1就行了
> [向量的查找 find](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=30):从后向前，顺序查找。输入敏感（input-sensitive），时间复杂度最好O(1)，最差O(n)，与输入强相关
> [向量的去重 dedup](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=32):find + remove 循环
> [向量的遍历 traverse](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=34):指定遍历行为对应的visit函数，将函数作为参数传入

#### 有序向量

[有序向量](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=37):有序性及其甄别——在有序序列中，任何一对相邻元素必顺序。disordered()可用来判断向量是否有序。
**无序向量经预处理转换为有序向量之后，相关算法多可优化。**

> [!NOTE] 有序向量:去jj重
> [低效算法](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=38):多次删除
> [高效算法](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=39):没有显式删除，最后一次性调整空间大小，相当于全部删除

#### 有序向量的查找

> [!NOTE] 有序向量:二分查找
> [二分查找A](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=43):利用向量有序的特性，减而治之
> [二分查找B](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=56):减少迭代中的比较次数

> [!note] 有序向量:fib查找
>   二分查找版本A的缺点在于：转向左、右分支前的关键码比较次数不等，而递归深度却相同 。通过递归深度的不均衡对转向成本的不均衡做补偿，平均查找长度应能进一步缩短
> [pivot](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=50&selection=65,0,65,5)按斐波那契数列来取。算法最优性[证明](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=53)在此。

> [!faq] 查找语义:[更精确的返回值](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=58)
> 事实上，查找即使失败，我们也需要给出新元素可安置的位置（有序性），而不是简单返回个 -1。若有相等的元素，也需按其插入的次序排列（稳定性）。
> 于是我们约定，总是返回的值m有如下约束：
> $$\begin{align} &m = search(e) = M-1 \\ &-\infty \le m = max \ \{k | [k] \le e \} \\ & min \ \{k | e < [k] \}  = M \le +\infty	\end{align}$$

综上，我们可以得出[二分查找版本C](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=61)
版本C严格符合接口的语义规定，平均查找长度ASL在常系数方面$(O(1.0*n\\log n))$也优于上述版本。
C通过确定 a[n]<=e 和 a[n] > e的区间来最后得出精确的返回值。

> [!note] 有序向量:插值查找
> [原理](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=66):基于有序向量的大数定律，动态地去选择轴点pivot

> [!faq] 字长上的比较
> 可知数值n的有效字长为$\log n$
>  - 插值查找 = 在字长意义上的折半查找，$n->\sqrt{n} , \log \sqrt{n} = \dfrac{1}{2} \log n$ 
>  - 二分查找 = 在字长意义上的顺序查找 ，$n -> \dfrac{n}{2} ,\log {\dfrac{n}{2}} = \log n -1$
