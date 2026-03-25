from django.db import models

# Create your models here.

class AccountingEntry(models.Model):

    class EntryType(models.TextChoices):
        JOURNAL = 'JO', 'Journal'
        OPENING = 'OP', 'Opening'
        ADJUSTMENT = 'AD', 'Adjustment'
        CLOSING = 'CL', 'Closing'

    class EntryState(models.TextChoices):
        DRAFT = 'DR', 'Draft'
        REGISTERED = 'RE', 'Registered'
        CANCELLED = 'CA', 'Cancelled'

    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    entry_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    type = models.CharField(
        max_length=2, 
        choices=EntryType.choices, 
        default=EntryType.JOURNAL
    )
    state = models.CharField(
        max_length=2, 
        choices=EntryState.choices, 
        default=EntryState.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['date'], name='idx_accounting_entry_date'),
            models.Index(fields=['state'], name='idx_accounting_entry_state'),
        ]
        verbose_name = "Asiento Contable"
        verbose_name_plural = "Asientos Contables"
        ordering = ['-date', '-id']

    def __str__(self):
        return self.description