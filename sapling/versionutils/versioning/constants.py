TYPE_ADDED = 0
TYPE_UPDATED = 1
TYPE_DELETED = 2
TYPE_REVERTED = 3
TYPE_REVERTED_ADDED = 4
TYPE_REVERTED_DELETED = 5
TYPE_CHOICES = (
    (TYPE_ADDED, 'Added'),
    (TYPE_UPDATED, 'Updated'),
    (TYPE_DELETED, 'Deleted'),
    (TYPE_REVERTED, 'Reverted'),
    (TYPE_REVERTED_ADDED, 'Reverted/Added'),
    (TYPE_REVERTED_DELETED, 'Reverted/Deleted'),
)
