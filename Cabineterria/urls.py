from django.contrib import admin
from django.urls import path, re_path
from .views import Home, CabinetView, BuildCabinet, Login, Signup, Logout, Profile, Answer

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Home.as_view(), name='home'),
    path('build/', BuildCabinet.as_view(), name="build_cabinet"),
    path('cabinet/<int:cabinet_id>/answer/', Answer.as_view(), name='answer_questions'),
    re_path(r'^cabinet/(?P<cabinet_path>.+)/build/$', BuildCabinet.as_view(), name='build_subcabinet'),
    re_path(r'^cabinet/(?P<cabinet_path>.+)/$', CabinetView.as_view(), name='cabinet'),
    path('login/', Login.as_view(), name='login'),
    path('signup/', Signup.as_view(), name='signup'),
    path('logout/', Logout.as_view(), name='logout'),
    path('profile/<str:username>/', Profile.as_view(), name='profile'),
]