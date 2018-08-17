
from rest_framework.routers import APIRootView
from rest_framework import routers

class LadderTestAPIView(APIRootView):
    pass

class LadderRouter(routers.DefaultRouter):
    APIRootView = LadderTestAPIView