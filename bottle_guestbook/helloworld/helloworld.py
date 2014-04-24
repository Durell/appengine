from bottle import Bottle, debug, redirect, request, response

bottle = Bottle()

from google.appengine.api import users

debug(True)

@bottle.route('/')
def home():
  user = users.get_current_user()

  if user:
    response.content_type = 'text/plain'
    return 'Hello, ' + user.nickname()
  else:
    redirect(users.create_login_url())

@bottle.route('/foo')
def foo():
  return "bar"
