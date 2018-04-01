# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0006_remove_cmdbuser_islogin'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_logs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=32, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7\xe5\x90\x8d')),
                ('action', models.CharField(max_length=32, verbose_name=b'\xe5\x8a\xa8\xe4\xbd\x9c')),
                ('action_time', models.DateTimeField(verbose_name=b'\xe6\x93\x8d\xe4\xbd\x9c\xe6\x97\xb6\xe9\x97\xb4')),
            ],
        ),
    ]
