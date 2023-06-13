from django.urls import path, include
from .views import RegisterView

urlpatterns = [
    path('auth/', include('dj_rest_auth.urls')),
    path('register/', RegisterView.as_view())
]





# login / logout  ---> dj-rest-auth
# register ---> (url -view - serializer)
#generate token with signal return token in registerview
# return user data in login response