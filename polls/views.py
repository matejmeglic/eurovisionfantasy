from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Question, Poll, Answer, Season
from django.forms.models import model_to_dict
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from operator import itemgetter
from django.contrib.auth.decorators import login_required
import math




def vote(request):
    active_polls = Poll.objects.filter(is_active=True).values() # get initial poll
    if len(active_polls) == 0:
        return HttpResponseRedirect(reverse("error"))
    active_question_list = [int(x.strip()) for x in active_polls[0]["question_ids"].split(',') if x]  # get questions
    questions = []
    for question in Question.objects.filter(id__in=active_question_list).order_by('id'): # construct context
        if question.question_values == "" or question.question_values is None :
            check_values = None 
        else:
            check_values = [x.strip() for x in question.question_values.split(',')]
        content = {"id": question.id, 
                   "question":question.question, 
                   "type": question.question_type, 
                   "max_choices":question.max_choices,
                   "values": check_values,
                   "grade": question.question_grade,
                   "grade_partials": question.question_grade_partials,
                   "grade_range": question.question_grade_range, 
                   "grade_description": question.question_grade_description
                   }
        questions.append(content)

    #sort
    questions_sorted = []
    
    for original_q in active_question_list:
        for question in questions:
            if original_q == question.get("id"):
                questions_sorted.append(question)

    context = {"questions": questions_sorted, "active_question_list":active_question_list}
    return render(request, "polls/vote.html", context)



def storeVotes(request):
    active_polls = Poll.objects.filter(is_active=True).values()
    active_question_list = [int(x.strip()) for x in active_polls[0]["question_ids"].split(',') if x]  
    answered_questions = list(request.POST.items())
    email=answered_questions[1][1]
    name=answered_questions[2][1]
    group=answered_questions[3][1]
    if name == "" or email=="":
        return HttpResponseRedirect(reverse("error"))

    answered_questions.pop(0) #remove middleware csrf key
    answered_questions.pop(0) #remove email
    answered_questions.pop(0) #remove name    
    answered_questions.pop(0) #remove group    

    answered_questions_parsed=[]

    # multiselect parsing   
    for answer in answered_questions:       
        if '-' not in answer[0]:
            if answer[1] != "": # remove blank values
                answered_questions_parsed.append(answer)
        else:
            answer_key = answer[0].split('-')[0] # get only multiselect answers
            check_existing = 0
            for existing_answer in answered_questions_parsed: # check if key already exists                
                if answer_key == existing_answer[0]:
                    new_answer_value = str(existing_answer[1])+","+str(answer[1])
                    answered_questions_parsed[check_existing-1] = (answer_key, new_answer_value)
                    check_existing+=1 # counter for existing key, prevent double append of ('10-2') values
            if check_existing == 0:
                answered_questions_parsed.append((answer_key,answer[1])) # the key doesn't exist, add the answer

    #saving script
    context_answers = []
    for answer in answered_questions_parsed:
        for question in active_question_list:
                if int(answer[0]) == question:
                    if answer[1] != "": # remove blank values, testing
                        if email != "":
                            if name != "":
                                questionFK = Question.objects.get(id=question) 
                                saveThis = Answer(userEmail=email, userName=name, userGroup=group, value=answer[1], question=questionFK, created_dt=timezone.now())
                                saveThis.save()
                                context_answers.append({"question":questionFK.question, "answer":answer[1]})

    #build context for thankyou page

    context = {"answers": context_answers}

    #return HttpResponseRedirect("") #testEnv
    #return HttpResponseRedirect(reverse("thankyou")) #production
    return render(request, "polls/thankyou.html", context)

def thankyou(request):

    return render(request, "polls/thankyou.html")

def error(request):

    return render(request, "polls/error.html")

@login_required(login_url='vote')
def email(request):
    distinct_emails = Answer.objects.all().order_by().values('userEmail').distinct()
    email_string = ""
    for email in distinct_emails:
        email_string += email.get("userEmail") + ", "

    context = {"emails": email_string}    


    return render(request, "polls/email.html", context)

def index(request):

    return render(request, "polls/index.html")

def grade(request):
    active_polls = Poll.objects.filter(is_grading=True).values() # get initial poll
    if len(active_polls) == 0:
        return HttpResponseRedirect(reverse("error"))
    active_question_list = [int(x.strip()) for x in active_polls[0]["question_ids"].split(',') if x]  # get questions
    questions = []
    for question in Question.objects.filter(id__in=active_question_list).order_by('id'): # construct context
        if question.question_values == "" or question.question_values is None :
            check_values = None 
        else:
            check_values = [x.strip() for x in question.question_values.split(',')]
        content = {"id": question.id, 
                   "question":question.question, 
                   "type": question.question_type, 
                   "max_choices":question.max_choices,
                   "values": check_values,
                   "grade": question.question_grade,
                   "grade_partials": question.question_grade_partials,
                   "grade_range": question.question_grade_range, 
                   "grade_description": question.question_grade_description
                   }
        questions.append(content)

    #sort
    questions_sorted = []
    
    for original_q in active_question_list:
        for question in questions:
            if original_q == question.get("id"):
                questions_sorted.append(question)

    context = {"questions": questions_sorted, "active_question_list":active_question_list}
    return render(request, "polls/grade.html", context)

def dryRunGrades(request):
    active_polls = Poll.objects.filter(is_grading=True).values()
    active_question_list = [int(x.strip()) for x in active_polls[0]["question_ids"].split(',') if x]  
    graded_questions = list(request.POST.items())
    graded_questions.pop(0) #remove middleware csrf key

    graded_questions_parsed=[]

    # multiselect parsing   
    for grade in graded_questions:       
        if '-' not in grade[0]:
            if grade[1] != "": # remove blank values
                graded_questions_parsed.append(grade)
        else:
            grade_key = grade[0].split('-')[0] # get only multiselect grades
            check_existing = 0
            for existing_grade in graded_questions_parsed: # check if key already exists                
                if grade_key == existing_grade[0]:
                    new_grade_value = str(existing_grade[1])+","+str(grade[1])
                    graded_questions_parsed[check_existing-1] = (grade_key, new_grade_value)
                    check_existing+=1 # counter for existing key, prevent double append of ('10-2') values
            if check_existing == 0:
                graded_questions_parsed.append((grade_key,grade[1])) # the key doesn't exist, add the grade
    graded_questions_parsed_object=[]
    for question in graded_questions_parsed: # change from tuple to object for easier use in the template
        content = {
            "question_id": int(question[0]),
            "question_answer": question[1]
        }
        graded_questions_parsed_object.append(content)

    #20240506 add result to questions object for final results rendering
    for graded_question in graded_questions_parsed_object:
        get_question = Question.objects.get(id=graded_question.get("question_id"))
        get_question.question_result = graded_question.get("question_answer")
        get_question.save() # save result to the question

    # get all eligible answers and create context
    eligible_answers = Answer.objects.filter(question__in=active_question_list).values()
    eligible_questions = Question.objects.filter(pk__in=active_question_list).values()

    #print(active_question_list)
    #print(graded_questions_parsed)  
    #print(graded_questions_parsed_object)
    #print(eligible_questions) 

    answers = []

    for answer in eligible_answers:
        for question in eligible_questions:
            if question.get("id") == answer.get("question_id"):
                # calculate grade
                
                grade_calc = 0
                for grade in graded_questions_parsed_object:
                    if grade.get("question_id") == question.get("id"):
                        if question.get("question_type") == "numvalue": #numvalue special range handling
                            if question.get("question_grade_range") == None:
                                if answer.get("value") == grade.get("question_answer"):
                                    grade_calc = question.get("question_grade")
                            elif int(answer.get("value")) <= int(grade.get("question_answer"))+question.get("question_grade_range"):
                                if int(answer.get("value")) >= int(grade.get("question_answer"))-question.get("question_grade_range"):
                                    grade_calc = question.get("question_grade")
                        elif question.get("question_type") == "boolean": #boolean handling in case of different points
                            if question.get("question_grade_partials") == None: #only correct answer gets point
                                 if answer.get("value") == grade.get("question_answer"):
                                    grade_calc = question.get("question_grade")
                            else:
                                if answer.get("value") == grade.get("question_answer"): #both answers have point and they might be different, check if the answer is correct
                                    if answer.get("value") == "True": 
                                        grade_calc = int(question.get("question_grade"))
                                    elif answer.get("value") == "False":
                                        grade_calc = int(question.get("question_grade_partials"))
                        elif question.get("question_type") == "multipleselect": #multipleselect special partial grades handling
                            
                            # get arrays
                            question_values = question.get("question_values").split(",")
                            answer_values = answer.get("value").split(",")
                            grade_values = grade.get("question_answer").split(",")
                            max_choices = question.get("max_choices")
                            correct_values = []
                            # get correct values from selection
                            for a_value in answer_values:
                                for g_value in grade_values:
                                    if a_value == g_value:
                                        correct_values.append(a_value) 
                            # calculate grade
                            if question.get("question_grade_partials") == None:
                                grade_calc = math.floor(len(correct_values)/max_choices * question.get("question_grade"))
                            else:
                                grade_calc_matrix = question.get("question_grade_partials").split(",")
                                grade_calc_matrix.append(question.get("question_grade")) # add initial top grade
                                grade_calc_matrix = [ int(x) for x in grade_calc_matrix ] # change elements to int
                                if len(correct_values) == 0:
                                    grade_calc = 0
                                else:
                                    grade_calc = grade_calc_matrix[len(correct_values)-1]
                        elif answer.get("value") == grade.get("question_answer"): #else: normal condition, assign grade
                            grade_calc = question.get("question_grade")
                #build answers context
                content = {
                        "id": answer.get("id"),
                        "userEmail": answer.get("userEmail"),
                        "userName": answer.get("userName"),
                        "question_id": answer.get("question_id"),
                        "value": answer.get("value"),
                        "grade": grade_calc,               
                        }
                #print(content)
        answers.append(content)


    context = {"answers": answers, "grades":graded_questions_parsed_object, "questions":eligible_questions}
    #print(context)
    #return HttpResponseRedirect("") #testEnv
    return render(request, "polls/checkresults.html", context)

def storeResults(request):
    answers_points = list(request.POST.items())
    answers_points.pop(0) #remove middleware csrf key

    # save grades into AnswersDB
    for specific_answer in answers_points:
        get_answer = Answer.objects.get(id=specific_answer[0]) # find correct answer
        get_answer.grade = int(specific_answer[1]) # append grade
        get_answer.save() # save grade to the answer

    #return HttpResponseRedirect("") #testEnv
    return render(request, "polls/gradingcomplete.html")

def gradingcomplete(request):

    return render(request, "polls/gradingcomplete.html")

def results(request):
    # get all Polls with is_results = True
    polls_results = Poll.objects.filter(is_results=True).values()
    if len(polls_results) > 0:
        # get all questions from multiple Polls
        polls_results_transformed = []
        for result in polls_results:
            season = Season.objects.filter(id=result.get("season_id"))
            context = {
                "id":result.get("id"),
                "poll_name":result.get("poll_name"),
                "season": getattr(season[0],"season_name"),
                "grouping":result.get("grouping"),
                "question_ids": [int(x.strip()) for x in result.get("question_ids").split(',') if x]   
            }
            polls_results_transformed.append(context)
        
        #20240506 Get all questions+answers for rendering in context
        context_questionsanswers = []
        for poll in polls_results_transformed:
            get_questionsanswers = Question.objects.filter(id__in=poll.get("question_ids"))
            build_questionsanswers = []
            for question in get_questionsanswers:
                text = str(question.question)+": "+str(question.question_result.replace(",", ", "))
                build_questionsanswers.append(text)
            questionsanswers_object = {
                "season": poll.get("season"),
                "poll_name": poll.get("poll_name"),
                "questionsanswers": build_questionsanswers
            }
            context_questionsanswers.append(questionsanswers_object)

        # get all graded Answers
        counter = 0
        grouped_results = []
        for poll in polls_results_transformed:
            #print(poll)
            answers = []
            for question in Question.objects.filter(id__in=poll.get("question_ids")): # construct context
                question_id = getattr(question, "id")
                eligible_answers = Answer.objects.filter(question=question_id).values()
                for answer in eligible_answers: # construct context
                    content = {
                        "id": answer.get("id"),
                        "userEmail": answer.get("userEmail"), # group in grade_grouping
                        "userName": answer.get("userName"), # render in app
                        "userGroup": answer.get("userGroup"),
                        "question": question_id,
                        "poll": poll.get("poll_name"),
                        "season": poll.get("season"),
                        "grade": answer.get("grade")
                    }
                    answers.append(content)
            polls_results_transformed[counter]["answers"] = answers

            # results per quiz per person
            grade_grouping_per_email = [] # first use email for grouping per person
            for answer in answers:
                if_exists = 0
                for person in grade_grouping_per_email:
                    #print(person)
                    if person[2] == answer.get("userEmail"):
                        person[5] += answer.get("grade")
                        if_exists = 1
                if if_exists == 0:
                    grade_grouping_per_email.append([answer.get("season"), answer.get("poll"), answer.get("userEmail"), answer.get("userName"), answer.get("userGroup"), answer.get("grade")])

            #print(grade_grouping_per_email)
            for any_result in grade_grouping_per_email:
                grouped_results.append(any_result)
            counter+=1


        # get total season results
        season_results = []
        for gresult in grouped_results:
            if_exists = 0
            for sresult in season_results:
                if sresult[0] == gresult[0]: # create arrays instead of strings for future results parsing/concating
                    if sresult[2] == gresult[2]: #check user
                        sresult[5] += gresult[5]
                        if_exists = 1
            if if_exists == 0:
                season_results.append([gresult[0], "Total", gresult[2], gresult[3], gresult[4], int(gresult[5]) ])

        #build content (unsorted)
        content_unsorted = []
        for sresult in season_results:
            user_content = {
                "season": sresult[0],
                "name": sresult[3],
                "group": sresult[4],
                "final_score": sresult[5],
                "partials": []
            }
            for gresult in grouped_results:
                if sresult[0] == gresult[0]: #check season
                    if sresult[3] == gresult[3]: #check user
                        user_content["partials"].append([gresult[1], gresult[5]]) # remove email from 
            content_unsorted.append(user_content)

        #sort content
        #content_grade = sorted(content_unsorted, key=lambda k: (k['final_score']) , reverse=True) # first pass, sort scoring
        content_sorted = sorted(content_unsorted, key=lambda k: ( k['season'],k['final_score']) , reverse=True) # second pass, sort seasons 
        
        counter = 1
        season_changed = ""
        previous_grade = 0
        for result in content_sorted:                
            if season_changed == "" or season_changed == result.get("season"):
                if result.get("final_score") == previous_grade:
                    result["position"] = counter - 1
                else:
                    result["position"] = counter
            else:
                counter = 1
                result["position"] = counter
            
            previous_grade = result.get("final_score")
            counter += 1
            season_changed= result.get("season")

            
        #build context
        context = {"results": content_sorted, "questionsanswers": context_questionsanswers}
    else:
        context = {}

    return render(request, "polls/results.html", context)