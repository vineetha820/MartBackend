"""Switch relations to custom users without importing legacy admin accounts."""
from django.db import migrations


def use_custom_users(apps, schema_editor):
    connection = schema_editor.connection
    alias = connection.alias
    if 'auth_user' not in connection.introspection.table_names():
        return
    LegacyUser = apps.get_model('auth', 'User')
    for app, model_name, field_name in (
        ('Products', 'Product', 'created_by'), ('admin', 'LogEntry', 'user'),
    ):
        model = apps.get_model(app, model_name)
        field = model._meta.get_field(field_name)
        with connection.cursor() as cursor:
            constraints = connection.introspection.get_constraints(cursor, model._meta.db_table)
        legacy_fk = any(
            item.get('foreign_key') == ('auth_user', 'id') and field.column in item['columns']
            for item in constraints.values()
        )
        if not legacy_fk:
            continue
        # Preserve historical attribution separately: legacy IDs must never be
        # interpreted as custom user IDs, even when their numbers coincide.
        with connection.cursor() as cursor:
            if app == 'admin':
                cursor.execute('CREATE TABLE legacy_django_admin_log AS SELECT * FROM django_admin_log')
                cursor.execute('DELETE FROM django_admin_log')
            else:
                cursor.execute('CREATE TABLE legacy_product_creators AS SELECT id, created_by_id FROM Products_product WHERE created_by_id IS NOT NULL')
                cursor.execute('UPDATE Products_product SET created_by_id = NULL WHERE created_by_id IS NOT NULL')
        old_field = field.clone()
        old_field.set_attributes_from_name(field.name)
        old_field.model = model
        old_field.remote_field.model = LegacyUser
        schema_editor.alter_field(model, old_field, field)
    # Old session IDs identify users from the previous authentication table.
    apps.get_model('sessions', 'Session').objects.using(alias).all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0002_alter_user_options_alter_user_managers_and_more'),
        ('Products', '0002_product_created_by'),
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('sessions', '0001_initial'),
    ]
    operations = [migrations.RunPython(use_custom_users)]
