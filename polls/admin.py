from django.contrib import admin
from . import models

@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
 
    list_display = ("id", "question", "question_type", "question_values", "question_grade_description", "max_choices", "question_grade", "question_grade_partials", "question_grade_range", "question_final_result")

@admin.register(models.Poll)
class PollAdmin(admin.ModelAdmin):
    
    list_display = ("poll_name","is_active", "is_grading", "is_results", "season", "question_ids")

    @admin.display(ordering='season__season_name', description='Season')
    def get_season(self, obj):
        return obj.season.season_name

@admin.register(models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    readonly_fields = ("created_dt",)
    list_display = ("created_dt", "id", "get_question", "value", "grade", "userName", "userGroup", "userEmail")
    ordering = ("-id",)
    
    @admin.display(ordering='question__question', description='Question')
    def get_question(self, obj):
        return obj.question.question
    
@admin.register(models.Season)
class SeasonAdmin(admin.ModelAdmin):
    
    list_display = ("id","season_name",)



