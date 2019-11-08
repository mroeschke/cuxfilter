import pytest

from cuXfilter.assets.numba_kernels.gpu_histogram import *
import numpy as np
from numba import cuda

from cuXfilter.charts.core.core_chart import BaseChart

@pytest.mark.parametrize('x, min_max_array_pre_calc, min_max_array_final', [
    (cuda.to_device(np.array([1, 5, 10, 15, 25,27, 30])),
        np.array([ 9.223372e+18, -9.223372e+18], dtype=np.float32),
        np.array([ 1., 30.], dtype=np.float32)),
    (cuda.to_device(np.array([-1, 0, 2, -10])),
        np.array([ 9.223372e+18, -9.223372e+18], dtype=np.float32),
        np.array([ -10., 2.], dtype=np.float32))
])
def test_min_max(x, min_max_array_pre_calc, min_max_array_final):
    min_max_array = cuda.to_device(np.array([dtype_min_max(x.dtype)[1],dtype_min_max(x.dtype)[0]] , dtype=np.float32))
    assert np.array_equal(min_max_array.copy_to_host(),min_max_array_pre_calc)

    min_max[64, 64](x, min_max_array)

    assert np.array_equal(min_max_array.copy_to_host(), min_max_array_final)

def test_histogram():
    x = cuda.to_device(np.array([1, 5, 10, 15, 25,27, 30,
                       23, 22, 35, 39, 99, 109, 109, 104, 11, 23]*50))
    min_max_array = cuda.to_device(np.array([dtype_min_max(x.dtype)[1],
                    dtype_min_max(x.dtype)[0]] , dtype=np.float32))
    min_max[64, 64](x, min_max_array)
    bins = 8
    hist_out = cuda.to_device(np.zeros(shape=(bins,), dtype=np.float64))

    assert np.array_equal(hist_out.copy_to_host(), np.array([0., 0., 0., 0., 0., 0., 0., 0.]))

    histogram[64,64](x, min_max_array, hist_out)

    assert np.array_equal(hist_out.copy_to_host(), np.array([200., 300., 150.,   0.,   0.,   0.,   0., 200.]))

@pytest.mark.parametrize('dtype, result', [
    (np.int64, (-9223372036854775808, 9223372036854775807)),
    (np.int32, (-2147483648, 2147483647)),
    (np.int16, (-32768, 32767)),
    (np.int8, (-128, 127)),
    (np.int, (-9223372036854775808, 9223372036854775807)),
    (np.float64, (-1.7976931348623157e+308, 1.7976931348623157e+308)),
    (np.float32, (np.float32(-3.4028235e+38), np.float32(3.4028235e+38))),
    (np.float16, (np.float16(-65500.0), np.float16(65500.0))),
    (np.float, (-1.7976931348623157e+308, 1.7976931348623157e+308))
])
def test_dtype_min_max(dtype, result):
    assert dtype_min_max(dtype) == result

def test_get_bin_edges():
    x = cuda.to_device(np.array([1, 5, 10, 15, 25,27, 30, 23, 22, 35, 39, 99, 109, 109, 104, 11, 23]*50))
    bins = 8
    bin_edges = cuda.to_device(np.zeros(shape=(bins,), dtype=np.float64))
    min_max_array = cuda.to_device(np.array([dtype_min_max(x.dtype)[1],dtype_min_max(x.dtype)[0]] , dtype=np.float32))
    
    get_bin_edges[64,64](min_max_array,bin_edges)

    assert np.array_equal(bin_edges.copy_to_host(),
                          np.array([9.22337204e+18,  6.91752903e+18,  4.61168602e+18,  2.30584301e+18,
                                    0.00000000e+00, -2.30584301e+18, -4.61168602e+18, -9.22337204e+18], dtype=np.float32))

@pytest.mark.parametrize( 'stride, test_arr, result', [
    (2, cuda.to_device(np.array([10.,  8.,  6.,  4.,  2., 10.,  8.,  6.,  4.,  2., 10.,  8.,  6.])),
    np.array([4., 3., 2., 1., 0., 4., 3., 2., 1., 0., 4., 3., 2.])),
    (1, cuda.to_device(np.array([10.,  8.,  6.,  4.,  2., 10.,  8.,  6.,  4.,  2., 10.,  8.,  6., 0.])),
    cuda.to_device(np.array([10.,  8.,  6.,  4.,  2., 10.,  8.,  6.,  4.,  2., 10.,  8.,  6., 0.])))
])
def test_calc_binwise_reduced_column(stride, test_arr, result):
    min, max = test_arr.copy_to_host().min(), test_arr.copy_to_host().max()
    test_res = get_binwise_reduced_column(test_arr, stride, cuda.to_device(np.asarray([min,max]))).copy_to_host()

    assert np.array_equal(test_res,result)

def test_calc_value_counts():
    x = cuda.to_device(np.array([1, 5, 10, 15, 25,27, 30, 23, 22, 35, 39, 99, 109, 109, 104, 11, 23]*50))
    bins = 8

    result = calc_value_counts(x, bins)

    assert np.array_equal(result[0], np.array([  1. ,  14.5,  28. ,  41.5,  55. ,  68.5,  82. , 109. ]))
    assert np.array_equal(result[1], np.array([200, 300, 150,   0,   0,   0,   0, 200]))

@pytest.mark.parametrize('aggregate_fn, result', [
    ('count', np.array([[0., 1., 2., 3., 4.],
       [5., 5., 5., 5., 5.]])),
    ('mean', np.array([[ 0.,  1.,  2.,  3.,  4.],
       [10.,  8.,  6.,  4.,  2.]]))
])
def test_calc_groupby(aggregate_fn, result):
    df = cudf.DataFrame({
                    'key': [float(i) for i in range(5)]*5,
                    'val': [float(i*2) for i in range(5, 0, -1)]*5
                    })
    bc = BaseChart()
    bc.x = 'key'
    bc.y = 'val'
    bc.stride = 1.0
    bc.max_value = 4.0
    bc.min_value = 0.0
    bc.data_points = 25

    bc.aggregate_fn = aggregate_fn

    assert np.array_equal(calc_groupby(bc, df), result)

def test_aggregated_column_unique():
    df = cudf.DataFrame({
                    'key': cuda.to_device(np.array([1, 5, 10, 15, 25,27, 30, 23, 22, 35, 39, 99, 109, 109, 104, 11, 23]*50)),
                    })
    bc = BaseChart()
    bc.x = 'key'
    bc.stride = 1.0
    bc.max_value = df['key'].max()
    bc.min_value = df['key'].min()

    assert np.array_equal(aggregated_column_unique(bc, df), np.array([0, 4, 9, 10, 14, 21, 22, 24, 26, 29, 34, 38, 98, 103, 108]))