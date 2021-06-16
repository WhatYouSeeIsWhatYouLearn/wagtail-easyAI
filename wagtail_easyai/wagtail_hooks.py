from wagtail.core import hooks
from wagtail.contrib.modeladmin.options import modeladmin_register

from wagtail_easyai.admin import MLGroup, MLDataGroup


# registers the MLData and MLWorkflow menus
modeladmin_register(MLGroup)
modeladmin_register(MLDataGroup)
