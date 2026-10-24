from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("posts", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="post",
            options={"ordering": ["-year", "-id"]},
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
    ]
