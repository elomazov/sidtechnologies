from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import logging
import webapp2
import os

import datetime
from datetime import date
from decimal import Decimal

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(template_dir))

class User(ndb.Model):
    username = ndb.StringProperty()
    email = ndb.StringProperty()
    date = ndb.DateProperty(auto_now = True)
    def history_url(self):
        return '/history?key=' + self.key.urlsafe()

class Sprint(ndb.Model):
    projectName = ndb.StringProperty()
    projectOwner = ndb.StringProperty()
    scrumMaster = ndb.StringProperty()
    team = ndb.StringProperty()
    sprintNum = ndb.StringProperty()
    sprintPlanDate = ndb.StringProperty()
    sprintRetroDate = ndb.StringProperty()
    scrumMeetDate = ndb.StringProperty()
    user_key = ndb.KeyProperty(kind = User)

class Task(ndb.Model):
    taskDescription = ndb.StringProperty()
    taskOwner = ndb.StringProperty()
    taskLength = ndb.StringProperty()
    taskNotes = ndb.StringProperty()
    taskStatus = ndb.StringProperty()
    user_key = ndb.KeyProperty(kind = User)
    sprint_key = ndb.KeyProperty(kind = Sprint)

    taskStatus = 'Task Created'

    def setInProgress(self):
        self.taskStatus = 'In Progress'

    def setDone(self):
        self.taskStatus = 'Done'

class MainHandler(webapp2.RequestHandler):
    def get(self):
        # get info
        current_user = users.get_current_user()


        if current_user:
            logout_url = users.CreateLogoutURL('/')
            email = current_user.email()
            username = email.split('@')[0]

            current_users = User.query(User.email == email).fetch()

            if not current_users:
                user = User(username=username, email=email)
                user.put()
            else:
                user = User.query(User.username == username).get()

            sprints = Sprint.query(Sprint.user_key == user.key).fetch()

            if sprints:
                template = jinja_environment.get_template('main.html')
                template_vals = {'user':user, 'sprints':sprints,
                'logout_url':logout_url}

                tasks = Task.query(Task.user_key == user.key)

                if tasks:
                    template_vals['tasks'] = tasks
                else:
                    template_vals['tasks'] = []

                self.response.write(template.render(template_vals))
            else:
                self.redirect('/getProject')

        else:
            login_url = users.CreateLoginURL('/')
            template = jinja_environment.get_template('home.html')
            template_vals = {'login_url':login_url}
            self.response.write(template.render(template_vals))

    def post(self):
        # get info
        current_user = users.get_current_user()
        email = current_user.email()

        user = User.query(User.email == email).get()

        sprint = Sprint.query(Sprint.user_key == user.key).get()
        sprint.put()

        self.redirect('/')

class ProjectHandler(webapp2.RequestHandler):

    def get(self):
        # get info
        current_user = users.get_current_user()
        email = current_user.email()


        user = User.query(User.email == email).get()

        user_key = user.key
        template = jinja_environment.get_template('main.html')
        logout_url = users.CreateLogoutURL('/')
        self.response.write(
        template.render({'user':user,'logout_url':logout_url})
        )

    def post(self):
        current_user = users.get_current_user()
        email = current_user.email()
        user = User.query(User.email == email).get()

        user_key = user.key

        projectName = self.request.get('projname')
        projectOwner = self.request.get('projowner')
        scrumMaster = self.request.get('scrummaster')
        team = self.request.get('team')
        sprintNum = self.request.get('sprintnum')
        sprintPlanDate = self.request.get('sprintplan')
        sprintRetroDate = self.request.get('sprintretro')
        scrumMeetDate = self.request.get('scrummeet')


        newSprint = Sprint(projectName = projectName,
        projectOwner = projectOwner, scrumMaster = scrumMaster, team = team,
        sprintNum = sprintNum, sprintPlanDate = sprintPlanDate,
        sprintRetroDate = sprintRetroDate, scrumMeetDate = scrumMeetDate,
        user_key = user_key)

        newSprint.put()
        self.redirect('/')

class TaskHandler(webapp2.RequestHandler):

    def get(self):
        current_user = users.get_current_user()
        email = current_user.email()
        user = User.query(User.email == email).get()
        user_key = user.key

        template = jinja_environment.get_template('main.html')
        logout_url = users.CreateLogoutURL('/')
        self.response.write(
        template.render({'user':user,'logout_url':logout_url})
        )

    def post(self):
        current_user = users.get_current_user()
        email = current_user.email()
        user = User.query(User.email == email).get()

        user_key = user.key

        taskDescription = self.request.get('taskDescription')
        taskOwner = self.request.get('taskOwner')
        taskLength = self.request.get('taskLength')
        taskNotes = self.request.get('taskNotes')

        sprint = Sprint.query(Sprint.user_key == user.key).get()

        newTask = Task(taskDescription = taskDescription, taskOwner = taskOwner,
        taskLength = taskLength, taskNotes = taskNotes, user_key = user.key,
        sprint_key = sprint.key)

        newTask.put()
        self.redirect('/')

class DeleteHandler(webapp2.RequestHandler):
    def post(self):
        task_safekey = self.request.get('key')
        ndb.Key(urlsafe=task_safekey).delete()
        self.redirect('/')

class CompletedTaskHandler(webapp2.RequestHandler):
    def post(self):
        task_safekey = self.request.get('key')
        task_key = ndb.Key(urlsafe=task_safekey)
        task = task_key.get()
        task.setDone()
        task.put()
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/getProject', ProjectHandler),
    ('/getTask', TaskHandler),
    ('/delete', DeleteHandler),
    ('/taskDone', CompletedTaskHandler),
], debug=True)
