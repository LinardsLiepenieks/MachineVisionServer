from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    #re_path(r'wsapi/$', consumers.YourConsumer.as_asgi()),
    re_path(r'wsapi/users/$', consumers.UserConsumer.as_asgi()),
    re_path(r'wsapi/machines/$', consumers.MachineConsumer.as_asgi()),
]
