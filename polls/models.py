from django.db import models
from django.contrib.auth.models import User


questions_types = (
    ("textbox", "textbox"),
    ("multipleselect", "multipleselect"),
    ("radiobutton", "radiobutton"),
    ("numvalue", "numvalue"),
    ("boolean","boolean")
) 
    
country_types = (
    ("sl", "Slovenija"),
    ("hr", "Hrvaška"),
    ("ger", "Nemčija"),
    ("ita", "Italija"),
    ("uk", "Anglija")
) 

class Question(models.Model):
    id = models.AutoField(primary_key = True)
    question = models.CharField("Vprašanje", max_length=200, null=False)
    question_type = models.CharField(
        "Tip",
        help_text="Izberi tip vprašanja",
        max_length=20,
        choices=questions_types,
        default="textbox",
    )
    max_choices = models.IntegerField(
        "Max odgovorov", blank=True, null=True
    )

    question_values = models.CharField("Vrednosti", max_length=500, blank=True, null=True)
    question_grade = models.IntegerField(
        "Točke", default=1, blank=False, null=False
    )
    question_grade_partials = models.CharField("Multi: Delne točke,Bool: False value", max_length=200, blank=True, null=True)
    question_grade_range =  models.IntegerField(
        "Rang +-", blank=True, null=True
    )
    question_grade_description = models.CharField("Opis ocene", max_length=500, blank=True, null=True)

    class Meta:
        verbose_name = "Vprašanje"
        verbose_name_plural = "Vprašanja"

#    def __str__(self):
#        return self.question

class Answer(models.Model):
    id = models.AutoField(primary_key = True)
    userEmail = models.CharField("Email", max_length=200, default="", null=False)
    userName = models.CharField("Ime", max_length=200, default="", null=False)
    userGroup = models.CharField("Skupina", max_length=200, default="", null=False)
    value = models.CharField("Odgovor", max_length=200, null=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_dt = models.DateTimeField("Datum", auto_now_add=True, null=False)
    grade = models.IntegerField(
        "Točke", blank=True, null=True
    )

    class Meta:
        verbose_name = "Odgovor"
        verbose_name_plural = "Odgovori"

    def __str__(self):
        return self.value

class Season(models.Model):
    id = models.AutoField(primary_key = True)
    season_name = models.CharField("Ime Sezone", max_length=200, default="", null=False)  

    class Meta:
        verbose_name = "Sezona"
        verbose_name_plural = "Sezone"
    
    def __str__(self):
        return self.season_name

class Poll(models.Model):
    id = models.AutoField(primary_key = True)
    poll_name = models.CharField("Ime kviza", max_length=200, null=False)
    question_ids = models.CharField("Serija vprašanj", max_length=200, null=False)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    is_active = models.BooleanField("Aktiven", help_text="Samo en aktiven kviz na enkrat", default=False)
    is_grading = models.BooleanField("Ocenjevanje", help_text="Samo en aktiven kviz na enkrat", default=False)
    is_results = models.BooleanField("Rezultati", help_text="Ali se rezultati pokažejo na www", default=False)
    

    class Meta:
        verbose_name = "Kviz"
        verbose_name_plural = "Kvizi"


