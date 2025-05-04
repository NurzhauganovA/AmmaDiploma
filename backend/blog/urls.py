from django.urls import path
from . import views


urlpatterns = [
    path('', views.blog, name='blog'),
    path('<int:blog_id>', views.blog_detail, name='blog-detail'),

    path('like_comment/<int:pk>', views.LikeComment, name='like_comment'),
    path('dislike_comment/<int:pk>', views.DislikeComment, name='dislike_comment'),
    path('complain_comment/<int:pk>', views.ComplainComment, name='complain_comment')
]
