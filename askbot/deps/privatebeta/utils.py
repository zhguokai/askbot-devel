from models import InviteRequest

def get_email_from_code(code):
    try:
        invite = InviteRequest.objects.get(invitation_code=code)
        return invite.email
    except:
        return None
