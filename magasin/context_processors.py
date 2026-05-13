from .models import Category


def categories_context(request):
    return {
        'categories': Category.objects.all()
    }

def lang_context(request):
    return {
        'lang_magasin': request.session.get('lang_magasin', 'fr')
    }
