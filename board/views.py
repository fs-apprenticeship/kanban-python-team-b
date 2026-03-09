from django.views.decorators.cache import never_cache
from django.db.models import Q
from board.models import Project, Task, Status
from .forms import LoginForm, ProfileForm, AddTaskForm
from django.contrib.auth import logout as _logout, authenticate, login as _login
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django_htmx.http import HttpResponseClientRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

# Constant Status Columns
KANBAN_COLUMNS = ["TODO", "DOING", "DONE"]


def _no_cache_response(response):
    """
    Add headers to prevent browser back-button caching.
    """
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response


@never_cache
def index(request):
    if not request.user.is_authenticated:
        return redirect(reverse("board:login"))
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
                    return HttpResponseClientRedirect(redirect_url)

                response = redirect(redirect_url)
                return _no_cache_response(response)

            else:
                form.add_error(None, "Invalid email or password.")

    else:
        form = LoginForm()

    template_name = (
        "board/partials/login_form.html"
        if getattr(request, "htmx", False)
        else "board/login.html"
    )

    response = render(
        request,
        template_name,
        {"form": form},
    )

    return _no_cache_response(response)


@login_required
def task_modal(request, task_id):
    tasks = Task.objects.filter(
        Q(task_assignees__user=request.user)
        | Q(project__project_teams__team__members__user=request.user)
    ).distinct()
    task = get_object_or_404(tasks, pk=task_id)
    return render(request, "board/partials/task_modal.html", {"task": task})


@login_required
def task_modal_close(request):
    return HttpResponse("")


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return render(
                request,
                "board/partials/profile_form.html",
                {"form": form, "success_message": "Profile updated successfully."},
            )

        return render(
            request, "board/partials/profile_form.html", {"form": form}, status=422
        )

    form = ProfileForm(instance=request.user)

    return render(request, "board/profile.html", {"form": form})


def _project_tasks_context(project, add_task_form=None):
    tasks = (
        Task.objects.filter(project=project)
        .select_related("project", "status")
        .prefetch_related("task_assignees")
        .order_by("-updated_at")
    )

    tasks_by_kind = {"UNASSIGNED": [], "ASSIGNED": [], "INPROGRESS": [], "COMPLETED": []}

    for task in tasks:
        status_name = (task.status.name if task.status else "TODO").upper()
        if status_name == "DONE":
            tasks_by_kind["COMPLETED"].append(task)
        elif status_name == "DOING":
            tasks_by_kind["INPROGRESS"].append(task)
        else:
            if task.task_assignees.exists():
                tasks_by_kind["ASSIGNED"].append(task)
            else:
                tasks_by_kind["UNASSIGNED"].append(task)

    if add_task_form is None:
        add_task_form = AddTaskForm(initial={"project": project.id, "status": "TODO"})

    return {"project": project, "tasks_by_kind": tasks_by_kind, "add_task_form": add_task_form}


@login_required
def project(request, project_id):
    project_obj = get_object_or_404(
        Project.objects.filter(
            project_teams__team__members__user=request.user,
            is_archived=False,
        ).distinct(),
        pk=project_id,
    )

    if request.method == "POST":
        form = AddTaskForm(request.POST)
        if form.is_valid() and form.cleaned_data["project"] == project_obj.id:
            status_obj = Status.objects.filter(name=form.cleaned_data["status"]).first()
            Task.objects.create(
                project=project_obj,
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"] or "",
                status=status_obj,
                created_by=request.user,
            )
            ctx = _project_tasks_context(project_obj)
            return render(
                request,
                "board/partials/project_tasks.html",
                ctx,
            )
        ctx = _project_tasks_context(project_obj, add_task_form=form)
        return render(
            request,
            "board/partials/project_tasks.html",
            ctx,
            status=422,
        )

    ctx = _project_tasks_context(project_obj)
    ctx["project"] = project_obj
    return render(request, "board/project.html", ctx)
