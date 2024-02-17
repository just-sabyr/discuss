"""Defines URL patterns for links app."""

from .views import HomeView, NewSubmissionView, SubmissionDetailView, NewCommentView, NewCommentReplyView, UpvoteSubmissionView, RemoveUpvoteFromSubmissionView
from django.urls import path

app_name='links'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('new-submission/', NewSubmissionView.as_view(), name='new-submission'),
    path('submission/<int:pk>/', SubmissionDetailView.as_view(), name='submission-detail'),
    path('new-comment/', NewCommentView.as_view(), name='new-comment'),
    path('new-comment-reply/', NewCommentReplyView.as_view(), name='new-comment-reply'),
    path('upvote/<int:link_pk>/', UpvoteSubmissionView.as_view(), name='upvote-submission'),
    path('upvote/<int:link_pk>/remove/', RemoveUpvoteFromSubmissionView.as_view(), name='remove-upvote')
]