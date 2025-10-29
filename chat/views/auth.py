from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_not_required


@login_not_required
class LoginView(auth_views.LoginView):
    template_name = "chat/login.html"
    pass
