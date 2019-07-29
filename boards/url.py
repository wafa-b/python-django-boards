from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    # path('boards/<int:id>/',views.boards_topic,name='boards_topic'),
    path('boards/<int:id>/',views.TopicListView.as_view(),name='boards_topic'),
    path('boards/<int:id>/new/',views.new_topic,name='new_topic'),
    # path('boards/<int:id>/topics/<int:topic_id>/',views.topic_posts,name='topic_posts'),
    path('boards/<int:id>/topics/<int:topic_id>/',views.PostListView.as_view(),name='topic_posts'),
    path('boards/<int:id>/topics/<int:topic_id>/reply/',views.reply_topic,name='reply_topic'),
    path('boards/<int:id>/topics/<int:topic_id>/posts/<int:post_id>/edit/',views.PostUpdateView.as_view(), name='edit_post'),


]
