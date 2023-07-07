
from rest_framework import serializers
from notification.models import FirebaseNotification, FirebaseNotificationHistory


class NotificationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirebaseNotification
        fields = ('id', 'message_title')


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirebaseNotification
        fields = '__all__'

    def create(self, validate_data):
        instance = FirebaseNotification.objects.create(**validate_data)
        return instance

    def update(self, instance, validate_data):
        data = self.initial_data
        FirebaseNotification.objects.filter(id=instance.id).update(**validate_data)
        return data


class NotificationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FirebaseNotificationHistory
        fields = '__all__'


class NotificationDetailSerializer(serializers.ModelSerializer):
    history = serializers.SerializerMethodField('get_history')

    class Meta:
        model = FirebaseNotification
        fields = '__all__'

    def get_history(self, obj):
        serializer_context = {'request': self.context.get('request')}
        data = FirebaseNotificationHistory.objects.filter(firebase_notification=obj, deleted=False)
        serializer = NotificationHistorySerializer(data, many=True, context=serializer_context)
        return serializer.data
