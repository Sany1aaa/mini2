from django.db import models
from users.models import CustomUser
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

class Student(models.Model):
    name = models.CharField(max_length=255, default="SomeName")
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    dob = models.DateField(null=True, blank=True)
    registration_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


@receiver([post_save, post_delete], sender=Student)
def clear_student_cache(sender, instance, **kwargs):
    cache.delete('student_list')
    cache_key = make_template_fragment_key('student_detail', [instance.pk])
    cache.delete(cache_key)