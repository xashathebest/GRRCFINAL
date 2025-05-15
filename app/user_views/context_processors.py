from .models import FooterInfo,HeroSection, MissionVision, KeyObjectives,DynamicBannerImage,ContentCard,TeamMember, ThemeSettings, FooterLink
# from django.conf import settings
# from .models import WebsiteSettings, HeroSection, Footer, FooterLink

def footer_context(request):
    from .models import FooterInfo, FooterLink
    
    # Get footer information
    try:
        footer = FooterInfo.objects.last()
    except:
        footer = None
    
    # Get footer links by category
    try:
        footer_quick_links = FooterLink.objects.filter(category='quick_links').order_by('order')
        resources = FooterLink.objects.filter(category='resources').order_by('order')
        social_links = FooterLink.objects.filter(category='social').order_by('order')
    except:
        footer_quick_links = []
        resources = []
        social_links = []
    
    return {
        'footer': footer,
        'footer_quick_links': footer_quick_links,
        'resources': resources,
        'social_links': social_links
    }

def hero_section_context(request):
    hero = HeroSection.objects.first()
    return {
        'hero_section': hero
    }

def mission_vision_context(request):
    mission_vision = MissionVision.objects.first()

    mission_points_list = []
    vision_points_list = []

    if mission_vision:
        if mission_vision.mission_points:
            mission_points_list = [point.strip() for point in mission_vision.mission_points.split(',') if point.strip()]
        if mission_vision.vision_points:
            vision_points_list = [point.strip() for point in mission_vision.vision_points.split(',') if point.strip()]

    return {
        'mission_vision': mission_vision,
        'mission_points': mission_points_list,
        'vision_points': vision_points_list,
    }

def key_objectives_context(request):
    key_objectives = KeyObjectives.objects.first()  # Or filter() if you expect multiple
    return {
        'key_objectives': key_objectives
    }

def banner_images(request):
    try:
        banner = DynamicBannerImage.objects.latest('uploaded_at')
    except DynamicBannerImage.DoesNotExist:
        banner = None
    return {
        'banner': banner
    }

def content_cards_context(request):
    # Using the model's default ordering (from Meta class)
    cards = ContentCard.objects.all()
    return {'content_cards': cards}


def team_members(request):
    director = TeamMember.objects.filter(role__iexact="Director").first()
    return {
        'team_members': TeamMember.objects.all(),
        'director': director,   
    }

def theme_settings(request):
    active_theme = ThemeSettings.objects.filter(is_active=True).first()
    if active_theme:
        return {
            'theme': {
                'primary_color': active_theme.primary_color,
                'secondary_color': active_theme.secondary_color,
                'button_color': active_theme.button_color,
                'button_hover_color': active_theme.button_hover_color,
                'text_color': active_theme.text_color,
                'background_color': active_theme.background_color,
                'nav_background': active_theme.nav_background,
                'nav_text_color': active_theme.nav_text_color,
                'nav_hover_color': active_theme.nav_hover_color,
                'success_color': active_theme.success_color,
                'warning_color': active_theme.warning_color,
                'error_color': active_theme.error_color,
            }
        }
    return {'theme': None}

def carousel_images(request):
    """
    Provides carousel background images to all templates
    """
    from .models import CarouselImage
    images = CarouselImage.objects.filter(is_active=True).order_by('order', 'created_at')
    return {'carousel_images': images}



