from django.db import models
from django.conf import settings


class LocomotiveType(models.Model):
    """Locomotive model/type master record (WAG9, WAP7, WAG12B, etc.)"""
    STATUS_CHOICES = [
        ('Production', 'Production'), ('Testing', 'Testing'),
        ('Concept', 'Concept'), ('Legacy', 'Legacy'), ('Under Review', 'Under Review'),
    ]
    model_id        = models.CharField(max_length=30, unique=True)
    name            = models.CharField(max_length=120)
    loco_class      = models.CharField(max_length=60)  # Heavy Freight, Electric High Speed...
    status          = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Production')
    engine_power    = models.CharField(max_length=30)  # e.g. '6000 kW', '4400 HP'
    engine_type     = models.CharField(max_length=60, blank=True)
    manufacturer    = models.CharField(max_length=80, blank=True)
    year_introduced = models.PositiveSmallIntegerField(null=True, blank=True)
    notes           = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    updated_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='loco_updates'
    )

    class Meta:
        ordering = ['model_id']

    def __str__(self):
        return f'{self.model_id} — {self.name}'


class ComponentCatalog(models.Model):
    """Standard component/part master"""
    CATEGORY_CHOICES = [
        ('Mechanical', 'Mechanical'), ('Electrical', 'Electrical'),
        ('Pneumatic', 'Pneumatic'), ('Electronic', 'Electronic'), ('Structural', 'Structural'),
    ]
    STATUS_CHOICES = [
        ('Active', 'Active'), ('Obsolete', 'Obsolete'), ('Under Review', 'Under Review'),
    ]
    part_number     = models.CharField(max_length=40, unique=True)
    description     = models.CharField(max_length=200)
    category        = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    status          = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Active')
    supplier        = models.CharField(max_length=100, blank=True)
    unit            = models.CharField(max_length=20, default='Nos')
    unit_price      = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    applicable_locos = models.ManyToManyField(LocomotiveType, blank=True, related_name='components')
    notes           = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['part_number']

    def __str__(self):
        return f'{self.part_number} — {self.description}'


class LookupCategory(models.Model):
    """Global enumeration/lookup category (Status codes, Material types, etc.)"""
    name = models.CharField(max_length=80, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Lookup Categories'

    def __str__(self):
        return self.name


class LookupItem(models.Model):
    """Individual lookup value within a category"""
    category  = models.ForeignKey(LookupCategory, on_delete=models.CASCADE, related_name='items')
    label     = models.CharField(max_length=80)
    value     = models.CharField(max_length=80)
    color     = models.CharField(max_length=20, default='#6b7280')  # hex
    order     = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'label']
        unique_together = [['category', 'value']]

    def __str__(self):
        return f'{self.category.name} / {self.label}'


class MasterDataChangeLog(models.Model):
    """Audit trail for master data changes"""
    ACTION_CHOICES = [('modified', 'Modified'), ('added', 'Added'), ('deprecated', 'Deprecated')]
    action      = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name  = models.CharField(max_length=50)
    object_id   = models.CharField(max_length=40)
    description = models.CharField(max_length=200)
    detail      = models.CharField(max_length=200, blank=True)
    user        = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='master_changes'
    )
    timestamp   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.action} {self.model_name} by {self.user} at {self.timestamp}'
