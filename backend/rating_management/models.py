from django.db import models
from authentication.models import User
from django.utils import timezone

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5)  
    comment = models.TextField(blank=True, null=True)  
    created_at = models.DateTimeField(default=timezone.now)

    # def calculate_average_rating():
    #     total_ratings = Rating.objects.aggregate(total=models.Sum('rating')).get('total', 0)
    #     num_ratings = Rating.objects.count()
    #     if num_ratings > 0:
    #         return total_ratings / num_ratings
    #     else:
    #         return 0