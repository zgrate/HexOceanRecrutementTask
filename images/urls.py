from django.urls import path

from images.views import ImageView, ImageAdmin, ImageExpire

urlpatterns = [
    # path("all/", views.ImageView.as_view(), name=""),
    path("", ImageAdmin.as_view()),
    path("<str:file_name>", ImageView.as_view(), name="img_view"),
    path("<str:file_name>/<str:size>", ImageView.as_view()),
    path("expire/", ImageExpire.as_view()),

    # path('', ImageManage.as_view())
]