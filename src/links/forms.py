from django import forms

from links.models import Comment

from django_recaptcha.fields import ReCaptchaField

class CommentModelForm(forms.ModelForm):
    link_pk = forms.IntegerField(widget=forms.HiddenInput) # widget is used for stylings
    parent_comment_pk = forms.IntegerField(widget=forms.HiddenInput, required=False)

    captcha = ReCaptchaField()
    
    class Meta:
        model = Comment
        fields = {
            'body',
        }