from django.db import models
from django.conf import settings

NODE_TYPE_CHOICES = [
    ('ASSEMBLY',    'Assembly'),
    ('SUBASSEMBLY', 'Sub-Assembly'),
    ('COMPONENT',   'Component'),
    ('PART',        'Part'),
]
CAT_CHOICES = [
    ('A', 'A - Safety Critical'),
    ('B', 'B - Important'),
    ('C', 'C - Normal'),
    ('D', 'D - General'),
    ('',  'Unclassified'),
]

class BOMTree(models.Model):
    loco_type   = models.CharField(max_length=20)
    variant     = models.CharField(max_length=60, blank=True)
    description = models.CharField(max_length=200, blank=True)
    is_active   = models.BooleanField(default=True)
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                    on_delete=models.SET_NULL, related_name='bom_trees_created')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'bom'
        ordering = ['loco_type', 'variant']
        unique_together = [['loco_type', 'variant']]

    def __str__(self):
        return f'{self.loco_type} {self.variant}'.strip()


class BOMNode(models.Model):
    tree        = models.ForeignKey(BOMTree, on_delete=models.CASCADE, related_name='nodes')
    parent      = models.ForeignKey('self', null=True, blank=True,
                    on_delete=models.SET_NULL, related_name='children')
    pl_number   = models.CharField(max_length=50, db_index=True)
    description = models.CharField(max_length=300, blank=True)
    node_type   = models.CharField(max_length=15, choices=NODE_TYPE_CHOICES, default='PART')
    inspection_category = models.CharField(max_length=1, choices=CAT_CHOICES, blank=True)
    safety_item = models.BooleanField(default=False)
    quantity    = models.DecimalField(max_digits=10, decimal_places=3, default=1)
    unit        = models.CharField(max_length=20, default='Nos')
    position    = models.FloatField(default=0)
    level       = models.PositiveSmallIntegerField(default=0)
    canvas_x    = models.FloatField(default=0)
    canvas_y    = models.FloatField(default=0)
    is_active   = models.BooleanField(default=True)
    remarks     = models.CharField(max_length=300, blank=True)
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                    on_delete=models.SET_NULL, related_name='bom_nodes_created')
    updated_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                    on_delete=models.SET_NULL, related_name='bom_nodes_updated')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'bom'
        ordering = ['level', 'position', 'pl_number']

    def __str__(self):
        return f'{self.tree} / {self.pl_number}'

    def recalculate_level(self):
        depth, node = 0, self
        while node.parent_id is not None:
            node = node.parent
            depth += 1
            if depth > 20:
                break
        self.level = depth


class BOMSnapshot(models.Model):
    tree          = models.ForeignKey(BOMTree, on_delete=models.CASCADE, related_name='snapshots')
    name          = models.CharField(max_length=120)
    description   = models.CharField(max_length=300, blank=True)
    snapshot_data = models.JSONField(default=dict)
    created_by    = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                      on_delete=models.SET_NULL, related_name='bom_snapshots_created')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'bom'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.tree} - {self.name}'
