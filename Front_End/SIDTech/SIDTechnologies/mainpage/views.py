from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Question


def index(request):
    # gets list from Question
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    template = loader.get_template('mainpage/index.html')
    context = {
        'latest_question_list': latest_question_list,
    }
    return HttpResponse(template.render(context, request))


def redirect(request):
    template = loader.get_template('mainpage/page2.html')
    context = {
        'latest_question_list': latest_question_list,
    }
    return HttpResponse(template.render(contexet, request))

def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)
