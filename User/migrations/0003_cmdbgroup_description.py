# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0002_auto_20180322_2207'),
    ]

    operations = [
        migrations.AddField(
            model_name='cmdbgroup',
            name='description',
            field=models.TextField(default=2, verbose_name=b'\xe7\xbb\x84\xe6\x8f\x8f\xe8\xbf\xb0'),
            preserve_default=False,
        ),
    ]
