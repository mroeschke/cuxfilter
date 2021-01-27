import re
import numpy as np
import panel as pn

from .custom_react_template import ReactTemplate


def is_widget(obj):
    return "widget" in obj.chart_type or obj.chart_type == "datasize_indicator"


def compute_position(arr, i, pos, offset):
    x, y = (
        np.array(
            [
                np.where(arr == i + 1)[0][pos] + offset,
                np.where(arr == i + 1)[1][pos] + offset,
            ]
        )
        / np.array(arr.shape)
        * (6, 12)
    )
    return int(x), int(y)


class _LayoutBase:
    _layout: str
    _layout_array: list
    _num_charts_pat = re.compile("roots.chart")

    def generate_dashboard(self, title, charts, theme, layout_array=None):
        pn.config.sizing_mode = "stretch_both"
        self._layout_array = layout_array
        tmpl = ReactTemplate(title=title, theme=theme, compact="both")
        widgets = [x for x in charts.values() if is_widget(x)]
        tmpl = self._process_widgets(widgets, tmpl)
        self._apply_themes(charts, theme)
        plots = [x for x in charts.values() if not is_widget(x)]
        self._process_plots(plots, tmpl)
        return tmpl

    def _apply_themes(self, charts, theme):
        for chart in charts.values():
            if hasattr(chart, "apply_theme"):
                chart.apply_theme(theme)

    def _process_widgets(self, widgets_list, tmpl):
        for obj in widgets_list:
            obj.chart.width = 280
            obj.chart.sizing_mode = "scale_width"
            tmpl.sidebar.append(obj.view())
        return tmpl

    def _process_grid_matrix(self, plots, tmpl):
        arr = np.array(self._layout_array)
        if len(arr.shape) == 1:
            arr = np.array([arr])
        for i in range(arr.max()):
            if i < len(plots):
                x0, y0 = compute_position(arr, i, 0, 0)
                x1, y1 = compute_position(arr, i, -1, 1)
                tmpl.main[x0:x1, y0:y1] = plots[i].view()

    def _process_plots(self, plots, tmpl):
        raise NotImplementedError()


class Layout0(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 0
        [1]
        """
        if not self._layout_array:
            self._layout_array = [1]
        self._process_grid_matrix(plots, tmpl)


class Layout1(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 1

        [1]
        [1]
        [2]
        """
        if not self._layout_array:
            self._layout_array = [[1], [1], [2]]
        self._process_grid_matrix(plots, tmpl)


class Layout2(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 2

        [1 2]
        """
        if not self._layout_array:
            self._layout_array = [1, 2]
        self._process_grid_matrix(plots, tmpl)


class Layout3(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 3

        [1   2]
        [1   3]
        """
        if not self._layout_array:
            self._layout_array = [[1, 2], [1, 3]]
        self._process_grid_matrix(plots, tmpl)


class Layout4(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 4

        [1 2 3]
        """
        if not self._layout_array:
            self._layout_array = [1, 2, 3]
        self._process_grid_matrix(plots, tmpl)


class Layout5(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 5

        [1   1]
        [2   3]
        """
        if not self._layout_array:
            self._layout_array = [[1, 1], [2, 3]]
        self._process_grid_matrix(plots, tmpl)


class Layout6(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 6

        [1  2]
        [3  4]
        """
        if not self._layout_array:
            self._layout_array = [[1, 2], [3, 4]]
        self._process_grid_matrix(plots, tmpl)


class Layout7(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 7

        [1  1  1]
        [2  3  4]
        """
        if not self._layout_array:
            self._layout_array = [[1, 1, 1], [2, 3, 4]]
        self._process_grid_matrix(plots, tmpl)


class Layout8(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 8

        [     1     ]
        [2  3   4  5]
        """
        if not self._layout_array:
            self._layout_array = [[1, 1, 1, 1], [2, 3, 4, 5]]
        self._process_grid_matrix(plots, tmpl)


class Layout9(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 9

        [1  1  2]
        [1  1  3]
        [4  5  6]
        """
        if not self._layout_array:
            self._layout_array = [[1, 1, 2], [1, 1, 3], [4, 5, 6]]
        self._process_grid_matrix(plots, tmpl)


class Layout10(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 10

        [1  2  3]
        [4  5  6]
        """
        if not self._layout_array:
            self._layout_array = [[1, 2, 3], [4, 5, 6]]
        self._process_grid_matrix(plots, tmpl)


class Layout11(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 11

        [1   1   2   2]
        [3   4   5   6]
        """
        if not self._layout_array:
            self._layout_array = [[1, 1, 2, 2], [3, 4, 5, 6]]
        self._process_grid_matrix(plots, tmpl)


class Layout12(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 12

        [1  2  3]
        [4  5  6]
        [7  8  9]
        """
        if not self._layout_array:
            self._layout_array = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        self._process_grid_matrix(plots, tmpl)
