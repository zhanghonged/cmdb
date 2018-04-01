# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0004_auto_20180327_1754'),
    ]

    operations = [
        migrations.AddField(
            model_name='cmdbuser',
            name='islogin',
            field=models.IntegerField(null=True, verbose_name=b'\xe7\x99\xbb\xe5\xbd\x95\xe7\x8a\xb6\xe6\x80\x81', blank=True),
        ),
    ]
