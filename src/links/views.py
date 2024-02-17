from django.utils import timezone

from typing import Any
from django.http import HttpResponse
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, TemplateView, DetailView, View

from links.models import Link, Comment
from links.forms import CommentModelForm


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super(HomeView, self).get_context_data(**kwargs)

        now = timezone.now()
        submissions = Link.objects.all()
        for submission in submissions:
            num_votes = submission.upvotes.count()
            num_comments = submission.comment_set.count()

            date_diff = now - submission.submitted_on
            number_of_days_since_submission = date_diff.days

            submission.rank = num_votes + num_comments - number_of_days_since_submission
        
        sorted_submissions = sorted(submissions, key=lambda x: x.rank, reverse=True)
        ctx['submissions'] = sorted_submissions

        return ctx


class NewSubmissionView(CreateView):
    model = Link
    fields = (
        'title', 'url'
    )   

    template_name= 'new_submission.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(NewSubmissionView, self).dispatch(request, *args, **kwargs)
    
    # defined and not inherited from CreateView because we need to set submitted_by field
    def form_valid(self, form):
        new_link = form.save(commit=False)          
        new_link.submitted_by = self.request.user
        new_link.save()

        self.object = new_link
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse('links:submission-detail', kwargs={'pk': self.object.pk})
    
    
class SubmissionDetailView(DetailView):
    model = Link
    template_name = 'submission_detail.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super(SubmissionDetailView, self).get_context_data(**kwargs)

        submission_comments = Comment.objects.filter(commented_on=self.object, in_reply_to__isnull=True)
        # in_reply_to__isnull allows only the comments that are no a reply

        ctx['comments'] = submission_comments

        ctx['comment_form'] = CommentModelForm(initial={'link_pk':self.object.pk})

        return ctx
    


class NewCommentView(CreateView):
    form_class = CommentModelForm
    http_method_names = ('post',)
    template_name = 'comment.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NewCommentView, self).dispatch(*args, **kwargs)

    def form_valid(self, form) -> HttpResponse:
        parent_link = Link.objects.get(pk=form.cleaned_data['link_pk'])
        new_comment = form.save(commit=False)
        new_comment.commented_on = parent_link
        new_comment.commented_by = self.request.user

        new_comment.save()

        return HttpResponseRedirect(reverse('links:submission-detail', kwargs={'pk': parent_link.pk}))
    
    def get_initial(self):
        initial_data = super(NewCommentView, self).get_initial()
        initial_data['link_pk'] = self.request.GET['link_pk']

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super(NewCommentView, self).get_context_data(**kwargs)
        ctx['submission'] = Link.objects.get(pk=self.request.GET['link_pk'])

        return ctx


class NewCommentReplyView(CreateView):
    form_class = CommentModelForm
    template_name = 'comment_reply.html' # a better way to do this is to use interactive javascript

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NewCommentReplyView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super(NewCommentReplyView, self).get_context_data(**kwargs)
        ctx['parent_comment'] = Comment.objects.get(pk=self.request.GET['parent_comment_pk'])

        return ctx
    
    """
    initial_data: initial data created by an empty form
    allows changing initial data without trigerring validation so as to avoid exceptions
    if the initial data was changed directly, we could have received invalid form errors.
    """
    def get_initial(self) -> dict[str, Any]:
        initial_data = super(NewCommentReplyView, self).get_initial()

        link_pk = self.request.GET['link_pk']
        initial_data['link_pk'] = link_pk

        parent_comment_pk = self.request.GET['parent_comment_pk']
        initial_data['parent_comment_pk'] = parent_comment_pk

        # initial_data is mutable, therefore even if the initial_data was stored under an another name in the original form
        # the previous line would work as expected
 
        return initial_data
    
    def form_valid(self, form):
        parent_link = Link.objects.get(pk=form.cleaned_data['link_pk'])
        parent_comment = Comment.objects.get(pk=form.cleaned_data['parent_comment_pk'])

        new_comment = form.save(commit=False)
        new_comment.commented_on = parent_link
        new_comment.in_reply_to = parent_comment
        new_comment.commented_by = self.request.user

        new_comment.save()

        return HttpResponseRedirect(reverse('links:submission-detail', kwargs={'pk': parent_link.pk}))
    

class UpvoteSubmissionView(View):
    def get(self, request, link_pk, **kwargs):
        link = Link.objects.get(pk=link_pk)
        link.upvotes.add(request.user)

        return HttpResponseRedirect(reverse('links:home'))
    

class RemoveUpvoteFromSubmissionView(View):
    def get(self, request, link_pk, **kwargs):
        link = Link.objects.get(pk=link_pk)
        link.upvotes.remove(request.user)

        return HttpResponseRedirect(reverse('links:home'))