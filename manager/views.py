from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Project, Task, Comment, Notification

def home(request):
    if request.user.is_authenticated:
        projects = Project.objects.filter(members=request.user) | Project.objects.filter(owner=request.user)
        projects = projects.distinct()
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        return render(request, 'manager/home.html', {
            'projects': projects,
            'notifications': notifications
        })
    return render(request, 'manager/landing.html')

@login_required
def create_project(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        project = Project.objects.create(
            name=name,
            description=description,
            owner=request.user
        )
        project.members.add(request.user)
        return redirect('project_detail', pk=project.pk)
    return render(request, 'manager/create_project.html')

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    todo_tasks = project.tasks.filter(status='todo')
    inprogress_tasks = project.tasks.filter(status='inprogress')
    done_tasks = project.tasks.filter(status='done')
    members = project.members.all()
    return render(request, 'manager/project_detail.html', {
        'project': project,
        'todo_tasks': todo_tasks,
        'inprogress_tasks': inprogress_tasks,
        'done_tasks': done_tasks,
        'members': members,
    })

@login_required
def add_member(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            project.members.add(user)
            Notification.objects.create(
                user=user,
                message=f'You were added to project: {project.name}'
            )
        except User.DoesNotExist:
            pass
    return redirect('project_detail', pk=pk)

@login_required
def create_task(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        assigned_id = request.POST.get('assigned_to')
        priority = request.POST.get('priority', 'medium')
        due_date = request.POST.get('due_date') or None
        assigned_user = None
        if assigned_id:
            try:
                assigned_user = User.objects.get(pk=assigned_id)
            except User.DoesNotExist:
                pass
        task = Task.objects.create(
            project=project,
            title=title,
            description=description,
            assigned_to=assigned_user,
            priority=priority,
            due_date=due_date,
        )
        if assigned_user:
            Notification.objects.create(
                user=assigned_user,
                message=f'You were assigned task: {task.title} in {project.name}'
            )
        return redirect('project_detail', pk=pk)
    members = project.members.all()
    return render(request, 'manager/create_task.html', {
        'project': project,
        'members': members
    })

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    comments = task.comments.all().order_by('-created_at')
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(task=task, user=request.user, content=content)
        return redirect('task_detail', pk=pk)
    return render(request, 'manager/task_detail.html', {
        'task': task,
        'comments': comments
    })

@login_required
def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['todo', 'inprogress', 'done']:
            task.status = status
            task.save()
    return redirect('project_detail', pk=task.project.pk)

@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    project_pk = task.project.pk
    task.delete()
    return redirect('project_detail', pk=project_pk)

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'manager/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'manager/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')
