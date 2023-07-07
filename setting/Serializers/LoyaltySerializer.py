
from setting.models import LoyaltySetting, Rule
from rest_framework import serializers


class SettingSerializer(serializers.ModelSerializer):
    rules = serializers.ListField(allow_null=True, allow_empty=True, required=False)

    class Meta:
        model = LoyaltySetting
        fields = '__all__'

    def create(self, validated_data):
        validated_data = self.validated_data
        rules = validated_data.pop('rules', [])

        if "id" in validated_data:
            LoyaltySetting.objects.filter(id=validated_data['id']).update(**validated_data)
        else:
            LoyaltySetting.objects.create(**validated_data)

        for rule in rules:
            if 'start_date' in rule or 'end_date' in rule:
                if not rule['start_date'] or not rule['end_date']:
                    rule.pop('start_date')
                    rule.pop('end_date')

            if 'id' in rule:
                Rule.objects.filter(id=rule['id']).update(**rule)
            else:
                Rule.objects.create(**rule)

        return validated_data


class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = '__all__'
