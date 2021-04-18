from wagtail.core import hooks
from wagtail.contrib.modeladmin.options import modeladmin_register

from wagtail_easyai.admin import MLGroup


# registers the MLProject and MLPipeline menu
modeladmin_register(MLGroup)
