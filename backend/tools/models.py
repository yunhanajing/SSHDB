from django.db import models


class VisitorEvent(models.Model):
    """A single anonymous page-view event used for visitor statistics."""

    id = models.BigAutoField(primary_key=True)
    event_id = models.CharField(
        max_length=36,
        unique=True,
        verbose_name="Event UUID",
    )
    visitor_hash = models.CharField(
        max_length=64,
        verbose_name="Anonymous visitor hash",
    )
    country_code = models.CharField(
        max_length=2,
        null=True,
        blank=True,
        verbose_name="Country code",
    )
    country_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Country name",
    )
    page_path = models.CharField(
        max_length=512,
        default="/",
        verbose_name="Page path",
    )
    referrer_host = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Referrer host",
    )
    is_bot = models.BooleanField(
        default=False,
        verbose_name="Bot visit",
    )
    visited_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Visited at",
    )

    class Meta:
        db_table = "visitor_event"
        managed = False
        ordering = ["-visited_at"]
        verbose_name = "Visitor event"
        verbose_name_plural = "Visitor events"

    def __str__(self):
        country = self.country_code or "Unknown"
        return f"{self.event_id} - {country} - {self.page_path}"
