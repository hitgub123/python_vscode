from django.db import models

# Create your models here.
class Question(models.Model):
    class Meta:
        db_table = "polls_question"

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text