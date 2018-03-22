# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations
from User.views import getmd5

def forwards_func(apps, schema_editor):
    Person = apps.get_model("User", "CMDBUser")
    db_alias = schema_editor.connection.alias
    Person.objects.using(db_alias).bulk_create([
        Person(username='admin', password=getmd5('123.com'))
    ])

class Migration(migrations.Migration):

    dependencies = [
        ('User', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards_func)
    ]
