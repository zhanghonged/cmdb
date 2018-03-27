# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0003_cmdbgroup_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cmdbgroup',
            name='description',
            field=models.TextField(null=True, verbose_name=b'\xe7\xbb\x84\xe6\x8f\x8f\xe8\xbf\xb0', blank=True),
        ),
    ]
