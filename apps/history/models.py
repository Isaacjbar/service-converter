from django.db import models
from django.conf import settings
from utils.crypto import sha256


class DiagramHistory(models.Model):
    """
    Almacena el resultado de cada conversión de código Java a diagramas UML.

    El campo 'version' se calcula automáticamente en save(): si el mismo usuario
    ya convirtió un archivo con el mismo nombre, la versión se incrementa.
    Esto permite rastrear la evolución del código sin sobrescribir historial previo.

    Campos:
        user         -- usuario propietario de la conversión.
        filename     -- nombre del archivo Java original.
        source_code  -- código fuente Java enviado.
        class_diagram   -- PlantUML generado para diagrama de clases.
        usecase_diagram -- PlantUML generado para diagrama de casos de uso.
        flow_diagram    -- PlantUML generado para diagrama de flujo.
        version      -- número de versión autoincremental por (user, filename).
        created_at   -- fecha y hora de la conversión (solo lectura).
    """

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
    source_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Diagram histories'

    def save(self, *args, **kwargs):
        """
        Sobreescribe save() para asignar el número de versión antes de insertar.
        Solo actúa en registros nuevos (sin pk). Consulta el máximo version
        existente para el mismo (user, filename) e incrementa en 1.
        Si no existe registro previo, asigna version=1.
        """
        if not self.pk:
            last = DiagramHistory.objects.filter(
                user=self.user,
                filename=self.filename,
            ).order_by('-version').first()
            self.version = (last.version + 1) if last else 1
        self.source_hash = sha256(self.source_code)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.filename} v{self.version} ({self.created_at:%Y-%m-%d})'
