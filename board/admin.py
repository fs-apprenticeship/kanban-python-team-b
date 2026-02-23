from django.contrib import admin
from .models import Role, User, Team, TeamMember, Project, ProjectTeam, Status, Task, TaskAssignee

admin.site.register(Role)
admin.site.register(User)
admin.site.register(Team)
admin.site.register(TeamMember)
admin.site.register(Project)
admin.site.register(ProjectTeam)
admin.site.register(Status)
admin.site.register(Task)
admin.site.register(TaskAssignee)
