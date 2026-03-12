"""Core serializers - PLW EDMS + LDO."""
from rest_framework import serializers
from apps.core.models import User, Section


class SectionSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'code', 'name', 'description', 'parent', 'parent_name', 'is_active']


class UserSerializer(serializers.ModelSerializer):
    section_name = serializers.CharField(source='section.name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'employee_code',
            'designation', 'section', 'section_name', 'role', 'role_display',
            'is_active', 'is_staff', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=10)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'full_name', 'employee_code', 'designation', 'section', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
