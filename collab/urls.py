from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response

class PostList(APIView):
    def get(self, request):
        return Response([])

urlpatterns = [
    path('posts/', PostList.as_view(), name='collab-posts'),
]
