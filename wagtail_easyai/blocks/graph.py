from django.db import models
from django import forms

from wagtail.core import blocks

from wagtail_easyai.blocks.ml_blocks import MLProjectChooserBlock


class BaseChartBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=200)
    ml_project = MLProjectChooserBlock()
    

class BoxPlotChartBlock(BaseChartBlock):
    pass


class DoughnutChartBlock(BaseChartBlock):
    pass


class ScatterPlotChartBlock(BaseChartBlock):
    pass


class BarChartBlock(BaseChartBlock):
    pass


class LineChartBlock(BaseChartBlock):
    pass


class ROCCurveChartBlock(BaseChartBlock):
    pass


class ValidationCurveChartBlock(BaseChartBlock):
    pass
