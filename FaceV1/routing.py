from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import FaceDL.routing
import Control.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            FaceDL.routing.websocket_urlpatterns
            + Control.routing.websocket_urlpatterns)
    ),

})
