from django.db import models
from django.conf import settings


class DiagramHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='diagram_history',
    )
    filename = models.CharField(max_length=255)
    source_code = models.TextField()
    class_diagram = models.TextField(blank=True)
    usecase_diagram = models.TextField(blank=True)
    flow_diagram = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Diagram histories'

    def save(self, *args, **kwargs):
        if not self.pk:
            last = DiagramHistory.objects.filter(
                user=self.user,
                filename=self.filename,
            ).order_by('-version').first()
            self.version = (last.version + 1) if last else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.filename} v{self.version} ({self.created_at:%Y-%m-%d})'
