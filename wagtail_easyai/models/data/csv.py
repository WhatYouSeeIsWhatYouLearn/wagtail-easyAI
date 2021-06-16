from itertools import islice
import io

from django.db import models
from django.utils.functional import cached_property
from django.core.exceptions import ValidationError

from wagtail.documents.blocks import DocumentChooserBlock
from wagtail_easyai.models.data.data import AbstractData

import pandas as pd

class CSVDataValidationError(ValidationError):
    ...


class CSVData(AbstractData):
    ...

    def clean(self):
        """
        Validates CSV file by checking extension and contents
        """
        self.clean_type("csv")

        # checks the first 100 lines for syntax
        try:
            df = pd.DataFrame(islice(self.file, 101))
            print(df)
        except (UnicodeDecodeError, AssertionError) as e:
            raise CSVDataValidationError("The CSV file is not valid")

# class CSVDataChooserBlock(DocumentChooserBlock):
#     ...

#     @cached_property
#     def target_model(self):
#         return CSVData 

#     def clean(self, value):
#         """
#         Validates CSV file by checking it is properly formed
#         """
#         # validates that this is a syntactically valid CSV file
#         try:
#             # loads the first 100 (or less) lines for validation
#             # print(dir(self.file))
#             # print(type(self.file))
#             with self.file.open("r") as csv_file:
#                 df = pd.read_csv(csv_file, nrows=100)
#         except (UnicodeDecodeError, AssertionError) as e:
#             raise CSVDataValidationError("The CSV file is not valid")

#         super().clean(value)
