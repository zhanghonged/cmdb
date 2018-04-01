# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0005_cmdbuser_islogin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cmdbuser',
            name='islogin',
        ),
    ]
