from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("departments", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="department",
            options={"ordering": ["name"]},
        ),
    ]
