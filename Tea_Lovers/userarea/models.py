from django.db import models
from django.core.exceptions import ValidationError

class SiteSettings(models.Model):
    registered_users_count = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            # if you're trying to save a new instance and a SiteSettings instance already exists
            raise ValidationError('There is can be only one SiteSettings instance')
        return super(SiteSettings, self).save(*args, **kwargs)


