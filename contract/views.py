from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction, models
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import filters

from .models import Contract, ContractType, ContractDocument, ContractComment
from .serializers import (
    ContractSerializer,
    ContractTypeSerializer,
    ContractDocumentSerializer,
    ContractCommentSerializer,
)
from .permissions import IsProcurementOfficer, IsAdminOrReadOnly


class ContractTypeViewSet(viewsets.ModelViewSet):
    queryset = ContractType.objects.all()
    serializer_class = ContractTypeSerializer
    permission_classes = [IsAdminOrReadOnly]


class ContractDocumentViewSet(viewsets.ModelViewSet):
    queryset = ContractDocument.objects.all()
    serializer_class = ContractDocumentSerializer
    permission_classes = [IsProcurementOfficer]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["contract_code", "vendor_name", "contract_title"]
    ordering_fields = ["created_at", "end_date", "status"]

    def create(self, request, *args, **kwargs):
        contract_id = self.kwargs.get("contract_pk")
        contract = Contract.objects.get(pk=contract_id)

        files = request.FILES.getlist("files")
        if not files:
            return Response({"error": "No files provided."}, status=400)

        created_docs = []
        for file in files:
            doc = ContractDocument.objects.create(contract=contract, file=file)
            created_docs.append(doc)

        serializer = self.get_serializer(created_docs, many=True)
        return Response(serializer.data, status=201)


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [IsProcurementOfficer]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        contract = self.get_object()
        new_status = request.data.get("status")
        remarks = request.data.get("remarks")

        try:
            with transaction.atomic():
                contract.set_status(
                    new_status=new_status, user=request.user, remarks=remarks
                )
            return Response({"status": "status updated"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ContractCommentViewSet(viewsets.ModelViewSet):
    queryset = ContractComment.objects.all()
    serializer_class = ContractCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter comments by contract if nested under /contracts/{id}/comments/"""
        user = self.request.user
        queryset = ContractComment.objects.filter(
            contract__in=Contract.objects.filter(
                models.Q(legal_officer=user)
                | models.Q(department_head=user)
                | models.Q(signatory=user)
                | models.Q(created_by=user)
            )
        )
        contract_id = self.kwargs.get("contract_pk")  # <-- from nested router
        if contract_id:
            queryset = queryset.filter(contract_id=contract_id)
        return queryset

    def perform_create(self, serializer):
        contract_id = self.kwargs.get("contract_pk")
        contract = get_object_or_404(Contract, pk=contract_id)
        user = self.request.user

        allowed_users = {
            contract.legal_officer,
            contract.department_head,
            contract.signatory,
            contract.created_by,
        }
        allowed_users.discard(None)

        if user not in allowed_users:
            raise ValidationError("You are not authorized to comment on this contract.")

        serializer.save(user=user, contract=contract)
