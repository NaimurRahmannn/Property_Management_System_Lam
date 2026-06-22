import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property_app', '0007_alter_location_embedding_alter_property_embedding'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='amenities',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=100),
                blank=True,
                default=list,
                size=None,
            ),
        ),
    ]
