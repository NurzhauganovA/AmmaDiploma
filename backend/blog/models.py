from django.db import models
from authorization.models import User


class Blog(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/blogs/', null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    summary = models.TextField()
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    image_url = models.URLField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.image_url = f'http://localhost:8000/media/images/blogs/{self.image.name}'
        super().save(*args, **kwargs)

    def formatted_date(self):
        return self.created_date.strftime("%B %d, %Y")

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'blog'


class Discussion(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    blog = models.ForeignKey(Blog, on_delete=models.SET_NULL, null=True, related_name='blog_discussion')
    comment = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    like = models.ManyToManyField(User, related_name='like_comment', null=True, blank=True)
    dislike = models.ManyToManyField(User, related_name='dislike_comment', null=True, blank=True)
    complain = models.ManyToManyField(User, related_name='complain_comment', null=True, blank=True)

    def __str__(self):
        return f'Author: {self.author} <---> Comment: {self.comment}'

    class Meta:
        db_table = 'discussion'


class ViewedBlog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    viewed_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'User: {self.user} <---> Blog: {self.blog}'

    class Meta:
        db_table = 'viewed_blog'
