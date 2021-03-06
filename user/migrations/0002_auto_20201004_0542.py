# Generated by Django 3.1.1 on 2020-10-04 05:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follow_from_user', to='user.user')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follow_to_user', to='user.user')),
            ],
            options={
                'db_table': 'follows',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='follower',
            field=models.ManyToManyField(through='user.Follow', to='user.User'),
        ),
    ]
