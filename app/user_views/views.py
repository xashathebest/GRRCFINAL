from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import PermissionDenied
from .forms import ArticleForm, UserForm, ResearchForm
from .models import Article, User, Research
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils import timezone

def index(request):
    return render(request, 'links/index.html')

def logout_view(request):
    # Clear any existing messages
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # Simply iterating clears the messages
    
    # Flush the session to log out the user
    request.session.flush()
    
    # Add a fresh logout success message
    messages.success(request, "You have been logged out.")
    
    return redirect('index')

def about_us(request):
    return render(request, 'links/about_us.html')

def home(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    context = {
        'user_name': f"{user.first_name} {user.last_name}",
        'user_role': user.role
    }
    
    if user.role == 'admin':
        # Admin sees all articles and statistics
        context['total_articles'] = Article.objects.count()
        context['pending_articles'] = Article.objects.filter(is_approved=False).count()
        context['approved_articles'] = Article.objects.filter(is_approved=True).count()
        context['recent_articles'] = Article.objects.all().order_by('-created_at')[:5]
    else:
        # Member sees only their articles and statistics
        context['total_articles'] = Article.objects.filter(author=user).count()
        context['pending_articles'] = Article.objects.filter(author=user, is_approved=False).count()
        context['approved_articles'] = Article.objects.filter(author=user, is_approved=True).count()
        context['recent_articles'] = Article.objects.filter(author=user).order_by('-created_at')[:5]
    
    return render(request, 'links/home.html', context)

def account_list(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    users = User.objects.all()
    context = {
        'users': users,
        'user_role': user.role,
        'user_name': f"{user.first_name} {user.last_name}"
    }
    return render(request, 'links/account_list.html', context)

def base(request):
    return render(request, 'links/base.html')

def login_auth(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, 'links/login.html')

        if not user.is_active:
            messages.error(request, "User is not active. Please contact the administrator.")
            return render(request, 'links/login.html') 
        
        # request.session['user_id'] = user.id
        # request.session['user_name'] = user.first_name
        # request.session['user_role'] = user.role
        # request.session['just_logged_in'] = True
        # return redirect('home')

        if check_password(password, user.password):
            request.session['user_id'] = user.id
            request.session['user_name'] = user.first_name
            request.session['user_role'] = user.role
            request.session['just_logged_in'] = True
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'links/login.html')

def article_list(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    if user.role == 'admin':
        articles = Article.objects.filter(is_approved=True).order_by('-created_at')
    else:
        articles = Article.objects.filter(author=user, is_approved=True).order_by('-created_at')
    
    context = {
        'articles': articles,
        'user_role': user.role,
        'user_name': f"{user.first_name} {user.last_name}"
    }
    return render(request, 'links/article_list.html', context)

def pending_articles(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    if user.role == 'admin':
        pending_articles = Article.objects.filter(is_approved=False).order_by('-created_at')
    else:
        pending_articles = Article.objects.filter(author=user, is_approved=False).order_by('-created_at')
    
    context = {
        'pending_articles': pending_articles,
        'user_role': user.role,
        'user_name': f"{user.first_name} {user.last_name}"
    }
    return render(request, 'links/pending_articles.html', context)

@require_POST
def approve_article(request, article_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    article = get_object_or_404(Article, id=article_id)
    article.is_approved = True
    article.save()
    messages.success(request, 'Article approved successfully!')
    return redirect('pending_articles')

def add_article(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = user
            # Set is_approved based on user role
            article.is_approved = (user.role == 'admin')
            article.save()
            messages.success(request, 'Article created successfully!')
            return redirect('pending_articles' if user.role == 'member' else 'article_list')
    else:
        form = ArticleForm()
    
    context = {
        'form': form,
        'user_role': user.role,
        'user_name': f"{user.first_name} {user.last_name}"
    }
    return render(request, 'links/add_article.html', context)

def edit_article(request, article_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    article = get_object_or_404(Article, id=article_id)
    
    # Check permissions
    if user.role != 'admin' and article.author != user:
        messages.error(request, 'You do not have permission to edit this article.')
        return redirect('article_list')
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article updated successfully!')
            return redirect('article_list')
    else:
        form = ArticleForm(instance=article)
    
    context = {
        'form': form,
        'article': article,
        'user_role': user.role,
        'user_name': f"{user.first_name} {user.last_name}"
    }
    return render(request, 'links/edit_article.html', context)

def delete_article(request, article_id):
    if not request.session.get('user_id'):
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'})
    
    user = User.objects.get(id=request.session['user_id'])
    article = get_object_or_404(Article, id=article_id)
    
    # Check permissions
    if user.role != 'admin' and article.author != user:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'})
    
    article.delete()
    return redirect("article_list")

def add_user(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'A user with this email already exists.')

            user = form.save(commit=False)  # Don't save yet
            user.is_active = True  # Set is_active to True
            user.save()  # Now save the user
            messages.success(request, 'User created successfully!')
            return redirect('account_list')
    else:
        form = UserForm()
    
    context = {
        'form': form,
        'user_role': user.role,
        'user_name': f"{user.first_name} {user.last_name}"
    }
    return render(request, 'links/add_user.html', context)

def edit_user(request, user_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    current_user = User.objects.get(id=request.session['user_id'])
    if current_user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('account_list')
    else:
        form = UserForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
        'user_role': current_user.role,
        'user_name': f"{current_user.first_name} {current_user.last_name}"
    }
    return render(request, 'links/edit_user.html', context)

def delete_user(request, user_id):
    if not request.session.get('user_id'):
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'})
    
    current_user = User.objects.get(id=request.session['user_id'])
    if current_user.role != 'admin':
        return JsonResponse({'status': 'error', 'message': 'Permission denied'})
    
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect("account_list")

def activities(request):
    # Get all approved articles ordered by creation date
    articles = Article.objects.filter(is_approved=True).order_by('-created_at')
    
    # Get current date
    current_date = timezone.now()
    
    # Separate articles into recent and past
    recent_articles = articles.filter(created_at__gte=current_date - timezone.timedelta(days=30))
    past_articles = articles.filter(created_at__lt=current_date - timezone.timedelta(days=30))
    
    # Get the latest article for featured section
    latest_article = recent_articles.first() if recent_articles.exists() else past_articles.first()
    
    # Get the next 3 recent articles for the Last Activities section
    recent_activities = recent_articles.exclude(id=latest_article.id)[:3] if latest_article else recent_articles[:3]
    
    # Paginate past articles
    paginator = Paginator(past_articles, 6)  # Show 6 articles per page
    page_number = request.GET.get('page')
    past_articles_page = paginator.get_page(page_number)
    
    context = {
        'latest_article': latest_article,
        'recent_activities': recent_activities,
        'past_articles_page': past_articles_page,
        'total_articles': articles.count(),
        'recent_count': recent_articles.count(),
        'past_count': past_articles.count()
    }
    return render(request, 'links/activities.html', context)

def uga(request):
    return render(request, 'links/uga.html')















################################################################################################################################################










#next time na
def research(request):
    # Get all approved research articles ordered by creation date
    research_articles = Research.objects.filter(is_approved=True).order_by('-created_at')
    
    # Get current date
    current_date = timezone.now()
    
    # Separate articles into recent and past
    recent_research = research_articles.filter(created_at__gte=current_date - timezone.timedelta(days=30))
    past_research = research_articles.filter(created_at__lt=current_date - timezone.timedelta(days=30))
    
    # Get the latest research for featured section
    latest_research = recent_research.first() if recent_research.exists() else past_research.first()
    
    # Get the next 3 recent research articles
    recent_research_list = recent_research.exclude(id=latest_research.id)[:3] if latest_research else recent_research[:3]
    
    # Paginate past research
    paginator = Paginator(past_research, 6)  # Show 6 articles per page
    page_number = request.GET.get('page')
    past_research_page = paginator.get_page(page_number)
    
    # Initialize context with public data
    context = {
        'latest_research': latest_research,
        'recent_research': recent_research_list,
        'past_research_page': past_research_page,
        'total_research': research_articles.count(),
        'recent_count': recent_research.count(),
        'past_count': past_research.count()
    }
    
    # Only handle form submission and add user data if user is logged in
    if request.session.get('user_id'):
        user = User.objects.get(id=request.session['user_id'])
        context.update({
            'user_role': user.role,
            'user_name': f"{user.first_name} {user.last_name}"
        })
        
        if request.method == 'POST':
            form = ResearchForm(request.POST, request.FILES)
            if form.is_valid():
                research = form.save(commit=False)
                research.author = user
                research.is_approved = (user.role == 'admin')
                research.save()
                messages.success(request, 'Research article submitted successfully!')
                return redirect('research')
        else:
            form = ResearchForm()
            context['form'] = form
    
    return render(request, 'links/research.html', context)

@require_POST
def approve_research(request, research_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('research')
    
    research = get_object_or_404(Research, id=research_id)
    research.is_approved = True
    research.save()
    messages.success(request, 'Research article approved successfully!')
    return redirect('research')

def edit_research(request, research_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    research = get_object_or_404(Research, id=research_id)
    
    # Check permissions
    if user.role != 'admin' and research.author != user:
        messages.error(request, 'You do not have permission to edit this research article.')
        return redirect('research')
    
    if request.method == 'POST':
        form = ResearchForm(request.POST, request.FILES, instance=research)
        if form.is_valid():
            form.save()
            messages.success(request, 'Research article updated successfully!')
            return redirect('research')
    else:
        form = ResearchForm(instance=research)
    
    context = {
        'form': form,
        'research': research,
        'user_role': user.role,
        'user_name': f"{user.first_name} {user.last_name}"
    }
    return render(request, 'links/edit_research.html', context)

def delete_research(request, research_id):
    if not request.session.get('user_id'):
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'})
    
    user = User.objects.get(id=request.session['user_id'])
    research = get_object_or_404(Research, id=research_id)
    
    # Check permissions
    if user.role != 'admin' and research.author != user:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'})
    
    research.delete()
    return JsonResponse({'status': 'success'})

def gender_clubs(request):
    return render(request, 'links/gender_clubs.html')