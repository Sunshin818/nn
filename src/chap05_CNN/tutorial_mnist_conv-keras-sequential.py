#!/usr/bin/env python
# coding: utf-8

# ## 准备数据

# In[1]:
import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, optimizers, datasets
from tensorflow.keras.layers import Dense, Dropout, Flatten # 导入常用网络层：全连接层、正则化层和维度展平层
from tensorflow.keras.layers import Conv2D, MaxPooling2D  # 导入卷积层和最大池化层

#设置TensorFlow日志级别，只显示错误信息
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


def mnist_dataset():
    """
    加载并预处理MNIST数据集，返回训练集和测试集的TensorFlow Dataset对象。
    #代码是使用TensorFlow处理MNIST数据集的预处理流程。MNIST是一个手写数字识别数据集，包含60,000个训练样本和10,000个测试样本，每个样本是28x28像素的灰度图像
    Returns:
        ds (tf.data.Dataset): 处理后的训练数据集。
        test_ds (tf.data.Dataset): 处理后的测试数据集。
    """
    # 加载MNIST手写数字数据集
    # 返回格式：((训练图片, 训练标签), (测试图片, 测试标签))
    (x, y), (x_test, y_test) = datasets.mnist.load_data()
    x = x.reshape(x.shape[0], 28, 28, 1)
    x_test = x_test.reshape(x_test.shape[0], 28, 28, 1)
    # 从NumPy数组创建TensorFlow Dataset对象
    # 每个元素是一个(image, label)对，来自(x, y)
    ds = tf.data.Dataset.from_tensor_slices((x, y))
    ds = ds.map(prepare_mnist_features_and_labels) # 应用预处理
    ds = ds.take(20000).shuffle(20000).batch(100) # 取20000样本，混洗后分100的批次

    # 创建测试数据集管道
    test_ds = tf.data.Dataset.from_tensor_slices((x_test, y_test))
    test_ds = test_ds.map(prepare_mnist_features_and_labels)
    test_ds = test_ds.take(20000).shuffle(20000).batch(20000) # 对取出的 20000 个样本进行随机打乱，shuffle 的参数 20000 表示缓冲区大小，用于随机打乱数据
    # 返回数据集 ds 和处理后的测试数据集 test_ds
    return ds, test_ds


def prepare_mnist_features_and_labels(x, y):
    """
    对MNIST数据集的特征和标签进行预处理。

    Args:
        x: 输入图像数据。
        y: 对应的标签。

    Returns:
        x: 归一化后的图像数据。
        y: 转换为整型的标签。
    """
    x = tf.cast(x, tf.float32) / 255.0 # 归一化
    y = tf.cast(y, tf.int64) # 类型转换
    return x, y


# In[2]:
7 * 7 * 64 # 计算展平后的特征维度：7x7特征图，64个通道 → 3136维向量


# 创建一个基于Keras Sequential API的卷积神经网络模型
# In[3]:
# 构建卷积神经网络（CNN）模型
model = keras.Sequential([
    # 第1层：卷积层（提取初级图像特征）
    # 32个5x5的卷积核，使用ReLU激活函数，保持输入输出尺寸相同（padding='same'）
    Conv2D(32, (5, 5), activation='relu', padding='same'),
    
    # 第2层：最大池化层（下采样，减少计算量）
    # 2x2的池化窗口，步长为2（输出尺寸减半）
    MaxPooling2D(pool_size=2, strides=2),
    
    # 第3层：卷积层（提取更高级特征）
    # 64个5x5的卷积核，ReLU激活，保持尺寸
    Conv2D(64, (5, 5), activation='relu', padding='same'),
    
    # 第4层：最大池化层（进一步下采样）
    # 同上使用2x2池化窗口，步长2
    MaxPooling2D(pool_size=2, strides=2),
    
    # 第5层：展平层（将3D特征图转换为1D向量）
    # 例如：输入形状(N,7,7,64) -> 输出形状(N,3136)
    Flatten(),
    
    # 第6层：全连接层（特征整合）
    # 128个神经元，使用tanh激活函数
    layers.Dense(128, activation='tanh'),
    
    # 第7层：输出层（分类预测）
    # 10个神经元对应10个类别，softmax激活输出概率分布
    layers.Dense(10, activation='softmax')
])

optimizer = optimizers.Adam(0.0001)
# 配置优化器（Adam优化算法）

# ## 编译， fit以及evaluate

# In[4]:
model.compile(
    optimizer = optimizer,# 使用预定义的优化器（如Adam、SGD）更新模型参数
    loss = 'sparse_categorical_crossentropy', # 稀疏分类交叉熵损失函数
    metrics = ['accuracy']# 训练和评估时监控准确率指标
)
# 加载 MNIST 数据集，并将其分为训练集和测试集。
# mnist_dataset 函数可能是自定义的，或者是从某个库中导入的，
# 它应该返回两个数据集对象：train_ds 和 test_ds，分别用于训练和测试。
train_ds, test_ds = mnist_dataset()
# 使用模型对训练数据集进行拟合（即训练）。
# model 是已经构建好的神经网络模型。
# fit 方法会根据设定的批次大小、周期数（epochs）等参数来训练模型。
# epochs=5 表示整个训练集将被遍历 5 次，目的是最小化损失函数。
model.fit(train_ds, epochs=5)
# 在测试数据集上评估模型性能。
# evaluate 方法会计算并返回模型在测试数据集上的损失值和评估指标（例如准确率）。
# 这一步骤用来验证模型的泛化能力，确保模型不仅仅是在训练集上表现良好。
# 在测试集上评估模型，批次大小设为100
model.evaluate(test_ds, batch_size=100)
