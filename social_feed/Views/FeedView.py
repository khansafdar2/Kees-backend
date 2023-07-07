
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi
from ecomm_app.pagination import StandardResultSetPagination
from social_feed.BusinessLogic.FeedGenerationListener import generate_feed
from social_feed.models import Feed
from social_feed.Serializers.FeedSerializer import FeedSerializer, FeedListSerializer
from rest_framework import exceptions
from datetime import datetime


class FeedListView(ListCreateAPIView):
    serializer_class = FeedListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        try:
            access = AccessApi(self.request.user, "socialfeed")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            queryset = Feed.objects.filter(deleted=False)

            # Post Entry in Logs
            action_performed = self.request.user.username + " get list of feeds"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)
            return queryset

        except Exception as e:
            print(e)
            raise exceptions.ParseError(str(e))


class FeedView(APIView):
    def post(self, request):
        access = AccessApi(self.request.user, "socialfeed")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        serializer = FeedSerializer(data=request_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            feed = Feed.objects.filter(id=serializer.data['id']).first()
            generate_feed(feed)

            # Post Entry in Logs
            action_performed = self.request.user.username + f" create feed with id no. {serializer.data['id']}"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)

    def put(self, request):
        access = AccessApi(self.request.user, "socialfeed")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        try:
            obj_id = request_data['id']
        except Exception as e:
            print(e)
            return Response({'detail': 'id is missing'}, status=404)

        feed = Feed.objects.filter(id=obj_id).first()
        serializer = FeedSerializer(feed, data=request_data)

        if serializer.is_valid():
            serializer.save()

            feed = Feed.objects.filter(id=obj_id).first()
            generate_feed(feed)

            # Post Entry in Logs
            action_performed = self.request.user.username + f" update {obj_id} feed"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)


class FeedDetailView(APIView):
    def get(self, request, pk):
        try:
            access = AccessApi(self.request.user, "socialfeed")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            feed = Feed.objects.filter(id=pk).first()
            serializer = FeedSerializer(feed)

            # Post Entry in Logs
            action_performed = self.request.user.username + f" get {pk} feed detail"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(serializer.data, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=422)

    def delete(self, request, pk):
        access = AccessApi(self.request.user, "socialfeed")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        Feed.objects.filter(id=pk).update(deleted=True, deleted_at=datetime.now())

        # Post Entry in Logs
        action_performed = self.request.user.username + f" delete {pk} feed"
        SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

        return Response({"detail": "Deleted Feed Successfully"}, status=200)
