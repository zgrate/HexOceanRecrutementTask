from django.urls import path, re_path

from images import views
from images.views import ImageView, ImageManage, ImageAdmin, ImageExpire

urlpatterns = [
    # path("all/", views.ImageView.as_view(), name=""),
    path("", ImageAdmin.as_view()),
    path("view/<str:file_name>", ImageView.as_view(), name="img_view"),
    path("view/<str:file_name>/<str:size>", ImageView.as_view()),
    path("expire", ImageExpire.as_view()),

    path('manage/', ImageManage.as_view())
]