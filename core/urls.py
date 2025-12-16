from UserApp.views import index
from core.views import TravelerViewSet , TripViewSet
from django.urls import path
from rest_framework.routers import DefaultRouter



# urlpatterns = [
#     path('', index, name='core-index')
# ]


router = DefaultRouter()
router.register(r"travelers", TravelerViewSet, basename="travelers")
router.register("trips", TripViewSet, basename="trip")


urlpatterns = router.urls