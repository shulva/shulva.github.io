# Tree

![Rooted Tree](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=3)

[树的接口](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=10):root(),parent()...
[父节点+孩子节点的概念](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=11)

> [!NOTE] intro
> [Ordered Tree 有序树](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=3)：兄弟节点间有次序关系。
> [路径+环路](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=5)：
> - $V中的k+1个节点，通过V中的k条边依次相联，构成一条路径/通路$
> - $\pi = \{(v_0,v_1),(v_1,v_2),...(v_{k-1},v_k)\},v_0=v_k即为环路$
>
> [连通+无环](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=6)：节点之间均有路径称为连通图。不含环路则为无环图。
> [深度+高度](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=7)

## 二叉树

![二叉树接口](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=15)

 [BinNode-Template](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=21)：二叉树节点模版类
 [BinNode](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=22)：插入新节点，更新高度
 
 [BinTree-Template](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=24)：二叉树模版类
 [BinTree](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=25)：插入新节点，接入/分离子树

> [!NOTE] intro
> [长子-兄弟表示法](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=16)：有根且有序的多叉树，均可转化并表示为二叉树。长子=左孩子，兄弟=右孩子
> [节点-边的数量公式](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=17)
> [满二叉树](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=18)：顾名思义，如果每一个层的结点数都达到最大值，则这个二叉树就是满二叉树。
> [真二叉树](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=19)：通过引入外部节点,可使原有节点度数统一为2。如此，即可将任一二叉树转化为真二叉树。节点度数除了0就是2。
> [完全二叉树](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=72)：叶节点仅限于最低两层。底层叶子，均居于次底层叶子左侧。叶节点不会少于内部节点，但至多多出一个。

### 二叉树的遍历

 > [!NOTE] 先序遍历
 > ![BinNode-Template](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=33)
 > 先序遍历的[递归实现](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=35)是比较容易的，那么它的迭代实现又如何呢？
 > [代码实现-迭代](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=35)：如图所示，访问子树x的藤蔓，各右子树（根）入栈
 > [实例](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=37)
 
  > [!NOTE] 中序遍历
 > ![BinNode-Template](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=41)
 > 中序遍历的[递归实现](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=39)是比较容易的，那么它的迭代实现又如何呢？
 > [代码实现-迭代](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=43)：如图所示，访问子树x的藤蔓，各右子树（根）入栈
 > [实例](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=45)如链接所示。
 >
>  >[!faq] 正确性与效率
 > > [正确性](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=47)：数学归纳
 > > [效率](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=48)：分摊分析->O(n)
 >
>  >[!faq] 中序遍历的直接后继
 > > [正确性](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=51)：最靠左的右后代或最低的左祖先


  > [!NOTE] 后序遍历
 > ![BinNode-Template](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=57)
 > 后序遍历的[递归实现](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=54)是比较容易的，那么它的迭代实现又如何呢？
 > [代码实现-迭代](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=59)：从根出发下行 尽可能沿左分支。实不得已，才沿右分支
 > [实例](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=61)如链接所示。
 >
>  >[!faq] 表达式树-括号匹配-逆波兰表达式
 > > [三者之间的内在关系](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=66)

  > [!NOTE] 层次遍历
 > [代码实现-迭代](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=68)：队列实现
 > [实例](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=69)如链接所示。
 >
>  >[!faq] 完全二叉树
 > > [完全二叉树的层次遍历](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=73)

### 二叉树的重构

当我们知晓一棵二叉树的[先序/后序和中序时](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=77)，我们就可以还原这棵树。只知道先序和后序是不能还原的。
但是，在特殊的[真二叉树](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=19)的情况下，只知道先序和后序是可以还原这棵二叉树的。

  > [!example] 题目示例
  > [106. 从中序与后序遍历序列构造二叉树](https://leetcode.cn/problems/construct-binary-tree-from-inorder-and-postorder-traversal/)

  > [!NOTE] 增强序列
 > [增强序列](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=82)：假想地认为，每个NULL也是真实的节点，并在遍历时一并输出。每次递归返回，同时输出一个事先约定的元字符“^”
 > 如此，通过对增强序列分而治之，即可[重构原树](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=83)
### Huffman树

![huffman](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=86)

由于字符的频率不同，我们的编码树可以使用[Huffman的贪心策略](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=92)构建最优带权编码树，尽管贪心策略未必总能得到最优解，但非常幸运，如上算法的确能够得到最优编码树之一

>  >[!faq] Huffman最优编码树的特性
 > > [正确性证明](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=97)：数学归纳
 > > [双子性，不唯一性等等](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=94)
 
[Huffman编码树代码实现](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=102)
[Huffman编码树改进策略](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=108)

## 代数判定树

- 在可解的前提下，可否谈论问题的**难度**？如何比较不同问题的难度？
- 问题P若存在算法，则所有算法中最低的复杂度称为P的难度
- 设计复杂度更低的算法 + 证明更高的问题难度下界 
- 一旦算法的复杂度达到难度下界，则说明就大O记号的意义而言，算法已经最优

![判定树](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=114)

线性规约:
![判定树](files/slides/Tsinghua-DSA-2024Fall-chapter/05.Binary%20Trees.pdf#page=119)