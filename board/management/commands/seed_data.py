from django.core.management.base import BaseCommand
from django.utils import timezone

from board.models import (
    Role,
    Status,
    User,
    Team,
    TeamMember,
    Project,
    ProjectTeam,
    Task,
    TaskAssignee,
)


class Command(BaseCommand):
    help = "Seed database with demo data for development"

    def handle(self, *args, **kawrgs):

        # Create Admin Role
        admin_role, _ = Role.objects.get_or_create(
            name="ADMIN", defaults={"description": "Administrator"}
        )

        # Create Apprentice Role
        apprentice_role, _ = Role.objects.get_or_create(
            name="APPRENTICE", defaults={"description": "Apprentice"}
        )

        # Create Admin User
        admin_user, created_admin = User.objects.get_or_create(
            email="admin@example.com",
            defaults={
                "first_name": "Admin",
                "last_name": "User",
                "role": admin_role,
                "is_staff": True,
                "is_active": True,
                "created_at": timezone.now(),
            },
        )

        if created_admin or not admin_user.has_usable_password():
            admin_user.set_password("password123")
            admin_user.save()

        # Create Apprentice User
        apprentice_user, created_appr = User.objects.get_or_create(
            email="apprentice@example.com",
            defaults={
                "first_name": "Istafa",
                "last_name": "Marshall",
                "role": apprentice_role,
                "is_active": True,
                "created_at": timezone.now(),
            },
        )

        if apprentice_user or not apprentice_user.has_usable_password():
            apprentice_user.set_password("password123")
            apprentice_user.save()

        # Create Team
        team, _ = Team.objects.get_or_create(
            name="Kanban Team", defaults={"description": "Main development team"}
        )
        TeamMember.objects.get_or_create(team=team, user=admin_user)
        TeamMember.objects.get_or_create(team=team, user=apprentice_user)

        # Create Project
        project1, _ = Project.objects.get_or_create(
            name="Kanban MVP",
            defaults={"description": "Build main page and core workflow."},
        )
        ProjectTeam.objects.get_or_create(project=project1, team=team)

        # Create Statuses
        todo, _ = Status.objects.get_or_create(
            name="TODO", defaults={"description": "To Do"}
        )
        doing, _ = Status.objects.get_or_create(
            name="DOING", defaults={"description": "In Progress"}
        )
        done, _ = Status.objects.get_or_create(
            name="DONE", defaults={"description": "Completed"}
        )

        # Create a List of Tasks for Projects
        task_list = [
            (
                project1,
                todo,
                "Build main index page",
                "Show Projects table and task columns",
            ),
            (project1, doing, "Seed demo data", "Add seed command and verify output"),
            (project1, done, "Create mockup", "Mockups approved by team."),
        ]

        # Create Tasks from task_list
        for project, status, title, description in task_list:
            task, _ = Task.objects.get_or_create(
                project=project,
                title=title,
                defaults={
                    "description": description,
                    "created_by": admin_user,
                    "status": status,
                },
            )
            TaskAssignee.objects.get_or_create(task=task, user=apprentice_user)

        self.stdout.write(
            self.style.SUCCESS("Seed data created/verified successfully.")
        )
        self.stdout.write("Demo login: apprentice@example.com / password123")
