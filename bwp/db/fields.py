# -*- coding: utf-8 -*-
#
#  bwp/db/fields.py
#
#  Copyright 2012 Grigoriy Kramarenko <root@rosix.ru>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
import os
import json
import six
from PIL import Image
from PIL.ExifTags import TAGS

from django.db.models import TextField
from django.db.models.fields.files import ImageField, ImageFieldFile
from django.forms.widgets import Textarea
from django.template.defaultfilters import slugify

from quickapi.http import JSONEncoder

from bwp.conf import settings

try:
    from unidecode import unidecode
    use_unidecode = True
except:
    use_unidecode = False


try:
    from tinymce.models import HTMLField  # NOQA
except ImportError:
    from django.db.models.fields import TextField as HTMLField  # NOQA


class JSONWidget(Textarea):
    """ Prettify dumps of all non-string JSON data. """
    def render(self, name, value, attrs=None):
        if not isinstance(value, six.string_types) and value is not None:
            value = json.dumps(value, indent=4, sort_keys=True)
        return super(JSONWidget, self).render(name, value, attrs)


class JSONField(TextField):
    form_class = JSONWidget

    def contribute_to_class(self, cls, name):
        super(JSONField, self).contribute_to_class(cls, name)

        def get_json(model):
            return self.get_db_prep_value(getattr(model, self.attname))
        setattr(cls, 'get_%s_json' % self.name, get_json)

        def set_json(model, json):
            setattr(model, self.attname, self.to_python(json))
        setattr(cls, 'set_%s_json' % self.name, set_json)

    def formfield(self, **kwargs):
        defaults = {'widget': Textarea}
        defaults.update(kwargs)
        return super(JSONField, self).formfield(**defaults)

    def from_db_value(self, value, expression, connection, context):
        """
        When the data is loaded from the database, including in
        aggregates and values() calls.
        """
        return self.to_python(value)

    def get_db_prep_save(self, value, connection, **kwargs):
        """Convert our JSON object to a string before we save"""

        if value == "":
            return None

        if isinstance(value, (list, dict)):
            value = json.dumps(
                value, cls=JSONEncoder, ensure_ascii=False, indent=4
            )
            try:
                value = value.encode('utf-8')
            except:
                pass

        return super(JSONField, self).get_db_prep_save(
            value, connection=connection, **kwargs
        )

    def to_python(self, value, **kwargs):
        """Convert our string value to JSON after we load it from the DB"""

        if value == "":
            return None

        if not isinstance(value, six.string_types):
            return value

        try:
            return json.loads(value, encoding=settings.DEFAULT_CHARSET)
        except ValueError:
            # If string could not parse as JSON it's means that it's Python
            # string saved to JSONField.
            return value

    def _get_val_from_obj(self, obj):
        if obj is not None:
            value = getattr(obj, self.attname)
            return self.get_db_prep_save(value, connection=None)
        else:
            return self.get_db_prep_save(self.get_default(), connection=None)


def _add_thumb(s):
    """ Изменяет строку (имя файла или URL), содержащую имя файла
        изображения, добавляя '.thumb' в конец и приводя к слагу,
        если это возможно.
    """
    # Что-то не так с сохранением путей
    s = [x for x in os.path.split(s)]  # from tuple to list
    name, ext = os.path.splitext(s[-1])
    if use_unidecode:
        name = unidecode(unicode(name))
        name = slugify(name)
    s[-1] = '.'.join([name.lower(), ext.lower()])
    s = '.'.join(s)
    return '%s.thumb' % s


def maxSize(image, maxSize, method=3):
    if (image.size[0] > maxSize[0] and image.size[0] > maxSize[1] or
            image.size[1] > maxSize[0] and image.size[1] > maxSize[1]):
        imAspect = float(image.size[0]) / float(image.size[1])
        outAspect = float(maxSize[0]) / float(maxSize[1])
        if imAspect >= outAspect:
            return image.resize(
                (maxSize[0], int((float(maxSize[0]) / imAspect) + 0.5)),
                method,
            )
        else:
            return image.resize(
                (int((float(maxSize[1]) * imAspect) + 0.5), maxSize[1]),
                method,
            )
    else:
        return image


def get_square_image(img):
    width, height = img.size
    if width > height:
        delta = width - height
        left = int(delta / 2)
        upper = 0
        right = height + left
        lower = height
    else:
        delta = height - width
        left = 0
        upper = int(delta / 2)
        right = width
        lower = width + upper
    img = img.crop((left, upper, right, lower))
    return img


class ThumbnailImageFieldFile(ImageFieldFile):
    @property
    def thumb_path(self):
        return _add_thumb(self.path)

    @property
    def thumb_url(self):
        end = self.thumb_path.replace(
            os.path.abspath(settings.MEDIA_ROOT),
            '',
        ).lstrip('/')
        return settings.MEDIA_URL + end

    @property
    def url(self):
        end = self.path.replace(
            os.path.abspath(settings.MEDIA_ROOT),
            '',
        ).lstrip('/')
        return settings.MEDIA_URL + end

    def save(self, name, content, save=True):
        super(ThumbnailImageFieldFile, self).save(name, content, save)

        img = Image.open(self.path)
        try:
            exif = img._getexif()
        except:
            exif = None
        if exif is not None:
            for tag, value in exif.items():
                decoded = TAGS.get(tag, tag)
                if decoded == 'Orientation':
                    if value == 3:
                        img = img.rotate(180)
                    if value == 6:
                        img = img.rotate(270)
                    if value == 8:
                        img = img.rotate(90)
                    break
        if self.field.square:
            img = get_square_image(img)
        if self.field.resize:
            img = maxSize(
                img,
                (self.field.max_width, self.field.max_height),
                Image.ANTIALIAS,
            )
            img.save(self.path)
        if self.field.thumb_square and not self.field.square:
            img = get_square_image(img)
        img.thumbnail(
            (self.field.thumb_width, self.field.thumb_height),
            Image.ANTIALIAS,
        )
        img.save(self.thumb_path, 'JPEG')


class ThumbnailImageField(ImageField):
    """ Ведёт себя также как и класс ImageField, но дополнительно
        сохраняет миниатюру изображения и предоставляет методы
        get_FIELD_thumb_url() и get_FIELD_thumb_filename().

        Принимает два дополнительных, необязательных аргумента:
        thumb_width и thumb_height, каждый из которых имеет значение
        по умолчанию 128 пикселей. При изсенении размеров, отношение
        ширины к высоте сохраняется, обеспечивая пропорциональность
        изображения.

        Также см. Image.thumbnail() библиотеки PIL.
    """
    attr_class = ThumbnailImageFieldFile

    def __init__(self, thumb_width=256, thumb_height=256,
                 max_width=1024, max_height=1024, resize=True,
                 square=False, thumb_square=False,
                 *args, **kwargs):

        self.resize = resize
        self.square = square
        self.thumb_square = thumb_square
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height
        self.max_width = max_width
        self.max_height = max_height
        super(ThumbnailImageField, self).__init__(*args, **kwargs)
