from django import forms
from privatebeta.models import InviteRequest

class InviteRequestForm(forms.ModelForm):
    class Meta:
        model = InviteRequest
        fields = ['email']

class InviteField(forms.BooleanField):
    '''Field for a invite'''

    def __init__(self, invite, **kwargs):
        self.invite = invite
        if not kwargs.get('label', None ):
            kwargs['label'] = self.invite.__unicode__()

        kwargs['required'] = False
        super(InviteField, self).__init__(**kwargs)
        self.widget.attrs = {'value': self.invite.id}
        #do something with the widget

class InviteApprovalForm(forms.Form):
    '''Form that mimics django admin form'''
    select_all = forms.BooleanField(required=False)

    def __init__(self, invites, *args, **kwargs):
        super(InviteApprovalForm, self).__init__(*args, **kwargs)
        if invites:
            self.invites = invites
            self.build_fields()
        else:
            self.invites = None
            self.build_fields(self.data)


    def build_fields(self, post=None):
        '''Builds all the fields'''
        if post:
            for invite_id in post.values():
                try:
                    invite = InviteRequest.objects.get(id=invite_id)
                    self.fields['invite_%d' % invite.id] = InviteField(invite)
                except:
                    pass
        elif self.invites:
            for invite in self.invites:
                self.fields['invite_%d' % invite.id] = InviteField(invite)
        else:
            pass
