from django.db import models
from django.contrib.auth.models import User
from askbot.models import MarkedTag

#field to store "subscribed wildcard tags"
User.add_to_class('subscribed_tags', models.TextField(blank = True))
