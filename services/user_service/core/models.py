from django.db import models
from PIL import Image
from django.utils.text import slugify
from django.core.files import File
from io import BytesIO

class MyBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True, null=True)

    class Meta:
        abstract = True


def make_thumbnail(image, size=(140, 140)):
    """Makes thumbnails of given size from given image"""

    im = Image.open(image)

    im.convert('RGB')  # convert mode

    im.thumbnail(size)  # resize image

    thumb_io = BytesIO()  # create a BytesIO object
    im.save(thumb_io, 'png', quality=100)
    file_name = image.name.split('/')[-1]  # Extract the file name from the path
    print(file_name)
    thumb_file_name, file_extension = file_name.rsplit('.', 1)
    print(thumb_file_name)

    thumbnail = File(thumb_io,
                     name=thumb_file_name + "_thumbnail." + file_extension)
    return thumbnail


class UploadFile(MyBaseModel):
    file = models.FileField(null=True, blank=True)
    thumbnail_file = models.ImageField(null=True, blank=True)
    file_tags = models.CharField(max_length=128, null=True, blank=True)
    file_url = models.CharField(max_length=128, null=True, blank=True)
    file_name = models.CharField(max_length=128, null=True, blank=True)
    bucket_name = models.CharField(max_length=128, default="chat-bucket")

    def __str__(self):
        if self.file_tags:
            return str(self.file_tags)
        if self.file_name:
            return str(self.file_name)
        else:
            return "Nothing to"
        # f"Tags: {self.file_tags or 'None'}, Name: {self.file_name or 'None'}"

    def save(self, *args, **kwargs):
        # Check the file extension
        file_extension = self.file.name.split('.')[-1].lower()

        # If the file extension is SVG, do not create a thumbnail
        if file_extension == 'svg':
            self.thumbnail_file = self.file  # Assign the original SVG file as thumbnail
        else:
            # For other file types, create a thumbnail
            thumbnail = make_thumbnail(self.file, size=(300, 300))
            self.thumbnail_file = thumbnail
        super().save(*args, **kwargs)



