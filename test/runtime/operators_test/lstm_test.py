import numpy as np
from chainer import Variable
from chainer.functions.activation.lstm import lstm
from chainer.functions.connection.linear import linear

from test.util import generate_kernel_test_case
from webdnn.graph.graph import Graph
from webdnn.graph.operators.lstm import LSTM
from webdnn.graph.order import OrderNTC, OrderCN, OrderC, OrderNC
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


def _convert_to_chainer_order(x):
    # NOTE:
    # In WebDNN, W_i, W_h, and b contains weights about input gate(v_i), forget gate(v_f) activated value(v_a), and output gate(v_o)
    # based on this order (v_i, v_f, v_a, v_o). However in chainer, they are packed as different order (v_a, v_i, v_f, and v_o).
    # Also, webdnn packs this weights as an tensor whose shape is (C1 or C2, 4, C2), but chainer packs as (C1 or C2, 4, C2)
    return x.reshape(x.shape[0], 4, x.shape[1] // 4).swapaxes(1, 2)[:, :, [2, 0, 1, 3]].reshape(x.shape)


def test_t_is_1():
    N = 1
    T = 1
    C1 = 128
    C2 = 64
    vx = np.random.normal(size=(N, T, C1)).astype(np.float32)
    vw_input = np.random.normal(size=(C1, C2 * 4)).astype(np.float32)
    vw_hidden = np.random.normal(size=(C2, C2 * 4)).astype(np.float32)
    vb = np.random.normal(size=(C2 * 4,)).astype(np.float32)
    vc_in = np.zeros((N, C2)).astype(np.float32)
    vc_out = vc_in.copy()
    vh = np.zeros((N, C2)).astype(np.float32)

    vw_input_c = _convert_to_chainer_order(vw_input)
    vw_hidden_c = _convert_to_chainer_order(vw_hidden)
    vb_c = _convert_to_chainer_order(vb[None, :])

    for i in range(T):
        vc_out, vh = lstm(vc_out, linear(vx[:, i, :], vw_input_c.T) + linear(vh, vw_hidden_c.T) + vb_c)

    vh = vh.data

    x = Variable(vx.shape, order=OrderNTC)
    c_in = ConstantVariable(vc_in, order=OrderNC)
    w_input = ConstantVariable(vw_input, order=OrderCN)
    w_hidden = ConstantVariable(vw_hidden, order=OrderCN)
    b = ConstantVariable(vb, order=OrderC)
    y, c_out = LSTM(None)(x, c_in, w_input, w_hidden, b)

    generate_kernel_test_case(
        description=f"LSTM t=10",
        backend=["webassembly", "webgpu"],
        graph=Graph([x], [y, c_out]),
        inputs={x: vx},
        expected={y: vh, c_out: vc_out}
    )


def test_t_is_10():
    N = 1
    T = 10
    C1 = 128
    C2 = 64
    vx = np.random.normal(size=(N, T, C1)).astype(np.float32)
    vw_input = np.random.normal(size=(C1, C2 * 4)).astype(np.float32)
    vw_hidden = np.random.normal(size=(C2, C2 * 4)).astype(np.float32)
    vb = np.random.normal(size=(C2 * 4,)).astype(np.float32)
    vc_in = np.zeros((N, C2)).astype(np.float32)
    vc_out = vc_in.copy()
    vh = np.zeros((N, C2)).astype(np.float32)

    vw_input_c = _convert_to_chainer_order(vw_input)
    vw_hidden_c = _convert_to_chainer_order(vw_hidden)
    vb_c = _convert_to_chainer_order(vb[None, :])

    for i in range(T):
        vc_out, vh = lstm(vc_out, linear(vx[:, i, :], vw_input_c.T) + linear(vh, vw_hidden_c.T) + vb_c)

    vh = vh.data

    x = Variable(vx.shape, order=OrderNTC)
    c_in = ConstantVariable(vc_in, order=OrderNC)
    w_input = ConstantVariable(vw_input, order=OrderCN)
    w_hidden = ConstantVariable(vw_hidden, order=OrderCN)
    b = ConstantVariable(vb, order=OrderC)
    y, c_out = LSTM(None)(x, c_in, w_input, w_hidden, b)

    generate_kernel_test_case(
        description=f"LSTM t=10",
        backend=["webassembly", "webgpu"],
        graph=Graph([x], [y, c_out]),
        inputs={x: vx},
        expected={y: vh, c_out: vc_out}
    )
