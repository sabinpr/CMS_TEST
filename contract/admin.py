from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Contract, ContractDocument, ContractType, ContractStatusHistory


class ContractDocumentInline(admin.TabularInline):
    model = ContractDocument
    extra = 0
    readonly_fields = ("uploaded_at",)
    fields = ("file", "uploaded_at")


class ContractStatusHistoryInline(admin.TabularInline):
    model = ContractStatusHistory
    extra = 0
    readonly_fields = (
        "old_status",
        "new_status",
        "changed_by",
        "remarks",
        "changed_at",
    )
    fields = ("old_status", "new_status", "changed_by", "remarks", "changed_at")
    can_delete = False


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = (
        "contract_code",
        "contract_title",
        "vendor_name",
        "department",
        "contract_type",
        "status",
        "start_date",
        "end_date",
        "is_active",
        "days_remaining",
    )
    list_filter = ("status", "department", "contract_type")
    search_fields = ("contract_title", "vendor_name", "contract_code")
    readonly_fields = ("contract_code", "created_at", "updated_at")
    inlines = [ContractDocumentInline, ContractStatusHistoryInline]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "contract_code",
                    "contract_title",
                    "vendor_name",
                    "contract_type",
                    "department",
                    "start_date",
                    "end_date",
                    "payment_terms",
                    "estimated_contract_value",
                    "renewal_terms",
                    "scope_of_work",
                    "instructions_for_reviewers",
                )
            },
        ),
        (
            "Status & Roles",
            {
                "fields": (
                    "status",
                    "remarks",
                    "legal_officer",
                    "department_head",
                    "signatory",
                )
            },
        ),
        (
            "Audit",
            {
                "fields": (
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    actions = [
        "mark_as_submitted",
        "mark_as_approved",
        "mark_as_rejected",
        "mark_as_returned",
    ]

    def mark_as_submitted(self, request, queryset):
        for contract in queryset:
            try:
                contract.set_status("submitted", user=request.user)
            except ValidationError as e:
                self.message_user(request, f"{contract}: {e}", level="error")

    mark_as_submitted.short_description = "Mark selected contracts as Submitted"

    def mark_as_approved(self, request, queryset):
        for contract in queryset:
            try:
                contract.set_status("approved", user=request.user)
            except ValidationError as e:
                self.message_user(request, f"{contract}: {e}", level="error")

    mark_as_approved.short_description = "Mark selected contracts as Approved"

    def mark_as_rejected(self, request, queryset):
        for contract in queryset:
            try:
                contract.set_status("rejected", user=request.user)
            except ValidationError as e:
                self.message_user(request, f"{contract}: {e}", level="error")

    mark_as_rejected.short_description = "Mark selected contracts as Rejected"

    def mark_as_returned(self, request, queryset):
        for contract in queryset:
            try:
                contract.set_status("returned", user=request.user)
            except ValidationError as e:
                self.message_user(request, f"{contract}: {e}", level="error")

    mark_as_returned.short_description = "Mark selected contracts as Returned"


@admin.register(ContractType)
class ContractTypeAdmin(admin.ModelAdmin):
    list_display = ("type_name",)
    search_fields = ("type_name",)
