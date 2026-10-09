from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class SubjectOwnershipMigrationTests(TransactionTestCase):
    def test_existing_subject_keeps_null_owner(self):
        executor = MigrationExecutor(connection)
        latest = executor.loader.graph.leaf_nodes()
        old_target = [("subjects", "0001_initial")]
        try:
            executor.migrate(old_target)
            old_apps = executor.loader.project_state(old_target).apps
            subject = old_apps.get_model("subjects", "Subject").objects.create(name="Legacy")
            executor = MigrationExecutor(connection)
            target = [("subjects", "0002_subject_owner_note")]
            executor.migrate(target)
            new_apps = executor.loader.project_state(target).apps
            migrated = new_apps.get_model("subjects", "Subject").objects.get(pk=subject.pk)
            self.assertEqual(migrated.name, "Legacy")
            self.assertIsNone(migrated.owner_id)
        finally:
            MigrationExecutor(connection).migrate(latest)
