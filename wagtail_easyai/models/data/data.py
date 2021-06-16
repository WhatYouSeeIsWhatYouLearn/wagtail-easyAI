from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from wagtail.contrib import settings
from wagtail.documents.models import AbstractDocument

import magic

class AbstractData(AbstractDocument):
    ...

    def clean_type(self, file_extension):
        """
        Validates file by checking it has the right extension
        """
        # validates it's a correct extension while respecting the user permitted extensions
        allowed_extensions = getattr(settings, "WAGTAILDOCS_EXTENSIONS", [file_extension])
        validate = FileExtensionValidator([file_extension] if file_extension in allowed_extensions else [])
        validate(self.file)

        # gets the file contents from uploaded file (only need first bit of data)
        file_contents = self.file.read(2048)
        self.file.seek(0)

        # uses the magic library to validate the headers
        # filetype = magic.from_buffer(file_contents)
        if not file_extension in file_extension:
            raise ValidationError(f"File is not {file_extension}.")

        # returns file contents as most functions will then validate the
        # contents themselves instead of just extension
        # return file_contents
