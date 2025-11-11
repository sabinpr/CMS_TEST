from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Contract,
    ContractDocument,
    ContractType,
    ContractStatusHistory,
    ContractComment,
)

User = get_user_model()


class ContractTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractType
        fields = ["id", "type_name"]


class ContractDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractDocument
        fields = ["id", "file", "uploaded_at"]
        read_only_fields = ["uploaded_at"]


class ContractDocumentUploadSerializer(serializers.ModelSerializer):
    """Use this serializer for uploading new documents"""

    class Meta:
        model = ContractDocument
        fields = ["id", "file"]


class ContractStatusHistorySerializer(serializers.ModelSerializer):
    changed_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ContractStatusHistory
        fields = ["id", "old_status", "new_status", "changed_at", "changed_by"]
        read_only_fields = ["changed_at", "changed_by"]


class ContractSerializer(serializers.ModelSerializer):
    contract_type = ContractTypeSerializer(read_only=True)
    documents = ContractDocumentSerializer(many=True, read_only=True)
    status_history = ContractStatusHistorySerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    updated_by = serializers.StringRelatedField(read_only=True)

    payment_terms_display = serializers.CharField(
        source="get_payment_terms_display", read_only=True
    )
    renewal_terms_display = serializers.CharField(
        source="get_renewal_terms_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    contract_type_id = serializers.PrimaryKeyRelatedField(
        queryset=ContractType.objects.all(),
        source="contract_type",
        write_only=True,
    )
    legal_officer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="legal_reviewer"),
        source="legal_officer",
        write_only=True,
        required=False,
        allow_null=True,
    )
    department_head_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="department_head"),
        source="department_head",
        write_only=True,
        required=False,
        allow_null=True,
    )
    signatory_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="signatory"),
        source="signatory",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Contract
        fields = [
            "id",
            "contract_code",
            "contract_title",
            "vendor_name",
            "contract_type",
            "contract_type_id",
            "department",
            "start_date",
            "end_date",
            "payment_terms",
            "payment_terms_display",
            "estimated_contract_value",
            "renewal_terms",
            "renewal_terms_display",
            "scope_of_work",
            "status",
            "status_display",
            "remarks",
            "legal_officer_id",
            "department_head_id",
            "signatory_id",
            "legal_officer",
            "department_head",
            "signatory",
            "documents",
            "status_history",
            "instructions_for_reviewers",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "contract_code",
            "status",
            "documents",
            "status_history",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "legal_officer",
            "department_head",
            "signatory",
        ]

    def validate(self, data):
        start = data.get("start_date") or getattr(self.instance, "start_date", None)
        end = data.get("end_date") or getattr(self.instance, "end_date", None)
        if start and end and end < start:
            raise serializers.ValidationError("End date cannot be before start date.")
        return data

    def create(self, validated_data):
        user = self.context.get("request").user if "request" in self.context else None
        if user:
            validated_data["created_by"] = user
            validated_data["updated_by"] = user
            if not validated_data.get("department") and hasattr(user, "department"):
                validated_data["department"] = user.department
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context.get("request").user if "request" in self.context else None
        if user:
            validated_data["updated_by"] = user
        return super().update(instance, validated_data)


class ContractCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ContractComment
        fields = ["id", "contract", "user", "comment", "created_at"]
        read_only_fields = ["id", "created_at", "user"]

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        comment = ContractComment(**validated_data)
        comment.clean()  # enforce permission validation
        comment.save()
        return comment
