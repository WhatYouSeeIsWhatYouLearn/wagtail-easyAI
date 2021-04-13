from django.db import models

from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField

from wagtail_automl.blocks import ml_blocks


class MLPipeline(models.Model):
    title = models.CharField(max_length=255)

    data_cleaning = StreamField((), null=True, blank=True)

    preprocessing = StreamField((
        ("knn_imputer", ml_blocks.KNNImputerBlock()),
        ), null=True, blank=True)

    training = StreamField((
        ("tpot_classifier", ml_blocks.TPOTClassifierBlock()),
        ), null=True)

    panels = (
            FieldPanel('title'),
            StreamFieldPanel("data_cleaning"),
            StreamFieldPanel("preprocessing"),
            StreamFieldPanel("training"),
            )

    def __str__(cls):
        return cls.title + f" ({cls.pk})"

    class Meta:
        verbose_name_plural = "Pipelines (Workflows)"
