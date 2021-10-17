from rest_framework import routers
from rest_framework.routers import APIRootView


class PrivatePoELadder(APIRootView):
    pass


class LadderRouter(routers.DefaultRouter):
    APIRootView = PrivatePoELadder
