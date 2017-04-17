import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Content(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class ViewPostHandler(Handler):
    def get(self, id):
        post = Content.get_by_id(int(id))
        self.render("single.html", post=post)

class MainPageHandler(Handler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Content ORDER BY created DESC limit 5")
        self.render("top5.html", posts=blogs)

class NewPostHandler(Handler):
    def render_newpost(self, title="", content="", error=""):
        self.render("newpost.html", title=title, content=content, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")

        if title and content:
            a = Content(title=title, content=content)
            a.put()

            self.redirect("/blog")
        else:
            error = "We need a subject and some content!"
            self.render_newpost(title, content, error)

app = webapp2.WSGIApplication([
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
    webapp2.Route('/blog', MainPageHandler),
    webapp2.Route('/newpost', NewPostHandler),
    ('/', MainPageHandler),
], debug=True)
