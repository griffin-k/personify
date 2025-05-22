from django.db import models


class AddMissing(models.Model):
    full_name = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)
    reporter_address = models.TextField()
    missing_place_address = models.TextField()
    identity_details = models.TextField()
    image = models.ImageField(upload_to='missing_person_images/', null=True, blank=True)

    def __str__(self):
        return self.full_name
