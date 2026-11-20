from django.db import migrations, models


def copy_fk_to_m2m(apps, schema_editor):
    Service = apps.get_model("catalog", "Service")
    for service in Service.objects.prefetch_related("categories").all():
        if service.category_id:
            service.categories.add(service.category_id)


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_service_is_price_variable_alter_service_price"),
    ]

    operations = [
        # 1. Add M2M with a temporary reverse name to avoid clash with the FK
        migrations.AddField(
            model_name="service",
            name="categories",
            field=models.ManyToManyField(
                blank=True,
                related_name="services_new",
                to="catalog.category",
            ),
        ),
        # 2. Copy existing FK values into the M2M table
        migrations.RunPython(copy_fk_to_m2m, migrations.RunPython.noop),
        # 3. Drop the old DB index that referenced the FK column
        migrations.RemoveIndex(
            model_name="service",
            name="catalog_ser_categor_657b62_idx",
        ),
        # 4. Remove the FK field
        migrations.RemoveField(
            model_name="service",
            name="category",
        ),
        # 5. Give the M2M its permanent related_name
        migrations.AlterField(
            model_name="service",
            name="categories",
            field=models.ManyToManyField(
                blank=True,
                related_name="services",
                to="catalog.category",
            ),
        ),
    ]