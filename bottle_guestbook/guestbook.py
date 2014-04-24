import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
from bottle import Bottle, request, redirect, debug
debug(True)

bottle = Bottle()

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_GUESTBOOK_NAME = 'guestbook'

# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return ndb.Key('Guestbook', guestbook_name)


class Greeting(ndb.Model):
    """Models an individual Guestbook entry with author, content, and date."""
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


@bottle.get('/')
def MainPage():
  guestbook_name = request.forms.get('guestbook_name',
                                      DEFAULT_GUESTBOOK_NAME)
  greetings_query = Greeting.query(
      ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
  greetings = greetings_query.fetch(10)
  
  if users.get_current_user():
      url = users.create_logout_url('/')
      url_linktext = 'Logout'
  else:
      url = users.create_login_url('/')
      url_linktext = 'Login'
  
  template_values = {
      'greetings': greetings,
      'guestbook_name': urllib.quote_plus(guestbook_name),
      'url': url,
      'url_linktext': url_linktext,
  }
  
  template = JINJA_ENVIRONMENT.get_template('index.html')
  return template.render(template_values)


@bottle.post('/sign')
def Guestbook():
  # We set the same parent key on the 'Greeting' to ensure each Greeting
  # is in the same entity group. Queries across the single entity group
  # will be consistent. However, the write rate to a single entity group
  # should be limited to ~1/second.
  guestbook_name = request.forms.get('guestbook_name',
                                    DEFAULT_GUESTBOOK_NAME)
  greeting = Greeting(parent=guestbook_key(guestbook_name))
  
  if users.get_current_user():
      greeting.author = users.get_current_user()
  
  greeting.content = request.forms.get('content')
  greeting.put()
  
  query_params = {'guestbook_name': guestbook_name}
  redirect('/?' + urllib.urlencode(query_params))


