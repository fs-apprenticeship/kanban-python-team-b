from django.contrib.auth import logout as _logout, authenticate, login as _login
from django.shortcuts import render, redirect
from django.urls import reverse
from board.models import Project, Task


# Constant Status Columns
KANBAN_COLUMNS = ["TODO", "DOING", "DONE"]

from .forms import LoginForm

def index(request):
    if not request.user.is_authenticated:
        return redirect(reverse("board:login"))
    return render(request, "board/index.html", {})
        # TODO: replace with board:login once created
        return redirect(reverse("admin:login"))

    # Logged-in user
    user = request.user

    # Projects
    projects = (
        Project.objects.filter(
            project_teams__team__members__user=user, is_archived=False
        )
        .distinct()
        .order_by("name")
    )

    # Tasks
    tasks = (
        Task.objects.filter(task_assignees__user=user)
        .select_related("project", "status")
        .order_by("-updated_at")
    )

    # Created grouped dictionary
    tasks_by_status = {col: [] for col in KANBAN_COLUMNS}

    for task in tasks:
        key = (task.status.name if task.status else "TODO").upper()
        if key not in tasks_by_status:
            key = "TODO"
        tasks_by_status[key].append(task)

    # Context
    context = {
        "projects": projects,
        "tasks_by_status": tasks_by_status,
    }

    return render(request, "board/index.html", context)


def logout(request):
    if request.user.is_authenticated:
        _logout(request)
    return redirect(reverse("board:index"))


def login(request):
    if request.user.is_authenticated:
        return redirect(reverse("board:index"))

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                _login(request, user)
                redirect_url = reverse("board:index")
                if getattr(request, "htmx", False):
                    response = redirect(redirect_url)
                    response["HX-Redirect"] = redirect_url
                    return response
                return redirect(redirect_url)
            else:
                form.add_error(None, "Invalid email or password.")
    else:
        form = LoginForm()

    template_name = "board/partials/login_form.html" if getattr(request, "htmx", False) else "board/login.html"
    return render(request, template_name, {"form": form})
