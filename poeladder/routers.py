
from rest_framework.routers import APIRootView
from rest_framework import routers


class LadderRouter(routers.DefaultRouter):
    APIRootView = LadderTestAPIView
