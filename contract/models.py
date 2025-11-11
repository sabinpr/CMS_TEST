from django.db import models, transaction
from django.contrib.auth import get_user_model
from users.models import Department
from django.core.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()

PAYMENT_TERMS = [
    ("one_time_payment", "One Time Payment"),
    ("installment", "Installment"),
    ("milestone_based", "Milestone Based"),
    ("others", "Others"),
]

RENEWAL_TERMS = [
    ("renewable_fixed", "Renewable (fixed terms)"),
    ("not_renewable", "Not Renewable"),
    ("on_request", "On Request"),
]

CONTRACT_STATUS = [
    ("draft", "Draft"),
    ("submitted", "Submitted"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("returned", "Returned"),
]


class ContractType(models.Model):
    type_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.type_name


def contract_document_path(instance, filename):
    contract_id = instance.contract.id if instance.contract_id else "unsaved"
    return f"contracts/{contract_id}/{filename}"


class ContractDocument(models.Model):
    contract = models.ForeignKey(
        "Contract", on_delete=models.CASCADE, related_name="documents"
    )
    file = models.FileField(upload_to=contract_document_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.contract.contract_title} - {self.file.name}"


class Contract(models.Model):
    contract_code = models.CharField(
        max_length=20, unique=True, blank=True, help_text="Auto-generated contract code"
    )
    contract_title = models.CharField(max_length=200)
    vendor_name = models.CharField(max_length=200)
    contract_type = models.ForeignKey(ContractType, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    payment_terms = models.CharField(max_length=50, choices=PAYMENT_TERMS)
    estimated_contract_value = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    renewal_terms = models.CharField(
        max_length=30, choices=RENEWAL_TERMS, default="not_renewable"
    )
    scope_of_work = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS, default="draft")
    remarks = models.TextField(
        blank=True, null=True, help_text="For rejected or returned contracts"
    )

    legal_officer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="legal_officer_contracts",
        limit_choices_to={"role": "legal_reviewer"},
    )
    department_head = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="department_head_contracts",
        limit_choices_to={"role": "department_head"},
    )
    signatory = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="signatory_contracts",
        limit_choices_to={"role": "signatory"},
    )

    instructions_for_reviewers = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_contracts"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="updated_contracts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contract"
        verbose_name_plural = "Contracts"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["end_date"]),
            models.Index(fields=["department"]),
        ]

    def __str__(self):
        return self.contract_title

    def clean(self):
        """Validate dates and status"""
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")

        # Only enforce past date restriction on new contracts
        if (
            self._state.adding
            and self.end_date < timezone.now().date()
            and self.status == "draft"
        ):
            raise ValidationError("Contract end date cannot be in the past.")

    @property
    def total_days(self):
        return (self.end_date - self.start_date).days

    @property
    def is_active(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date and self.status == "approved"

    @property
    def days_remaining(self):
        today = timezone.now().date()
        return max((self.end_date - today).days, 0)

    @property
    def is_expiring_soon(self):
        return 0 < self.days_remaining <= 30

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Safe auto-generate contract code with transaction to avoid race conditions"""
        if not self.contract_code:
            current_year = timezone.now().year
            # Lock the table for safe counting
            last_contract = (
                Contract.objects.select_for_update()
                .filter(created_at__year=timezone.now().year)
                .order_by("id")
                .last()
            )
            count = (last_contract.id if last_contract else 0) + 1
            self.contract_code = f"CON-{current_year}-{count:04d}"
        super().save(*args, **kwargs)

    def set_status(self, new_status, user=None, remarks=None):
        """Change status safely and log history"""
        valid_transitions = {
            "draft": ["submitted"],
            "submitted": ["approved", "rejected", "returned"],
            "returned": ["submitted", "draft"],
            "approved": [],
            "rejected": [],
        }
        if new_status not in valid_transitions.get(self.status, []):
            raise ValidationError(
                f"Cannot transition from {self.status} to {new_status}"
            )

        old_status = self.status
        self.status = new_status
        if remarks:
            self.remarks = remarks
        if user:
            self.updated_by = user
        self.save()

        # Log status change
        ContractStatusHistory.objects.create(
            contract=self,
            old_status=old_status,
            new_status=new_status,
            changed_by=user,
            remarks=remarks,
        )


class ContractStatusHistory(models.Model):
    """Tracks status changes for auditing"""

    contract = models.ForeignKey(
        Contract, on_delete=models.CASCADE, related_name="status_history"
    )
    old_status = models.CharField(max_length=20, choices=CONTRACT_STATUS)
    new_status = models.CharField(max_length=20, choices=CONTRACT_STATUS)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    remarks = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]


class ContractComment(models.Model):
    """Comments made by assigned users on a contract"""

    contract = models.ForeignKey(
        Contract, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user} on {self.contract.contract_title}"

    def clean(self):
        """Ensure only assigned users can comment"""
        allowed_users = {
            self.contract.legal_officer,
            self.contract.department_head,
            self.contract.signatory,
            self.contract.created_by,
        }
        allowed_users.discard(None)  # remove None values

        if self.user not in allowed_users:
            raise ValidationError("You are not allowed to comment on this contract.")
