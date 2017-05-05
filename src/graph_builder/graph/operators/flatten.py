from typing import Dict

import numpy as np

from graph_builder.graph.axis import Axis
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.inplace import Inplace
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNC


# FIXME: improve documentation
class Flatten(Operator):
    """Flatten some axes into one axis.

    Args:
        name (str): Operator name.
        parameters (Dict[str, any]): Parameters.

    """

    # 入力変数の形を変形するレイヤー
    # データ内の特定の軸(複数)を特定の軸(現状、1つ)に射影
    # 入出力変数の形によっては、データそのものを転置する必要がある
    # NCHW -> NCなど

    attributes = {PostElementwise,
                  PostAxiswise,
                  Inplace}

    def __init__(self, name: str, parameters: Dict[str, any]):
        # in_axes: [Axis.H, Axis.W, Axis.C], out_axes: [Axis.C]
        # のとき、NHWC入力・NC出力ならデータを操作しないでaxis_order=NCの出力とする。
        # NCHW入力・NC出力なら、入力データをNHWCに並び替えたうえでaxis_order=NCの出力とする。

        assert "in_axes" in parameters
        assert "out_axes" in parameters

        # FIXME: 現状はこの組み合わせだけで十分

        assert set(parameters["in_axes"]) == {Axis.C, Axis.H, Axis.W}
        assert set(parameters["out_axes"]) == {Axis.C}

        super().__init__(name, parameters)

    def __call__(self, x: Variable):
        """
        Args:
            x (:class:`~graph_builder.graph.variable.Variable`): Input

        Returns:
            tuple of :class:`~graph_builder.graph.variable.Variable`: Output
        """
        out_axis_order = OrderNC  # FIXME: 決め打ちをしない

        reduction_size: int = np.prod([x.shape_dict[axis] for axis in self.parameters["in_axes"]])
        keep_size = x.shape_dict[Axis.N]
        y = Variable((keep_size, reduction_size), out_axis_order)
        self.append_input("x", x)
        self.append_output("y", y)

        return y,
