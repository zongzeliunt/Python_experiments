#这个是我自己写的程序，用来测试我自己的函数和TF的函数完全match
#TF flow怎么跑，参考my_program.py


import tensorflow.compat.v1 as tf
tf.disable_eager_execution()

import os
import argparse
import sys
import numpy as np
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


TF = 1 

def weight_variable(shape):
#{{{
  """weight_variable generates a weight variable of a given shape."""
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)
#}}}

def bias_variable(shape):
#{{{
	"""bias_variable generates a bias variable of a given shape."""
	initial = tf.constant(np.float64(0.1), shape=shape)
	return tf.Variable(initial)
#}}}

def conv2d(x, W):
#{{{
  	"""conv2d returns a 2d convolution layer with full stride."""
  	#stride = [1,水平移动步长,竖直移动步长,1]
	#[0] 和[3]必须都是1
	#padding 是和原图一样
  	return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')
#}}}

def max_pool_2x2(x):
#{{{
  """max_pool_2x2 downsamples a feature map by 2X."""
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding='SAME')
#}}}


def W_write_4d  (matrix, shape, file_name):
#{{{
	fl = open(file_name, "w")
	for l_0 in range( shape[0]):
		for l_1 in range( shape[1]):
			for l_2 in range( shape[2]):
				string = ""
				for l_3 in range( shape[3]):

					string += str(matrix[l_0][l_1][l_2][l_3]) + " "
				fl.write(string + "\n")
	fl.close() 
#}}}
	
def W_read_4d (shape, file_name):
#{{{
	result = np.zeros (shape)
	
	fl = open(file_name, "r")
	for l_0 in range( shape[0]):
		for l_1 in range( shape[1]):
			for l_2 in range( shape[2]):
				string = fl.readline()
				string.replace('\n', '')
				string = string.split(' ')
				line = np.zeros(shape[3])
				for l_3 in range( shape[3]):
					line[l_3] = float(string[l_3])
				result[l_0][l_1][l_2] = line
	fl.close() 
	return result
#}}}

def W_write_2d  (matrix, shape, file_name):
#{{{
	fl = open(file_name, "w")
	for l_0 in range( shape[0]):
		string = ""
		for l_1 in range( shape[1]):
			string += str(matrix[l_0][l_1]) + " "
		fl.write(string + "\n")
	fl.close() 
#}}}
	
def W_read_2d (shape, file_name):
#{{{
	result = np.zeros (shape)
	
	fl = open(file_name, "r")
	for l_0 in range( shape[0]):
		string = fl.readline()
		string.replace('\n', '')
		string = string.split(' ')
		line = np.zeros(shape[1])
		for l_1 in range( shape[1]):
			line[l_1] = float(string[l_1])
		result[l_0] = line
	fl.close() 
	return result
#}}}

def two_file_compare (file1, file2, shape):
#{{{
	data_1 = W_read_4d (shape, file1)
	data_2 = W_read_4d (shape, file2)

	
	for l0 in range (shape[0]):	
		for l1 in range (shape[1]):	
			for l2 in range (shape[2]):	
				for l3 in range (shape[3]):	
					if abs(data_1[l0][l1][l2][l3] - data_2[l0][l1][l2][l3]) >= 0.000001:
						return False

	return True
#}}}


def judge_size (x):
#{{{
	#在这里默认x是四维的
	x_shape = [len(x), len(x[0]), len(x[0][0]), len(x[0][0][0])]
	return x_shape
#}}}

def my_conv2d (x, W):
#{{{
	x_shape = judge_size(x)
	w_shape = judge_size(W)
	
	x_row = x_shape[1]
	x_col = x_shape[2]
	x_in_size = x_shape[3]
	
	w_row = w_shape[0]
	w_col = w_shape[1]
	w_in_size = w_shape[2]
	w_out_size = w_shape[3]
	#按说x_in_size 和 w_in_size应该是一样的
	#x第一维默认只有1，我不确定是不是应该这样，但是先这么写
	
	#计算mid，mid的意义去看develop_log
	mid = 0
	w_size = w_row
	w_mid = int(w_size / 2)
	w_mid_rem = w_size % 2
	
	w_mid_reduce = 0
	if w_mid_rem == 0:
		w_mid_reduce = 1
	
	mid = w_mid - w_mid_reduce

	result_shape = [1, x_row, x_col, w_out_size]
	
	result = np.zeros (result_shape)

	for x_in_row in range(x_row):
		for x_in_col in range(x_col):
			result_spot = np.zeros(w_out_size)
			for w_in_row in range(w_row):
				for w_in_col in range(w_col):

					x_pos_row = x_in_row - mid + w_in_row
					x_pos_col = x_in_col - mid + w_in_col
					if x_pos_row < 0:
						continue 
					if x_pos_col < 0:
						continue

					if x_pos_row >= x_row:
						continue 
					if x_pos_col >= x_col:
						continue

					for in_pos in range(x_in_size):
						#在这里，假如in_pos是1,那这层loop就没用了
						for out_pos in range (w_out_size):
							result_spot[out_pos] += x[0][x_pos_row][x_pos_col][in_pos] * W[w_in_row][w_in_col][in_pos][out_pos]



			result [0][x_in_row][x_in_col] = result_spot
	return result
#}}}

def single_relu (x):
	return x if x > 0 else 0

def my_relu_4d(x):
#{{{
	x_shape = judge_size(x)
	result = np.zeros(x_shape)
	for row in range (x_shape[1]):	
		for col in range (x_shape[2]):
			for i in range (x_shape[3]):
				result[0][row][col][i] = single_relu(x[0][row][col][i])
	return result

#}}}

def my_relu_2d(x):
#{{{
	x_shape = [len(x), len(x[0])]
	result = np.zeros(x_shape)
	for row in range (x_shape[0]):	
		for col in range (x_shape[1]):	
			result[row][col] = single_relu(x[row][col])
	return result

#}}}

def my_pool_2x2 (x):
#{{{
	x_shape = judge_size(x)
	x_row = x_shape[1]	
	x_col = x_shape[2]	
	x_out_size = x_shape[3]

	pool_step = 2 
	#这个pool_step和kernel_step不是一个东西，这个step决定了输出图的大小
	#大致是这个strides里的2 × 2 
	#strides=[1, 2, 2, 1]

	kernel_size = 2
	#这个	kernel_size 是那个罩在图上的kernel大小，ksize=[1, 2, 2, 1]

	r_row = int(x_row / pool_step)
	r_row_rem = x_row % pool_step
	if r_row_rem != 0:
		r_row += 1
	
	r_col = int(x_col / pool_step)
	r_col_rem = x_col % pool_step
	if r_col_rem != 0:
		r_col += 1

	result_shape = [1, r_row, r_col, x_out_size]

	result = np.zeros (result_shape)
	
	for r_row_pos in range (r_row):
		for r_col_pos in range (r_col):
			result_tmp = np.zeros(x_out_size)
			x_row_pos = r_row_pos * pool_step
			x_col_pos = r_col_pos * pool_step
			for out_pos in range (x_out_size):
				out_tmp_list = []
				for k_row_pos in range (kernel_size):
					for k_col_pos in range (kernel_size):
						x_point_row_pos = x_row_pos + k_row_pos
						x_point_col_pos = x_col_pos + k_col_pos

						if x_point_row_pos >= x_row:
							continue
						
						if x_point_col_pos >= x_col:
							continue

						x_point = x[0][x_point_row_pos][x_point_col_pos]
						out_tmp_list.append(x_point[out_pos])	
		
				result_tmp[out_pos] = max (out_tmp_list)
			result[0][r_row_pos][r_col_pos] = result_tmp
	return result
#}}}

def my_matmul(x, y):
#{{{
	#x y 都是二维矩阵，只要行列的size就行
	x_row = len(x)
	x_col = len(x[0])
	y_row = len(y)
	y_col = len(y[0])

	#x_col 和y_row理论上应该一致，如果不一致这里得有error message，不过我这就不用了
	result = np.zeros([x_row, y_col])
	for x_row_pos in range (x_row):
		row_tmp = np.zeros(y_col)
		for y_col_pos in range (y_col):
			col_tmp = 0
			for x_col_pos in range (x_col):# x_col_pos也指y_row_pos
				col_tmp += x[x_row_pos][x_col_pos] * y[x_col_pos][y_col_pos]
			row_tmp [y_col_pos] = col_tmp
		result[x_row_pos] = row_tmp
	
	return result	
#}}}

def my_dropout(x, keep_prob):
#{{{
	x_row = len(x)
	x_col = len(x[0])
	result = np.zeros([x_row, x_col])
	
	for x_row_pos in range (x_row):
		row_tmp = np.zeros(x_col)
		for x_col_pos in range (x_col):
			row_tmp[x_col_pos] = x[x_row_pos][x_col_pos] / keep_prob
		result[x_row_pos] = row_tmp
	return result
#}}}

def my_reshape_flat (x, reshape_shape):
#{{{
	#现在我只能做成全平，但是输出的是[1, reshape_shape]的二维数组 
	result = [0] * reshape_shape
	x_shape = judge_size(x)
	x_0 = x_shape[0]
	x_1 = x_shape[1]
	x_2 = x_shape[2]
	x_3 = x_shape[3]
	for l0 in range (x_0):
		for l1 in range (x_1):
			for l2 in range (x_2):
				for l3 in range (x_3):
					result[l0 * x_3*x_1*x_2 + l1 * x_3*x_2 + l2 * x_3 + l3] = x[l0][l1][l2][l3]
	return [result]
#}}}

#=================================================
#TF
W1_shape = [5, 5, 1, 32]
W2_shape = [5, 5, 32, 64]
x_shape = [1, 28, 28, 1]
conv1_shape = [1,28,28,32] #也是h_conv1的shape
conv2_shape = [1,14,14,64] #也是h_conv2的shape
h_pool1_shape = [1, 14, 14, 32]
h_pool2_shape = [1, 7, 7, 64]
W_fc1_shape = [7* 7* 64, 1024]
W_fc2_shape = [1024, 10]
y_shape = [1, 10]

if TF == 1:
#{{{
	#全flow测试
	from tensorflow.examples.tutorials.mnist import input_data
	mnist = input_data.read_data_sets('MNIST_data', one_hot=True)
	#画图必须在一开始，要不出错
	#W_conv1 = weight_variable(W1_shape)
	#b_conv1 = bias_variable([32])

	#W_conv2 = weight_variable(W2_shape)
	#b_conv2 = bias_variable([64])
	
	#W_fc1 = weight_variable(W_fc1_shape)
	#b_fc1 = bias_variable([1024])

	#W_fc2 = weight_variable(W_fc2_shape)
	b_fc2 = bias_variable([10])

	#x = tf.placeholder(tf.float32, [None, 784])
	#x_image = tf.reshape(x, x_shape)

	#sess声明以后后面就只剩下run了
	#有一种办法是一边画图一边run，但是run里面必须有feed_dict, 要不然出错！
	sess = tf.InteractiveSession()
	sess.run(tf.global_variables_initializer())

	#以下部分只用来取标准值，代码只能执行一遍	
	
	#x
	#batch = mnist.train.next_batch(1)
	#result = sess.run (x_image, feed_dict={x: batch[0]})
	#W_write_4d(result, x_shape, "data/x_image.txt" )

	#W1	
	#result = sess.run (W_conv1)
	#W_write_4d(result, W1_shape, "data_orig/W_conv1.txt" )

	#conv1 result
	"""
	W_conv1 = W_read_4d(W1_shape, "data_orig/W_conv1.txt")	
	x_image = W_read_4d(x_shape, "data_orig/x_image.txt")	
	conv_result = conv2d(x_image, W_conv1)

	result = sess.run (conv_result)
	W_write_4d(result, conv1_shape, "data_orig/conv1.txt" )
	"""
	
	#h_conv1
	"""
	conv_result = W_read_4d (conv1_shape, "data_orig/conv1.txt")
	h_conv1 = tf.nn.relu(conv_result + b_conv1)
	
	result = sess.run (h_conv1)
	W_write_4d(result, conv1_shape, "data_orig/h_conv1.txt" )
	"""

	#pool1
	"""
	h_conv1 = W_read_4d (conv1_shape, "data_orig/h_conv1.txt")
	h_pool1 = max_pool_2x2(h_conv1)
	
	result = sess.run (h_pool1)
	W_write_4d(result, h_pool1_shape , "data_orig/h_pool1.txt" )
	"""

	#w2
	"""
	result = sess.run (W_conv2)
	W_write_4d(result, W2_shape, "data_orig/W_conv2.txt" )
	"""
	
	#conv2 result
	"""
	W_conv2 = W_read_4d(W2_shape, "data_orig/W_conv2.txt")	
	h_pool1 = W_read_4d(h_pool1_shape, "data_orig/h_pool1.txt")	
	conv_result = conv2d(h_pool1, W_conv2)

	result = sess.run (conv_result)
	W_write_4d(result, conv2_shape, "data_orig/conv2.txt" )
	"""
	
	#h_conv2
	"""
	conv_result = W_read_4d (conv2_shape, "data_orig/conv2.txt")
	h_conv2 = tf.nn.relu(conv_result + b_conv2)
	
	result = sess.run (h_conv2)
	W_write_4d(result, conv2_shape, "data_orig/h_conv2.txt" )
	"""

	#pool2
	"""
	h_conv2 = W_read_4d (conv2_shape, "data_orig/h_conv2.txt")
	h_pool2 = max_pool_2x2(h_conv2)
	
	result = sess.run (h_pool2)
	W_write_4d(result, h_pool2_shape , "data_orig/h_pool2.txt" )
	"""
	
	#W_fc1
	"""
	result = sess.run (W_fc1)
	W_write_2d(result, W_fc1_shape, "data_orig/W_fc1.txt" )
	"""

	#h_fc1
	"""	
	W_fc1 = W_read_2d (W_fc1_shape, "data_orig/W_fc1.txt")
	h_pool2 = W_read_4d (h_pool2_shape, "data_orig/h_pool2.txt")
	h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
	
	h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)
	result = sess.run(h_fc1)
	W_write_2d(result, [1, 1024], "data_orig/h_fc1.txt")
	"""	
	
	#keep_prob
	#keep_prob = 1.0	
	#keep_prob = 0.75	

	#dropout
	"""
	h_fc1 = W_read_2d ([1, 1024], "data_orig/h_fc1.txt")
	h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)
	result = sess.run(h_fc1_drop)
	W_write_2d(result, [1, 1024], "data_orig/h_fc1_drop.txt")
	"""

	#W_fc2
	"""
	result = sess.run (W_fc2)
	W_write_2d(result, W_fc2_shape, "data_orig/W_fc2.txt" )
	"""

	#y	
	W_fc2 = W_read_2d (W_fc2_shape, "data_orig/W_fc2.txt")
	h_fc1_drop = W_read_2d([1, 1024], "data_orig/h_fc1_drop.txt")
	y_conv = tf.matmul(h_fc1_drop, W_fc2) + b_fc2
	result = sess.run(y_conv)	
	W_write_2d(result, y_shape, "data_orig/y.txt" )

	sess.close()
#}}}

elif TF == 2:
#{{{
	#这里是小规模试验
	W1_shape = [2, 2, 1, 4]
	x_shape = [1, 5, 5, 1]
	#以下这几个shape是算出来的，不是我手动写的，但是写在这里看着玩
	conv1_shape = [1,5,5,4]
	h_pool1_shape = [1, 3, 3, 4]
	W_fc1_shape = [3*3*4, 4]	


	
	#所有的常量声明必须在一开头
	#但是运算可以在sess声明后去做
	#暂时这么认为

	#x = weight_variable(x_shape)
	#W_conv1 = weight_variable(W1_shape)
	#b_conv1 = bias_variable([4])

	#W_fc1 = weight_variable(W_fc1_shape)
	b_fc1 = bias_variable([4])

	sess = tf.InteractiveSession()
	sess.run(tf.global_variables_initializer())
	
	#x
	"""
	result = sess.run (x)
	W_write_4d(result, x_shape, "data_small/x_image.txt" )
	"""


	#W	
	"""
	result = sess.run (W_conv1)
	W_write_4d(result, W1_shape, "data_small/W_conv1.txt" )
	"""

	#conv result
	"""
	W_conv1 = W_read_4d(W1_shape, "data_small/W_conv1.txt")	
	x_image = W_read_4d(x_shape, "data_small/x_image.txt")	
	conv_result = conv2d(x_image, W_conv1)

	result = sess.run (conv_result)
	W_write_4d(result, conv1_shape, "data_small/conv1.txt" )
	"""
	
	#h_conv1
	"""
	conv_result = W_read_4d (conv1_shape, "data_small/conv1.txt")
	h_conv1 = tf.nn.relu(conv_result + b_conv1)
	
	result = sess.run (h_conv1)
	W_write_4d(result, conv1_shape, "data_small/h_conv1.txt" )
	"""
	
	#pool1
	"""
	h_conv1 = W_read_4d (conv1_shape, "data_small/h_conv1.txt")
	h_pool1 = max_pool_2x2(h_conv1)
	
	result = sess.run (h_pool1)
	W_write_4d(result, h_pool1_shape , "data_small/h_pool1.txt" )
	"""

	#W_fc1
	"""
	result = sess.run (W_fc1)
	W_write_2d(result, W_fc1_shape, "data_small/W_fc1.txt" )
	"""

	#h_fc1
	"""
	W_fc1 = W_read_2d (W_fc1_shape, "data_small/W_fc1.txt")

	h_pool1 = W_read_4d (h_pool1_shape, "data_small/h_pool1.txt")
	h_pool1_flat = tf.reshape(h_pool1, [-1, 3*3*4])
	
	h_fc1 = tf.nn.relu(tf.matmul(h_pool1_flat, W_fc1) + b_fc1)
	result = sess.run(h_fc1)
	W_write_2d(result, [1, 4], "data_small/h_fc1.txt")
	"""

	
	sess.close()
#}}}

elif TF == 3:
#{{{
	#小实验,调用TF的函数但是跑的data是小规模
	x_shape = [1, 5, 5, 1]
	W1_shape = [2, 2, 1, 4]
	conv1_shape = [1,5,5,4]
	h_pool1_shape = [1, 3, 3, 4]
	h_pool1_shape_2d = [1, 3* 3* 4]
	W_fc1_shape = [3*3*4, 4]	

	#conv
	"""
	W_conv1 = W_read_4d(W1_shape, "data_small/W_conv1.txt")	
	x_image = W_read_4d(x_shape, "data_small/x_image.txt")	
	result = my_conv2d (x_image, W_conv1)
	W_write_4d(result, conv1_shape, "data_small/conv1_my.txt" )
	"""
	
	#h_conv1 4 是小实验的out_size
	"""
	b_conv1 = [0.1] * 4
	conv_result = W_read_4d (conv1_shape, "data_small/conv1_my.txt")
	h_conv1 = my_relu_4d(conv_result + b_conv1)
	W_write_4d(h_conv1, conv1_shape, "data_small/h_conv1_my.txt" )
	"""
	
	#pool1
	"""
	h_conv1 = W_read_4d (conv1_shape, "data_small/h_conv1_my.txt")
	h_pool1 = my_pool_2x2(h_conv1)
	W_write_4d(h_pool1, h_pool1_shape , "data_small/h_pool1_my.txt" )
	"""

	#h_fc1
	"""
	W_fc1 = W_read_2d (W_fc1_shape, "data_small/W_fc1.txt")
	h_pool1 = W_read_4d (h_pool1_shape, "data_small/h_pool1.txt")
	h_pool1_flat = my_reshape_flat (h_pool1, h_pool1_shape_2d[1])
	matmul_result = my_matmul(h_pool1_flat, W_fc1)
	b_fc1 = [0.1] * 4
	h_fc1 = my_relu_2d(matmul_result + b_fc1)
	W_write_2d(h_fc1, [1, 4], "data_small/h_fc1_my.txt")
	"""
	
	

#}}}

elif TF == 4:
#{{{

	#大实验,但是用我自己的函数
	#conv 1
	"""
	W_conv1 = W_read_4d(W1_shape, "data_orig/W_conv1.txt")	
	x_image = W_read_4d(x_shape, "data_orig/x_image.txt")	
	result = my_conv2d (x_image, W_conv1)
	W_write_4d(result, conv1_shape, "data_orig/conv1_my.txt" )
	"""
	
	#h_conv1 
	"""
	b_conv1 = [0.1] * 32
	conv_result = W_read_4d (conv_shape, "data_orig/conv1_my.txt")
	h_conv1 = my_relu_4d(conv_result + b_conv1)
	W_write_4d(h_conv1, conv1_shape, "data_orig/h_conv1_my.txt" )
	"""
	
	#pool1
	"""
	h_conv1 = W_read_4d (conv1_shape, "data_orig/h_conv1_my.txt")
	h_pool1 = my_pool_2x2(h_conv1)
	W_write_4d(h_pool1, h_pool1_shape , "data_orig/h_pool1_my.txt" )
	"""
	
	#conv2 
	"""
	W_conv2 = W_read_4d(W2_shape, "data_orig/W_conv2.txt")	
	h_pool1 = W_read_4d(h_pool1_shape, "data_orig/h_pool1_my.txt")	
	result = my_conv2d(h_pool1, W_conv2)
	W_write_4d(result, conv2_shape, "data_orig/conv2_my.txt" )
	"""
	
	#h_conv2
	"""
	b_conv2 = [0.1] * 64 
	conv_result = W_read_4d (conv2_shape, "data_orig/conv2_my.txt")
	h_conv2 = my_relu_4d(conv_result + b_conv2)
	W_write_4d(h_conv2, conv2_shape, "data_orig/h_conv2_my.txt" )
	"""

	#pool2
	"""
	h_conv2 = W_read_4d (conv2_shape, "data_orig/h_conv2_my.txt")
	h_pool2 = my_pool_2x2(h_conv2)
	W_write_4d(h_pool2, h_pool2_shape , "data_orig/h_pool2_my.txt" )
	"""

	#h_fc1
	"""
	W_fc1 = W_read_2d (W_fc1_shape, "data_orig/W_fc1.txt")
	h_pool2 = W_read_4d (h_pool2_shape, "data_orig/h_pool2.txt")
	h_pool2_flat = my_reshape_flat(h_pool2, 7*7*64)
	
	matmul_result = my_matmul(h_pool2_flat, W_fc1)
	b_fc1 = [0.1] * 1024
	
	h_fc1 = my_relu_2d(matmul_result + b_fc1)
	W_write_2d(h_fc1, [1, 1024], "data_orig/h_fc1_my.txt")
	"""
	
	#dropout
	keep_prob = 1.0	
	h_fc1 = W_read_2d ([1, 1024], "data_orig/h_fc1_my.txt")
	result = my_dropout(h_fc1, keep_prob)	
	W_write_2d(result, [1, 1024], "data_orig/h_fc1_drop_my.txt")

#}}}

else:
	print ("compare")
	result = two_file_compare ("data_orig/h_fc1_my.txt", "data_orig/h_fc1.txt", [1, 1, 1, 1024])
	print (result)
	#h_fc1的size是1×1024，如果compare，要用size为[1,1,1,1024]





