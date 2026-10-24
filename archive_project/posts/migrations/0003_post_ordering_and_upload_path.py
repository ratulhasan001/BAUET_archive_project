import taggit.managers
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("posts", "0002_alter_post_title"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="comment",
            options={"ordering": ["created_on"]},
        ),
        migrations.AlterModelOptions(
            name="post",
            options={"ordering": ["-year", "-id"]},
        ),
        migrations.AlterField(
            model_name="post",
            name="content",
            field=models.TextField(verbose_name="Abstract"),
        ),
        migrations.AlterField(
            model_name="post",
            name="file",
            field=models.FileField(upload_to="uploads/"),
        ),
        migrations.AlterField(
            model_name="post",
            name="supervisors",
            field=models.ManyToManyField(blank=True, related_name="supers", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="post",
            name="tags",
            field=taggit.managers.TaggableManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="posts.CustomTaggedItem",
                to="posts.CustomTag",
                verbose_name="Tags",
            ),
        ),
    ]
