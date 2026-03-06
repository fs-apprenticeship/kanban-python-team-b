from django.views.decorators.cache import never_cache
from board.models import Project, Task
from .forms import LoginForm, ProfileForm
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
    task = get_object_or_404(
        Task.objects.filter(task_assignees__user=request.user), pk=task_id
    )
    return render(request, "board/partials/task_modal.html", {"task": task})


def task_modal_close(request):
    return HttpResponse("")


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
            request, "board/partials/profile_form.html", {"form": form}, status=400
        )

    form = ProfileForm(instance=request.user)

    return render(request, "board/profile.html", {"form": form})
