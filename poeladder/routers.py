from rest_framework import routers
from rest_framework.routers import APIRootView


class PrivatePOELadderApi(APIRootView):
    """Simple API for current registered PoE characters"""


class LadderRouter(routers.DefaultRouter):
    APIRootView = PrivatePOELadderApi
