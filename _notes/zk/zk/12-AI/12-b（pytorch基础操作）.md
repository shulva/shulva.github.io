# pytorch

### 数据操作

##### 创建基本单元[^1]

![](../../../files/slides/d2l/part-0_4.pdf#page=2)

 深度学习存储和操作数据的主要接口是张量（n维数组）。它提供了各种功能，包括基本数学运算、广播、索引、切片、内存节省和转换其他Python对象。

张量（tensor）表示一个由数值组成的数组，这个数组可能有多个维度。 具有一个轴的张量对应数学上的_向量_（vector）, 具有两个轴的张量对应数学上的_矩阵_（matrix）

我们可以使用 `arange` 创建一个行向量 x

这个行向量包含以0开始的前12个整数，它们默认创建为整数。也可指定创建类型为浮点数。张量中的每个值都称为张量的 _元素_（element）

除非额外指定，新的张量将存储在内存中，并采用基于CPU的计算

```python
x = torch.arange(12)
tensor([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11])
```

可以通过张量的`shape`属性来访问张量（沿每个轴的长度） 
`shape`属性说明了**张量有多少个维度**以及**每个维度上有多少个元素**

```python
x.shape
torch.Size([12])

torch.tensor([[1, 2, 3], [4, 5, 6]])
torch.Size([2, 3])
```

要想改变一个张量的形状而不改变元素数量和元素值，可以调用`reshape`函数。

```python
X = x.reshape(3, 4)
tensor([[ 0,  1,  2,  3],
        [ 4,  5,  6,  7],
        [ 8,  9, 10, 11]])
```

有时，我们希望使用全0、全1，或者从特定分布中随机采样的数字来初始化矩阵。

```python
torch.zeros((2, 3, 4)) #torch.ones((2, 3, 4))同理
tensor([[[0., 0., 0., 0.],
         [0., 0., 0., 0.],
         [0., 0., 0., 0.]],

        [[0., 0., 0., 0.],
         [0., 0., 0., 0.],
         [0., 0., 0., 0.]]])
```

以下代码创建一个形状为（3,4）的张量。 其中的每个元素都从均值为0、标准差为1的标准高斯分布（正态分布）中随机采样

```python
torch.randn(3, 4)
tensor([[-0.0135,  0.0665,  0.0912,  0.3212],
        [ 1.4653,  0.1843, -1.6995, -0.3036],
        [ 1.7646,  1.0450,  0.2457, -0.7732]])
```

##### 运算符[^2]
对于任意具有相同形状的张量， 常见的标准算术运算符（`+`、`-`、`*`、`/`和`**`）都可以被升级为按元素运算。 我们可以在同一形状的任意两个张量上调用按元素操作。

```python
x = torch.tensor([1.0, 2, 4, 8])
y = torch.tensor([2, 2, 2, 2])
x + y, x - y, x * y, x / y, x ** y  # **运算符是求幂运算


(tensor([ 3.,  4.,  6., 10.]),
 tensor([-1.,  0.,  2.,  6.]),
 tensor([ 2.,  4.,  8., 16.]),
 tensor([0.5000, 1.0000, 2.0000, 4.0000]),
 tensor([ 1.,  4., 16., 64.]))
 
torch.exp(x) #e的指数运算
tensor([2.7183e+00, 7.3891e+00, 5.4598e+01, 2.9810e+03])
```

我们也可以把多个张量_连结_（concatenate）在一起， 把它们端对端地叠起来形成一个更大的张量。 

我们只需要提供张量列表，并给出沿哪个轴连结。 下面的例子分别演示了当我们沿行（轴-0，形状的第一个元素） 和按列（轴-1，形状的第二个元素）连结两个矩阵时，会发生什么情况。

```python
X = torch.arange(12, dtype=torch.float32).reshape((3,4))
Y = torch.tensor([[2.0, 1, 4, 3], [1, 2, 3, 4], [4, 3, 2, 1]])
torch.cat((X, Y), dim=0), torch.cat((X, Y), dim=1)

(tensor([[ 0.,  1.,  2.,  3.],
         [ 4.,  5.,  6.,  7.],
         [ 8.,  9., 10., 11.],
         [ 2.,  1.,  4.,  3.],
         [ 1.,  2.,  3.,  4.],
         [ 4.,  3.,  2.,  1.]]),
 tensor([[ 0.,  1.,  2.,  3.,  2.,  1.,  4.,  3.],
         [ 4.,  5.,  6.,  7.,  1.,  2.,  3.,  4.],
         [ 8.,  9., 10., 11.,  4.,  3.,  2.,  1.]]))
```

有时，我们想通过_逻辑运算符_构建二元张量。 以`X == Y`为例： 对于每个位置，如果`X`和`Y`在该位置相等，则新张量中相应项的值为1。 这意味着逻辑语句`X == Y`在该位置处为真，否则该位置为0。

```python
X == Y
tensor([[False,  True, False,  True],
        [False, False, False, False],
        [False, False, False, False]])

X.sum() #对张量中的所有元素进行求和，会产生一个单元素张量。
tensor(66.)
```

##### 广播机制[^3]
在上面的部分中，我们看到了如何在相同形状的两个张量上执行按元素操作。 在某些情况下，即使形状不同，我们仍然可以通过调用 _广播机制_（broadcasting mechanism）来执行按元素操作


 这种机制的工作方式如下：

1. 通过适当复制元素来扩展一个或两个数组，以便在转换之后，两个张量具有相同的形状；
2. 对生成的数组执行按元素操作。

```python
a = torch.arange(3).reshape((3, 1))
b = torch.arange(2).reshape((1, 2))
a, b

(tensor([[0],
         [1],
         [2]]),
 tensor([[0, 1]]))

```

由于`a`和`b`分别是3×1和1×2矩阵，如果让它们相加，它们的形状不匹配。 我们将两个矩阵**广播**为一个更大的3×2矩阵(相当与这两个矩阵的行和列找到了最大公约数)。如下所示：矩阵`a`将复制列， 矩阵`b`将复制行，然后再按元素相加

```python
a + b
tensor([[0, 1],
        [1, 2],
        [2, 3]])
```

#####  索引和切片[^4]
就像在任何其他Python数组中一样，张量中的元素可以通过索引访问

与任何Python数组一样：第一个元素的索引是0，最后一个元素索引是-1

注:[x:y]语法是开闭区间，在数学上是[x,y)
注:[::3, ::2]的简要意思是：
- **在第一个维度（通常是行）：** 从第 0 行开始，每隔 3 行选取一行。
- **在第二个维度（通常是列）：** 从第 0 列开始，每隔 2 列选取一列。

![](../../../files/images/AI/12-b1.png)

如果我们想为多个元素赋值相同的值，我们只需要索引所有元素，然后为它们赋值
```python
X
tensor([[ 0.,  1.,  2.,  3.],
        [ 4.,  5.,  8.,  7.],
        [ 8.,  9., 10., 11.]])

X[0:2, :] = 12
tensor([[12., 12., 12., 12.],
        [12., 12., 12., 12.],
        [ 8.,  9., 10., 11.]])
```

##### 节省内存[^6]

运行一些操作可能会导致为新结果分配内存。 例如，如果我们用`Y = X + Y`，我们将取消引用`Y`指向的张量，而是指向新分配的内存处的张量

```python
before = id(Y)
Y = Y + X
id(Y) == before False #新分配了内存

```

这可能是不可取的，原因有两个：

1. 首先，我们不想总是不必要地分配内存。在机器学习中，我们可能有数百兆的参数(矩阵会很大!），并且在一秒内多次更新所有参数。通常情况下，我们希望原地执行这些更新，否则会占有太多内存。
    
2. 如果我们不原地更新，其他引用仍然会指向旧的内存位置，这样我们的某些代码可能会无意中引用旧的参数。

我们可以使用切片表示法将操作的结果分配给先前分配的数组，例如`Z[:] = <expression>`。 为了说明这一点，我们首先创建一个新的矩阵`Z`，其形状与另一个`Y`相同， 使用`zeros_like`来分配一个全0的块。

```python
Z = torch.zeros_like(Y)
print('id(Z):', id(Z))
Z[:] = X + Y
print('id(Z):', id(Z))

id(Z): 140327634811696
id(Z): 140327634811696 #相同

#如果在后续计算中没有重复使用X， 我们也可以使用X[:] = X + Y或X += Y来减少操作的内存开销。

before = id(X)
X += Y
id(X) == before True #没有新分配内存
```

##### 转换为其他Python对象[^5]

将深度学习框架定义的张量转换为NumPy张量（`ndarray`）很容易，反之也同样容易

torch张量和numpy数组将共享它们的底层内存，就地操作更改一个张量也会同时更改另一个张量

```python
A = X.numpy()
B = torch.tensor(A)
type(A), type(B)

(numpy.ndarray, torch.Tensor)

要将大小为1的张量转换为Python标量，我们可以调用item函数或Python的内置函数。

a = torch.tensor([3.5])
a, a.item(), float(a), int(a)

(tensor([3.5000]), 3.5, 3.5, 3)
```

### 数据预处理

##### 读取数据集[^7]
我们首先创建一个人工数据集，并存储在CSV（逗号分隔值）文件 `../data/house_tiny.csv`中

下面我们将数据集按行写入CSV文件中:
```python
import os

os.makedirs(os.path.join('..', 'data'), exist_ok=True)
data_file = os.path.join('..', 'data', 'house_tiny.csv')

#以写入模式打开 (或创建并打开) house_tiny.csv 文件，并将文件对象赋给 f，以便后续写入内容。并且确保操作完成后文件会被自动关闭

with open(data_file, 'w') as f:
    f.write('NumRooms,Alley,Price\n')  # 列名
    f.write('NA,Pave,127500\n')  # 每行表示一个数据样本
    f.write('2,NA,106000\n')
    f.write('4,NA,178100\n')
    f.write('NA,NA,140000\n')

import pandas as pd

data = pd.read_csv(data_file)
print(data)

   NumRooms Alley   Price
0       NaN  Pave  127500
1       2.0   NaN  106000
2       4.0   NaN  178100
3       NaN   NaN  140000

```

##### 处理缺失值[^8]

“NaN”项代表缺失值。 为了处理缺失的数据，典型的方法包括插值法和删除法， 其中插值法用一个替代值弥补缺失值，而删除法则直接忽略缺失值

```python
# iloc()为pd中基于整数位置选择数据的方法,类似于python中数组的方法
inputs, outputs = data.iloc[:, 0:2], data.iloc[:, 2]

# fillna()用于填充Nan缺失值,mean()用来计算均值
inputs = inputs.fillna(inputs.mean())
print(inputs)

   NumRooms Alley
0       3.0  Pave
1       2.0   NaN
2       4.0   NaN
3       3.0   NaN

```

`inputs`中缺少的数值，我们用同一列的均值替换“NaN”项

对于`inputs`中的类别值或离散值，我们将“NaN”视为一个类别。 由于Alley列只接受两种类型的类别值Pave和NaN， `pandas`可以自动将此列转换为两列“Alley_Pave”和“Alley_nan”。

```python
inputs = pd.get_dummies(inputs, dummy_na=True)
print(inputs)

   NumRooms  Alley_Pave  Alley_nan
0       3.0           1          0
1       2.0           0          1
2       4.0           0          1
3       3.0           0          1

```

##### 转换为张量格式[^9]

现在`inputs`和`outputs`中的所有条目都是数值类型，它们可以转换为张量格式

```python
import torch

X = torch.tensor(inputs.to_numpy(dtype=float))
y = torch.tensor(outputs.to_numpy(dtype=float))
X, y

(tensor([[3., 1., 0.],
         [2., 0., 1.],
         [4., 0., 1.],
         [3., 0., 1.]], dtype=torch.float64),
 tensor([127500., 106000., 178100., 140000.], dtype=torch.float64))
```

当数据采用张量格式后，可以通过在[数据操作](12-b（pytorch基础操作）.md#数据操作)中引入的那些张量函数来进一步操作


[^1]: https://zh-v2.d2l.ai/chapter_preliminaries/ndarray.html#id2

[^2]: https://zh-v2.d2l.ai/chapter_preliminaries/ndarray.html#id3

[^3]: https://zh-v2.d2l.ai/chapter_preliminaries/ndarray.html#subsec-broadcasting

[^4]: https://zh-v2.d2l.ai/chapter_preliminaries/ndarray.html#id5

[^5]: https://zh-v2.d2l.ai/chapter_preliminaries/ndarray.html#python

[^6]: https://zh-v2.d2l.ai/chapter_preliminaries/ndarray.html#id6

[^7]: https://zh-v2.d2l.ai/chapter_preliminaries/pandas.html#id2

[^8]: https://zh-v2.d2l.ai/chapter_preliminaries/pandas.html#id3

[^9]: https://zh-v2.d2l.ai/chapter_preliminaries/pandas.html#id4
