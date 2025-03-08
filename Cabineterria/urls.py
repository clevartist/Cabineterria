from django.contrib import admin
from django.urls import path
from .views import Home, CabinetView, BuildCabinet, Login, Signup, Logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Home.as_view(), name='home'),
    path('cabinet/<int:pk>/', CabinetView.as_view(), name='cabinet'),
    path('build/', BuildCabinet.as_view(), name='build_cabinet'),
    path('login/', Login.as_view(), name='login'),
    path('signup/', Signup.as_view(), name='signup'),
    path('logout/', Logout.as_view(), name='logout'),
]
