import constants
from django.conf.urls import path

from .views import CommandReceiveView

urlpatterns = [
    path ('bot/', constants.token, CommandReceiveView.as_view(), name='command'),

]