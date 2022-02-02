from django.urls import path

from adventure import views

urlpatterns = [
    path("create-vehicle/", views.VehicleAPIView.as_view()),
    path("vehicle/<str:number_plate>/", views.VehicleAPIView.as_view()),
    path("create-service-area/", views.ServiceAreaAPIView.as_view()),
    path("start/", views.StartJourneyAPIView.as_view()),
    path('service-area/<int:kilometer>/', views.ServiceAreaAPIView.as_view()),
]
