#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class PostBlog(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

class MainPage(Handler):
    def render_front(self, subject="", content="", error=""):
        posts = db.GqlQuery("SELECT * FROM PostBlog "
                           "ORDER BY last_modified DESC LIMIT 5")
        self.render("front.html", subject=subject, content=content, error=error, posts=posts)


    def get(self):
        self.render_front()


class NewPost(Handler):
    def render_new_post(self, subject="", content="", error=""):
        posts = db.GqlQuery("SELECT * FROM PostBlog "
                           "ORDER BY last_modified DESC ")
        self.render("newpost.html", subject=subject, content=content, error=error, posts=posts)

    def get(self):
        self.render_new_post()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            a = PostBlog(subject = subject, content = content)
            a.put()
            a_link = str(a.key().id())

            self.redirect("/blog/" + a_link)
        else:
            error = "we need both a subject and body!"
            self.render_new_post(subject, content, error)

class ViewPostHandler(Handler):

    def get(self, id):
        id = int(id)
        post = PostBlog.get_by_id(id)

        self.render("viewpost.html", post=post, id=id)

app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
