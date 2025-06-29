# List

#### 数据结构对比

> [!faq] 数据结构对比
> ###### 静态与动态的对比:[是否修改数据结构？](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=2)
> - 静态：数据空间整体创建或销毁，对于不动数据结构组成的较优
> - 动态：为各数据元素动态地分配和回收的物理空间，对于改变数据结构局部或整体的操作更优
> ###### call-by-rank vs call-by-position
> [List:call-by-position](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=4):循位置访问：利用节点之间的相互引用，找到特定的节点
> [Vector:call-by-rank](files/slides/Tsinghua-DSA-2024Fall-chapter/02.Vector.pdf#page=6):各元素与\[0, n)内的秩(rank)一一对应
> RAM与图灵机的操作模式或许各自暗合了这两种思想？
> **思考各种排序的复杂度时，你需要将这几个要素纳入参考!**
> ###### 综合性
> [Tree](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=2)则能兼具Vector和List的优点，同时具有高效的搜索，插入，删除

#### 无序列表

![List](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=3)

[ListNode](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=6):列表基本元素列表结点定义
[List-ADT](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=8):各种接口函数的定义及功能
[List-template](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=8):实现及初始化

> [!NOTE] 列表操作
> [List[]](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=11):重载下标操作符
> [List.insert(e,p)](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=13):将e当做p的前驱插入
> [List.remove(p)](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=15):删除合法节点p
> [List()](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=18):构造，拷贝与析构函数
> [List.find(e,n,p)](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=21):自后向前，逐个比对。在p的n个前驱中，寻找等于e的最靠后者
> [List.dedup()](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=22):去重，和Vector.dedup()相似
> [List.traverse()](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=24):遍历

#### 有序列表

> [!NOTE] 有序列表操作
> [List.uniquify()](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=11):去重，只需遍历整个列表一趟，仅需$O(n)$
> [List.search(e,n,p)](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=11):在有序列表内节点p的n个真前驱中，找到不大于e的最靠后者

 > [!faq] 循环节
> [cycle](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=38):不明白这个东西的意义所在

#### 其他

[列表的游标实现](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=61)
[Python中的列表](files/slides/Tsinghua-DSA-2024Fall-chapter/03.List.pdf#page=74)