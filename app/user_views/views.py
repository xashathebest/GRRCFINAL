import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .forms import * # Forms
from .models import * #  Models
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils import timezone
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required


def index(request):
    active_theme = ThemeSettings.objects.filter(is_active=True).first()
    context = {
        'active_theme': active_theme
    }
    return render(request, 'links/index.html', context)

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
    carousel_images = AboutUsCarousel.objects.filter(is_active=True).order_by('order', '-created_at')
    return render(request, 'links/about_us.html', {'carousel_images': carousel_images})

def gender_clubs(request):
    return render(request, 'links/gender_clubs.html')
    

def footer_info(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    
    # Get or create footer information
    footer, created = FooterInfo.objects.get_or_create(
        defaults={
            'contact_email': 'grrc@wmsu.edu.ph',
            'contact_phone': '(+63) 123-4567'
        }
    )
    
    return render(request, 'links/edit_footer.html', {
        'footer': footer,
        'user_name': f"{user.first_name} {user.last_name}",
        'user_role': user.role
    })

def update_footer_info(request):
    if request.method == 'POST':
        # Get or create the footer info object
        footer, created = FooterInfo.objects.get_or_create(id=1)
        
        # Update the footer info with form data
        footer.contact_email = request.POST.get('contact_email')
        footer.contact_phone = request.POST.get('contact_phone')
        footer.social_facebook = request.POST.get('social_facebook')
        footer.social_instagram = request.POST.get('social_instagram')
        
        # Handle logo upload
        if 'logo' in request.FILES and request.FILES['logo']:
            # Delete old logo file if it exists
            if footer.logo:
                try:
                    if os.path.isfile(footer.logo.path):
                        os.remove(footer.logo.path)
                except:
                    pass  # If file doesn't exist or can't be deleted, continue anyway
            
            # Save the new logo
            footer.logo = request.FILES['logo']
        
        # Save the updated footer info
        footer.save()
        
        # Add a success message
        messages.success(request, 'Footer information updated successfully!')
        
        # Redirect back to the edit page
        return redirect('footer_info')
    else:
        # For GET requests, redirect to the footer info page
        return redirect('footer_info')

def base(request):
    active_theme = ThemeSettings.objects.filter(is_active=True).first()
    context = {
        'active_theme': active_theme
    }
    return render(request, 'links/base.html', context)

def get_base_context(request):
    """Helper function to get base context with theme settings"""
    user = None
    if request.session.get('user_id'):
        user = User.objects.get(id=request.session['user_id'])
    
    active_theme = ThemeSettings.objects.filter(is_active=True).first()
    
    context = {
        'active_theme': active_theme
    }
    
    if user:
        context.update({
            'user_name': f"{user.first_name} {user.last_name}",
            'user_role': user.role
        })
    
    return context

def login_auth(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                if not user.is_active:
                    messages.error(request, "User is not active. Please contact the administrator.")
                    return render(request, 'links/login.html')
                
                request.session['user_id'] = user.id
                request.session['user_name'] = user.first_name
                request.session['user_role'] = user.role
                request.session['just_logged_in'] = True
                return redirect('home')
            else:
                messages.error(request, "Invalid email or password.")
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
        except Exception as e:
            messages.error(request, "An error occurred during login. Please try again.")
            print(f"Login error: {str(e)}")

    return render(request, 'links/login.html')


def article_list(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    context = get_base_context(request)
    
    if user.role == 'admin':
        articles = Article.objects.filter(is_approved=True).order_by('-created_at')
    else:
        articles = Article.objects.filter(author=user, is_approved=True).order_by('-created_at')
    
    context['articles'] = articles
    return render(request, 'links/article_list.html', context)

def pending_articles(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    if user.role == 'admin':
        pending_articles = Article.objects.filter(is_approved=False).order_by('-created_at')
    elif user.role == 'member':
        pending_articles = Article.objects.filter(author=user, is_approved=False).order_by('-created_at')
    
    context = {
        'pending_articles': pending_articles,
        'user_role': user.role,
        'user_name': f"{user.first_name} {user.last_name}"
    }
    return render(request, 'links/pending_articles.html', context)


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
    latest_article = Article.objects.filter(is_approved=True).order_by('-created_at').first()
    recent_activities = Article.objects.filter(is_approved=True).order_by('-created_at')[1:4]
    
    # Get activities carousel images
    carousel_images = ActivitiesCarousel.objects.filter(is_active=True).order_by('order', '-created_at')
    
    # Pagination for past articles
    past_articles = Article.objects.filter(is_approved=True).order_by('-created_at')[4:]
    paginator = Paginator(past_articles, 6)
    page = request.GET.get('page')
    
    try:
        past_articles_page = paginator.page(page)
    except PageNotAnInteger:
        past_articles_page = paginator.page(1)
    except EmptyPage:
        past_articles_page = paginator.page(paginator.num_pages)

    context = {
        'latest_article': latest_article,
        'recent_activities': recent_activities,
        'past_articles_page': past_articles_page,
        'carousel_images': carousel_images,
    }
    
    return render(request, 'links/activities.html', context)

def activity_detail(request, pk):
    article = get_object_or_404(Article, pk=pk, is_approved=True)
    return render(request, 'links/activity_detail.html', {'article': article})

def past_activities_ajax(request):
    page = request.GET.get("page", 1)
    articles = Research.objects.filter(is_approved=True, is_featured=False).order_by('-created_at')
    paginator = Paginator(articles, 3)

    try:
        page = int(page)
        paginated_articles = paginator.page(page)
    except:
        paginated_articles = paginator.page(1)

    html = render_to_string("links/past_activities_partial.html", {
        "past_articles_page": paginated_articles,
    }, request=request)

    return JsonResponse({
        'html': html,
        'has_next': paginated_articles.has_next()  # Add this to help frontend
    })

def uga(request):
    carousel_images = UGACarousel.objects.filter(is_active=True).order_by('order', '-created_at')
    context = {
        'hero': UGAHeroSection.objects.first(),
        'overview': UGAOverviewSection.objects.first(),
        'overview_cards': UGAOverviewCard.objects.all(),
        'key_areas': UGAKeyArea.objects.all(),
        'implementation_steps': UGAImplementationStep.objects.order_by('step_number'),
        'cta': UGACallToAction.objects.first(),
        'carousel_images': carousel_images
    }
    return render(request, 'links/uga.html', context)

def manage_content(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    hero = UGAHeroSection.objects.first()
    overview = UGAOverviewSection.objects.first()
    overview_cards = UGAOverviewCard.objects.all()
    key_areas = UGAKeyArea.objects.all()
    steps = UGAImplementationStep.objects.all()
    call_to_action = UGACallToAction.objects.first()

    return render(request, 'uga/manage_content.html', {
        'hero': hero,
        'overview': overview,
        'overview_cards': overview_cards,
        'key_areas': key_areas,
        'steps': steps,
        'call_to_action': call_to_action,
        'user_name': f"{user.first_name} {user.last_name}",
        'user_role': user.role
    })

# def update_hero(request):
#     if not request.session.get('user_id'):
#         return redirect('login')
    
#     user = User.objects.get(id=request.session['user_id'])
#     hero = UGAHeroSection.objects.first()
#     if not hero:
#         hero = UGAHeroSection.objects.create()  # Ensure one exists

#     if request.method == 'POST':
#         form = UGAHeroForm(request.POST, request.FILES, instance=hero)
#         if form.is_valid():
#             form.save()
#             return redirect('manage_content')
#     else:
#         form = UGAHeroForm(instance=hero)

#     return render(request, 'uga/update_hero.html', {'form': form,'user_name': f"{user.first_name} {user.last_name}",'user_role': user.role})

# def update_overview(request):
#     if not request.session.get('user_id'):
#         return redirect('login')

#     user = User.objects.get(id=request.session['user_id'])
#     overview = UGAOverviewSection.objects.first()
#     if not overview:
#         overview = UGAOverviewSection.objects.create()

#     if request.method == 'POST':
#         form = UGAOverviewForm(request.POST, instance=overview)
#         if form.is_valid():
#             form.save()
#             return redirect('manage_content')
#     else:
#         form = UGAOverviewForm(instance=overview)

#     return render(request, 'uga/update_overview.html', {
#         'form': form,
#         'user_name': f"{user.first_name} {user.last_name}",
#         'user_role': user.role
#     })

# def update_key_area(request, key_area_id):
#     if not request.session.get('user_id'):
#         return redirect('login')

#     user = User.objects.get(id=request.session['user_id'])
#     key_area = UGAKeyArea.objects.get(id=key_area_id)

#     if request.method == 'POST':
#         form = UGAKeyAreaForm(request.POST, instance=key_area)
#         if form.is_valid():
#             form.save()
#             return redirect('manage_content')
#     else:
#         form = UGAKeyAreaForm(instance=key_area)

#     return render(request, 'uga/update_key_area.html', {
#         'form': form,
#         'user_name': f"{user.first_name} {user.last_name}",
#         'user_role': user.role
#     })

# def update_card(request, card_id):
#     if not request.session.get('user_id'):
#         return redirect('login')

#     user = User.objects.get(id=request.session['user_id'])
#     card = ContentCard.objects.get(id=card_id)

#     if request.method == 'POST':
#         form = UGAOverviewCardForm(request.POST, request.FILES, instance=card)
#         if form.is_valid():
#             form.save()
#             return redirect('manage_content')
#     else:
#         form = UGAOverviewCardForm(instance=card)

#     return render(request, 'uga/update_card.html', {
#         'form': form,
#         'user_name': f"{user.first_name} {user.last_name}",
#         'user_role': user.role
#     })

# def update_strategy(request):
#     if not request.session.get('user_id'):
#         return redirect('login')

#     user = User.objects.get(id=request.session['user_id'])
#     strategy = UGAImplementationStep.objects.first()
#     if not strategy:
#         strategy = UGAImplementationStep.objects.create()

#     if request.method == 'POST':
#         form = ImplementationStepForm(request.POST, instance=strategy)
#         if form.is_valid():
#             form.save()
#             return redirect('manage_content')
#     else:
#         form = ImplementationStepForm(instance=strategy)

#     return render(request, 'uga/update_strategy.html', {
#         'form': form,
#         'user_name': f"{user.first_name} {user.last_name}",
#         'user_role': user.role
#     })
# def update_cta  (request):
#     if not request.session.get('user_id'):
#         return redirect('login')

#     user = User.objects.get(id=request.session['user_id'])
#     cta = UGACallToAction.objects.first()
#     if not cta:
#         cta = UGACallToAction.objects.create()

#     if request.method == 'POST':
#         form = UGACallToActionForm(request.POST, instance=cta)
#         if form.is_valid():
#             form.save()
#             return redirect('manage_content')
#     else:
#         form = UGACallToActionForm(instance=cta)

#     return render(request, 'uga/update_cta.html', {
#         'form': form,
#         'user_name': f"{user.first_name} {user.last_name}",
#         'user_role': user.role
#     })



################################################################################################################################################


def research(request):
    carousel_images = ResearchCarousel.objects.filter(is_active=True).order_by('order', '-created_at')
    category_id = request.GET.get('category')
    research_list = Research.objects.all().order_by('-created_at')

    if category_id:
        research_list = research_list.filter(category_id=category_id)

    paginator = Paginator(research_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    selected_category = int(category_id) if category_id else None
    categories = ResearchCategory.objects.all()
    featured_research = Research.objects.filter(is_featured=True).order_by('-featured_order')[:3]

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('links/research_results.html', {
            'page_obj': page_obj,
            'selected_category': selected_category
        })
        return JsonResponse({
            'html': html,
            'selected_category': selected_category
        })

    return render(request, 'links/research.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'featured_research': featured_research,
        'carousel_images': carousel_images
    })

def research_list(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])

    # Role-based filtering
    if user.role == 'admin':
        research_articles = Research.objects.filter(is_approved=True)
    elif user.role == 'member':
        # Members can only see their own articles (whether approved or not)
        research_articles = Research.objects.filter(author=user)
    else:
        # Other roles (e.g., editors, faculty) see only their approved articles
        research_articles = Research.objects.filter(author=user, is_approved=True)

    # Sort: featured first, then by featured_order, then by newest created
    sorted_articles = sorted(
        research_articles,
        key=lambda x: (
            not x.is_featured,  # True (featured) comes first
            x.featured_order if x.featured_order is not None else float('inf'),
            -x.created_at.timestamp()
        )
    )
    
    context = get_base_context(request)
    context['research_articles'] = sorted_articles
    return render(request, 'links/research_list.html', context)


def research_detail(request, pk):
    research = get_object_or_404(Research, pk=pk)
    context = {
        'research': research
    }
    return render(request, 'links/research_detail.html', context)

def pending_research(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])

    if user.role == 'admin':
        # Admin sees all unapproved research
        research_articles = Research.objects.filter(is_approved=False).order_by('-created_at')
    elif user.role == 'member':
        # Members only see their own (approved or not)
        research_articles = Research.objects.filter(author=user,is_approved=False).order_by('-created_at')
    
    context = {
        'research_articles': research_articles,
        'user_role': user.role,
        'user_name': f"{user.first_name} {user.last_name}"
    }

    return render(request, 'links/pending_research.html', context)




def add_research(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
        
    if request.method == 'POST':
        form = ResearchForm(request.POST, request.FILES)
        if form.is_valid():
            research = form.save(commit=False)
            research.author = user
            
            # Auto-approve research submitted by admin users
            if user.role == 'admin':
                research.is_approved = True
                message = 'Research submitted and published successfully!'
            else:
                message = 'Research submitted successfully! Awaiting approval.'
                
            research.save()
            messages.success(request, message)
            return redirect('research_list')  # Redirect to research list page
    else:
        form = ResearchForm()

    context = {
        'form': form,
        'user_role': user.role,
        'user_name': f"{user.first_name} {user.last_name}"
    }
    print("FILES:", request.FILES)

    return render(request, 'links/add_research.html',context)

@require_POST
def approve_research(request, research_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('research_list')
    
    research = get_object_or_404(Research, id=research_id)
    research.is_approved = True
    research.save()
    messages.success(request, 'Research article approved successfully!')
    return redirect('research_list')

def edit_research(request, research_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    research = get_object_or_404(Research, id=research_id)
    
    # Check permissions
    if user.role != 'admin' and research.author != user:
        messages.error(request, 'You do not have permission to edit this research article.')
        return redirect('login')
    
    if request.method == 'POST':
        form = ResearchForm(request.POST, request.FILES, instance=research)
        if form.is_valid():
            form.save()
            messages.success(request, 'Research article updated successfully!')
            return redirect('research_list')
    else:
        form = ResearchForm(instance=research)
    
    context = {
        'form': form,
        'research': research,
        'user_role': user.role,
        'user_name': f"{user.first_name} {user.last_name}"
    }
    print("FILES:", request.FILES)

    return render(request, 'links/edit_research.html', context)

def delete_research(request, pk):
    if request.session.get('user_role') != 'admin':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('index')  # or wherever you'd like to redirect unauthorized users

    research = get_object_or_404(Research, pk=pk)
    research.delete()
    messages.success(request, "Research deleted successfully.")
    return redirect('research_list')  # change to your actual list or dashboard view

def feature_research(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('featured_articles')

        # First, reset all current featured articles
        Research.objects.filter(is_featured=True).update(is_featured=False, featured_order=None)

        # Then, set new ones — limit to 3 just to be safe
        for order, article_id in enumerate(selected_ids[:3], start=1):
            try:
                research = Research.objects.get(pk=article_id)
                research.is_featured = True
                research.featured_order = order
                research.save()
            except Research.DoesNotExist:
                continue

        messages.success(request, "Featured articles updated successfully.")
        return redirect('research_list') 

def add_category(request):
    if request.method == 'POST':
        form = ResearchCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('pending_research')  # Or wherever you want to redirect
    else:
        form = ResearchCategoryForm()
    
    return render(request, 'links/pending_research.html', {'category_form': form})


# For HOME HeroSection CRUD operations

def hero_section(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    hero = HeroSection.objects.first()
    if not hero:
        hero = HeroSection.objects.create()

    context = get_base_context(request)
    context['hero'] = hero
    return render(request, 'hero_section/edit_hero.html', context)

def update_hero_section(request):
    if not request.session.get('user_id'):
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        hero, created = HeroSection.objects.get_or_create(id=1)

        hero.title_line_1 = request.POST.get('title_line_1', '').strip()
        hero.title_line_2 = request.POST.get('title_line_2', '').strip()
        hero.description = request.POST.get('description', '').strip()
        hero.visit_us_link = request.POST.get('visit_us_link', '').strip()

        if 'logo_image' in request.FILES:
            hero.logo_image = request.FILES['logo_image']

        if 'background_image' in request.FILES:
            hero.background_image = request.FILES['background_image']

        hero.save()

        messages.success(request, "Hero Section updated successfully.")
        return redirect('hero_section')

    hero = HeroSection.objects.first()
    context = get_base_context(request)
    context['hero'] = hero
    return render(request, 'hero_section/edit_hero.html', context)


def mission_vision_info(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    mission_vision = MissionVision.objects.first()
    if not mission_vision:
        mission_vision = MissionVision.objects.create()

    context = get_base_context(request)
    context['mission_vision'] = mission_vision
    return render(request, 'hero_section/edit_mission_vision.html', context)

def update_mission_vision(request):
    if not request.session.get('user_id'):
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        mission_vision, created = MissionVision.objects.get_or_create(id=1)

        mission_vision.mission_title = request.POST.get('mission_title', '').strip()
        mission_vision.mission_description = request.POST.get('mission_description', '').strip()
        mission_vision.vision_title = request.POST.get('vision_title', '').strip()
        mission_vision.vision_description = request.POST.get('vision_description', '').strip()
        mission_vision.mission_points = request.POST.get('mission_points').strip()
        mission_vision.vision_points = request.POST.get('vision_points').strip()

        if 'background_image' in request.FILES:
            mission_vision.background_image = request.FILES['background_image']

        mission_vision.save()
        messages.success(request, "Mission and Vision updated successfully.")
        return redirect('mission_vision_info')

    return redirect('mission_vision_info')

def key_objectives_info(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    key_objectives = KeyObjectives.objects.first()
    if not key_objectives:
        key_objectives = KeyObjectives.objects.create(
            heading="Key Objectives",
            intro="",
            objective_1_title="",
            objective_1_text="",
            objective_2_title="",
            objective_2_text="",
            objective_3_title="",
            objective_3_text="",
            objective_4_title="",
            objective_4_text="",
        )
    
    context = get_base_context(request)
    context['key_objectives'] = key_objectives
    return render(request, 'links/edit_key_objectives.html', context)


def update_key_objectives(request):
    if not request.session.get('user_id'):
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        key_objectives, created = KeyObjectives.objects.get_or_create(id=1)

        key_objectives.heading = request.POST.get('heading', '').strip()
        key_objectives.intro = request.POST.get('intro', '').strip()
        key_objectives.objective_1_title = request.POST.get('objective_1_title', '').strip()
        key_objectives.objective_1_text = request.POST.get('objective_1_text', '').strip()
        key_objectives.objective_2_title = request.POST.get('objective_2_title', '').strip()
        key_objectives.objective_2_text = request.POST.get('objective_2_text', '').strip()
        key_objectives.objective_3_title = request.POST.get('objective_3_title', '').strip()
        key_objectives.objective_3_text = request.POST.get('objective_3_text', '').strip()
        key_objectives.objective_4_title = request.POST.get('objective_4_title', '').strip()
        key_objectives.objective_4_text = request.POST.get('objective_4_text', '').strip()

        key_objectives.save()
        messages.success(request, "Key Objectives updated successfully.")
        return redirect('key_objectives_info')
    
    return redirect('key_objectives_info')

def edit_banner(request):
    if not request.session.get('user_id'):
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    banner = DynamicBannerImage.objects.last()
    form = BannerImageForm(request.POST or None, request.FILES or None, instance=banner)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Banner updated successfully!')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    context = get_base_context(request)
    context['form'] = form
    return render(request, 'hero_section/edit_banner.html', context)


def manage_cards(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    context = get_base_context(request)
    # The ContentCard model now has a Meta class with ordering, so we can just get all objects
    context['cards'] = ContentCard.objects.all()  
    return render(request, 'hero_section/manage_cards.html', context)

def edit_card(request, card_id):
    if not request.session.get('user_id'):
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    card = get_object_or_404(ContentCard, id=card_id)
    form = ContentCardForm(request.POST or None, request.FILES or None, instance=card)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Card updated successfully!')
        return redirect('manage_cards')

    context = get_base_context(request)
    context.update({
        'form': form,
        'card': card
    })
    return render(request, 'hero_section/edit_card.html', context)

def create_card(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    
    if request.method == 'POST':
        form = ContentCardForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Card created successfully!")
            return redirect('manage_cards')
    else:
        # Get next available order number (max + 1)
        next_order = 1
        if ContentCard.objects.exists():
            max_order = ContentCard.objects.aggregate(models.Max('order'))['order__max']
            next_order = max_order + 1 if max_order else 1
        
        # Initialize form with suggested next order
        form = ContentCardForm(initial={'order': next_order})
    
    context = get_base_context(request)
    context['form'] = form
    context['user_name'] = f"{user.first_name} {user.last_name}"
    context['user_role'] = user.role
    return render(request, 'hero_section/create_card.html', context)

def delete_card(request, card_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    card = get_object_or_404(ContentCard, id=card_id)
    
    if request.method == 'POST':
        # Store image path to delete file after database record is deleted
        image_path = card.image.path if card.image else None
        
        # Delete the card
        card.delete()
        
        # Delete the image file
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
            
        messages.success(request, "Card deleted successfully!")
        return redirect('manage_cards')
    
    context = get_base_context(request)
    context['card'] = card
    context['user_name'] = f"{user.first_name} {user.last_name}"
    context['user_role'] = user.role
    return render(request, 'hero_section/delete_card.html', context)

# Read - Show all team members
def team_list(request):
    if not request.session.get('user_id'):
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    context = get_base_context(request)
    context['team_members'] = TeamMember.objects.all()
    return render(request, 'team/team_list.html', context)

# Create - Add a new team member
def team_create(request):
    if not request.session.get('user_id'):
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('team_list')
    else:
        form = TeamMemberForm()
    
    context = get_base_context(request)
    context['form'] = form
    return render(request, 'team/team_form.html', context)

# Update - Edit an existing team member
def team_edit(request, pk):
    if not request.session.get('user_id'):
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    team_member = get_object_or_404(TeamMember, pk=pk)
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES, instance=team_member)
        if form.is_valid():
            form.save()
            return redirect('team_list')
    else:
        form = TeamMemberForm(instance=team_member)
    
    context = get_base_context(request)
    context['form'] = form
    return render(request, 'team/team_form.html', context)

# Delete - Remove a team member
def team_delete(request, pk):
    if not request.session.get('user_id'):
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    team_member = get_object_or_404(TeamMember, pk=pk)
    if request.method == 'POST':
        team_member.delete()
        return redirect('team_list')
    
    context = get_base_context(request)
    context['team_member'] = team_member
    return render(request, 'team/team_confirm_delete.html', context)

def theme_settings(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    context = get_base_context(request)
    themes = ThemeSettings.objects.all().order_by('-is_active', '-updated_at')
    context['themes'] = themes
    
    if request.method == 'POST':
        # Handle quick theme application
        if 'name' in request.POST and 'primary_color' in request.POST:
            # Deactivate all other themes
            ThemeSettings.objects.update(is_active=False)
            
            # Create or update the theme
            theme, created = ThemeSettings.objects.update_or_create(
                name=request.POST['name'],
                defaults={
                    'primary_color': request.POST['primary_color'],
                    'secondary_color': request.POST['secondary_color'],
                    'button_color': request.POST['button_color'],
                    'button_hover_color': request.POST['button_hover_color'],
                    'text_color': request.POST['text_color'],
                    'background_color': request.POST['background_color'],
                    'nav_background': request.POST['nav_background'],
                    'nav_text_color': request.POST['nav_text_color'],
                    'nav_hover_color': request.POST['nav_hover_color'],
                    'success_color': request.POST['success_color'],
                    'warning_color': request.POST['warning_color'],
                    'error_color': request.POST['error_color'],
                    'is_active': True
                }
            )
            messages.success(request, f'Theme "{theme.name}" has been applied successfully.')
            return redirect('theme_settings')
    
    return render(request, 'links/theme_settings.html', context)

def edit_theme(request, theme_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    theme = get_object_or_404(ThemeSettings, id=theme_id)
    
    if request.method == 'POST':
        form = ThemeSettingsForm(request.POST, instance=theme)
        if form.is_valid():
            theme = form.save()
            messages.success(request, f'Theme "{theme.name}" has been updated successfully.')
            return redirect('theme_settings')
    else:
        form = ThemeSettingsForm(instance=theme)
    
    context = {
        'theme': theme,
        'form': form,
        'user_role': user.role,
        'user_name': f"{user.first_name} {user.last_name}"
    }
    return render(request, 'links/edit_theme.html', context)

def delete_theme(request, theme_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    theme = get_object_or_404(ThemeSettings, id=theme_id)
    
    if request.method == 'POST':
        theme_name = theme.name
        theme.delete()
        messages.success(request, f'Theme "{theme_name}" has been deleted successfully.')
        return redirect('theme_settings')
    
    context = get_base_context(request)
    context['theme'] = theme
    return render(request, 'links/delete_theme.html', context)

def activate_theme(request, theme_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    theme = get_object_or_404(ThemeSettings, id=theme_id)
    theme.is_active = True
    theme.save()
    
    messages.success(request, f'Theme "{theme.name}" has been activated successfully.')
    return redirect('theme_settings')

def home(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    context = get_base_context(request)
    user = User.objects.get(id=request.session['user_id'])
    
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
    
    context = get_base_context(request)
    context['users'] = User.objects.all()
    users = User.objects.all().order_by('-date_created')
    for user in users:
        if isinstance(user.updated_at, str):
            user.updated_at = None
    context['users'] = users
    return render(request, 'links/account_list.html', context)

# List all cards
def card_list(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    cards = ContentCard.objects.all()
    context = get_base_context(request)
    context['cards'] = cards
    return render(request, 'cards/card_list.html', context)

# Create a new card
def card_create(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    if request.method == 'POST':
        form = ContentCardForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Card created successfully!')
            return redirect('card_list')
    else:
        form = ContentCardForm()
    
    context = get_base_context(request)
    context['form'] = form
    context['action'] = 'Create'
    return render(request, 'cards/card_form.html', context)

# Update an existing card
def card_edit(request, card_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    card = get_object_or_404(ContentCard, id=card_id)
    if request.method == 'POST':
        form = ContentCardForm(request.POST, request.FILES, instance=card)
        if form.is_valid():
            form.save()
            messages.success(request, 'Card updated successfully!')
            return redirect('card_list')
    else:
        form = ContentCardForm(instance=card)
    
    context = get_base_context(request)
    context['form'] = form
    context['card'] = card
    context['action'] = 'Update'
    return render(request, 'cards/card_form.html', context)

# Delete a card (with HTMX support)
def card_delete(request, card_id):
    if not request.session.get('user_id'):
        if request.headers.get('HX-Request'):
            return HttpResponse("Authentication required", status=401)
        return redirect('login')
    
    card = get_object_or_404(ContentCard, id=card_id)
    
    if request.method == 'POST':
        card.delete()
        if request.headers.get('HX-Request'):
            return HttpResponse("")  # Empty response means remove the element
        messages.success(request, 'Card deleted successfully!')
        return redirect('card_list')
    
    if request.headers.get('HX-Request'):
        return render(request, 'cards/card_delete_confirm_htmx.html', {'card': card})
    
    context = get_base_context(request)
    context['card'] = card
    return render(request, 'cards/card_delete_confirm.html', context)

def theme_css(request):
    active_theme = ThemeSettings.objects.filter(is_active=True).first()
    response = render(request, 'css/theme.css', {'active_theme': active_theme}, content_type='text/css')
    return response

def manage_carousel(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    carousel_images = CarouselImage.objects.all().order_by('order', 'created_at')
    hero_section = HeroSection.objects.first()
    
    if not hero_section:
        hero_section = HeroSection.objects.create()
    
    context = get_base_context(request)
    context['carousel_images'] = carousel_images
    context['hero_section'] = hero_section
    return render(request, 'hero_section/manage_carousel.html', context)

def add_carousel_image(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        image = request.FILES.get('image')
        
        # Check if we already have 5 images
        if CarouselImage.objects.count() >= 5:
            messages.error(request, "Maximum number of carousel images (5) reached. Delete an existing image to add a new one.")
            return redirect('manage_carousel')
        
        if title and image:
            CarouselImage.objects.create(
                title=title,
                order=order,
                is_active=is_active,
                image=image
            )
            messages.success(request, "Carousel image added successfully.")
        else:
            messages.error(request, "Please provide both title and image.")
            
    return redirect('manage_carousel')

def delete_carousel_image(request, image_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    try:
        carousel_image = CarouselImage.objects.get(id=image_id)
        
        # Check if deleting would leave us with less than 3 images
        if CarouselImage.objects.count() <= 3:
            messages.error(request, "Cannot delete image. A minimum of 3 carousel images is required.")
            return redirect('manage_carousel')
            
        carousel_image.delete()
        messages.success(request, "Carousel image deleted successfully.")
        
    except CarouselImage.DoesNotExist:
        messages.error(request, "Carousel image not found.")
        
    return redirect('manage_carousel')

def update_carousel_image(request, image_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    try:
        carousel_image = CarouselImage.objects.get(id=image_id)
        if request.method == 'POST':
            carousel_image.title = request.POST.get('title')
            carousel_image.order = request.POST.get('order', 0)
            carousel_image.is_active = request.POST.get('is_active') == 'on'
            
            if 'image' in request.FILES:
                carousel_image.image = request.FILES['image']
                
            carousel_image.save()
            messages.success(request, "Carousel image updated successfully.")
            
    except CarouselImage.DoesNotExist:
        messages.error(request, "Carousel image not found.")
        
    return redirect('manage_carousel')

def manage_activities_carousel(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    carousel_images = ActivitiesCarousel.objects.all().order_by('order', '-created_at')
    
    context = get_base_context(request)
    context['carousel_images'] = carousel_images
    return render(request, 'activities/manage_carousel.html', context)

def add_activities_carousel_image(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        subtitle = request.POST.get('subtitle')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        image = request.FILES.get('image')
        
        if title and image:
            ActivitiesCarousel.objects.create(
                title=title,
                subtitle=subtitle,
                order=order,
                is_active=is_active,
                image=image
            )
            messages.success(request, "Activities carousel image added successfully.")
        else:
            messages.error(request, "Please provide both title and image.")
            
    return redirect('manage_activities_carousel')

def update_activities_carousel_image(request, image_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    try:
        carousel_image = ActivitiesCarousel.objects.get(id=image_id)
        if request.method == 'POST':
            carousel_image.title = request.POST.get('title')
            carousel_image.subtitle = request.POST.get('subtitle')
            carousel_image.order = request.POST.get('order', 0)
            carousel_image.is_active = request.POST.get('is_active') == 'on'
            
            if 'image' in request.FILES:
                carousel_image.image = request.FILES['image']
                
            carousel_image.save()
            messages.success(request, "Activities carousel image updated successfully.")
            
    except ActivitiesCarousel.DoesNotExist:
        messages.error(request, "Carousel image not found.")
        
    return redirect('manage_activities_carousel')

def delete_activities_carousel_image(request, image_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    try:
        carousel_image = ActivitiesCarousel.objects.get(id=image_id)
        carousel_image.delete()
        messages.success(request, "Activities carousel image deleted successfully.")
        
    except ActivitiesCarousel.DoesNotExist:
        messages.error(request, "Carousel image not found.")
        
    return redirect('manage_activities_carousel')

def manage_aboutus_carousel(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    carousel_images = AboutUsCarousel.objects.all().order_by('order', '-created_at')
    
    context = get_base_context(request)
    context['carousel_images'] = carousel_images
    return render(request, 'aboutus/manage_carousel.html', context)

def add_aboutus_carousel_image(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        subtitle = request.POST.get('subtitle')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        image = request.FILES.get('image')
        
        if title and image:
            AboutUsCarousel.objects.create(
                title=title,
                subtitle=subtitle,
                order=order,
                is_active=is_active,
                image=image
            )
            messages.success(request, "About Us carousel image added successfully.")
        else:
            messages.error(request, "Please provide both title and image.")
            
    return redirect('manage_aboutus_carousel')

def update_aboutus_carousel_image(request, image_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    try:
        carousel_image = AboutUsCarousel.objects.get(id=image_id)
        if request.method == 'POST':
            carousel_image.title = request.POST.get('title')
            carousel_image.subtitle = request.POST.get('subtitle')
            carousel_image.order = request.POST.get('order', 0)
            carousel_image.is_active = request.POST.get('is_active') == 'on'
            
            if 'image' in request.FILES:
                carousel_image.image = request.FILES['image']
                
            carousel_image.save()
            messages.success(request, "About Us carousel image updated successfully.")
            
    except AboutUsCarousel.DoesNotExist:
        messages.error(request, "Carousel image not found.")
        
    return redirect('manage_aboutus_carousel')

def delete_aboutus_carousel_image(request, image_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    try:
        carousel_image = AboutUsCarousel.objects.get(id=image_id)
        carousel_image.delete()
        messages.success(request, "About Us carousel image deleted successfully.")
        
    except AboutUsCarousel.DoesNotExist:
        messages.error(request, "Carousel image not found.")
        
    return redirect('manage_aboutus_carousel')

def manage_uga_carousel(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    carousel_images = UGACarousel.objects.all().order_by('order', '-created_at')
    
    context = get_base_context(request)
    context['carousel_images'] = carousel_images
    return render(request, 'uga/manage_carousel.html', context)

def add_uga_carousel_image(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        subtitle = request.POST.get('subtitle')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        image = request.FILES.get('image')
        
        if title and image:
            UGACarousel.objects.create(
                title=title,
                subtitle=subtitle,
                order=order,
                is_active=is_active,
                image=image
            )
            messages.success(request, "UGA carousel image added successfully.")
        else:
            messages.error(request, "Please provide both title and image.")
            
    return redirect('manage_uga_carousel')

def update_uga_carousel_image(request, image_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    try:
        carousel_image = UGACarousel.objects.get(id=image_id)
        if request.method == 'POST':
            carousel_image.title = request.POST.get('title')
            carousel_image.subtitle = request.POST.get('subtitle')
            carousel_image.order = request.POST.get('order', 0)
            carousel_image.is_active = request.POST.get('is_active') == 'on'
            
            if 'image' in request.FILES:
                carousel_image.image = request.FILES['image']
                
            carousel_image.save()
            messages.success(request, "UGA carousel image updated successfully.")
            
    except UGACarousel.DoesNotExist:
        messages.error(request, "Carousel image not found.")
        
    return redirect('manage_uga_carousel')

def delete_uga_carousel_image(request, image_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    try:
        carousel_image = UGACarousel.objects.get(id=image_id)
        carousel_image.delete()
        messages.success(request, "UGA carousel image deleted successfully.")
        
    except UGACarousel.DoesNotExist:
        messages.error(request, "Carousel image not found.")
        
    return redirect('manage_uga_carousel')

def manage_research_carousel(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    carousel_images = ResearchCarousel.objects.all().order_by('order', '-created_at')
    
    context = get_base_context(request)
    context['carousel_images'] = carousel_images
    return render(request, 'research/manage_carousel.html', context)

def add_research_carousel_image(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        subtitle = request.POST.get('subtitle')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        image = request.FILES.get('image')
        
        if title and image:
            ResearchCarousel.objects.create(
                title=title,
                subtitle=subtitle,
                order=order,
                is_active=is_active,
                image=image
            )
            messages.success(request, "Research carousel image added successfully.")
        else:
            messages.error(request, "Please provide both title and image.")
            
    return redirect('manage_research_carousel')

def update_research_carousel_image(request, image_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    try:
        carousel_image = ResearchCarousel.objects.get(id=image_id)
        if request.method == 'POST':
            carousel_image.title = request.POST.get('title')
            carousel_image.subtitle = request.POST.get('subtitle')
            carousel_image.order = request.POST.get('order', 0)
            carousel_image.is_active = request.POST.get('is_active') == 'on'
            
            if 'image' in request.FILES:
                carousel_image.image = request.FILES['image']
                
            carousel_image.save()
            messages.success(request, "Research carousel image updated successfully.")
            
    except ResearchCarousel.DoesNotExist:
        messages.error(request, "Carousel image not found.")
        
    return redirect('manage_research_carousel')

def delete_research_carousel_image(request, image_id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    try:
        carousel_image = ResearchCarousel.objects.get(id=image_id)
        carousel_image.delete()
        messages.success(request, "Research carousel image deleted successfully.")
        
    except ResearchCarousel.DoesNotExist:
        messages.error(request, "Carousel image not found.")
        
    return redirect('manage_research_carousel')