from django.contrib import admin
from . import models

admin.site.register(models.Role)
admin.site.register(models.User)
admin.site.register(models.Team)
admin.site.register(models.TeamMember)
admin.site.register(models.Project)
admin.site.register(models.ProjectTeam)
admin.site.register(models.Status)
admin.site.register(models.Task)
admin.site.register(models.TaskAssignee)
admin.site.register(models.TaskComment)
