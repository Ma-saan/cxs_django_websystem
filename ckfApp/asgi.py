# ckfApp/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import schedule_manager.routin

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ckfApp.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            schedule_manager.routing.websocket_urlpatterns
        )
    ),
})
