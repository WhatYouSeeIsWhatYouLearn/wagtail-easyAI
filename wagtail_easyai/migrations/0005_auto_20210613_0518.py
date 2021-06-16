# Generated by Django 3.2.4 on 2021-06-13 05:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtail_easyai', '0004_abstractdata'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='csvdata',
            name='collection',
        ),
        migrations.RemoveField(
            model_name='csvdata',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='csvdata',
            name='file',
        ),
        migrations.RemoveField(
            model_name='csvdata',
            name='file_hash',
        ),
        migrations.RemoveField(
            model_name='csvdata',
            name='file_size',
        ),
        migrations.RemoveField(
            model_name='csvdata',
            name='id',
        ),
        migrations.RemoveField(
            model_name='csvdata',
            name='tags',
        ),
        migrations.RemoveField(
            model_name='csvdata',
            name='title',
        ),
        migrations.RemoveField(
            model_name='csvdata',
            name='uploaded_by_user',
        ),
        migrations.AddField(
            model_name='csvdata',
            name='abstractdata_ptr',
            field=models.OneToOneField(auto_created=True, default=None, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtail_easyai.abstractdata'),
            preserve_default=False,
        ),
    ]
