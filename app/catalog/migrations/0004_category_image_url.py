from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_service_categories"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="image",
            field=models.ImageField(blank=True, upload_to="categories/"),
        ),
        migrations.AddField(
            model_name="category",
            name="image_url",
            field=models.URLField(blank=True),
        ),
    ]