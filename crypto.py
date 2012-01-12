import re
import os
import datetime
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
#from google.appengine.ext import db

MAX_CHATS = 10
MAX_TIME = 60*10 # 10 minutes

class MainPage(webapp.RequestHandler):
  def get(self,room='fun',alias='Anon'):
    if len(alias) < 1:
      alias = 'Anon'
    template_values = {'room': room, 'alias': alias}
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

class ChatAJAX(webapp.RequestHandler):
  def get(self,room):
    m = re.search('(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+).(\d+)',self.request.get("date"))
    if m:
      d = datetime.datetime(int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4)),int(m.group(5)),int(m.group(6)),int(m.group(7)))
    else: 
      d = datetime.datetime(2008,1,1)

    # mark as in the room!
    ip = self.request.remote_addr
    alias = self.request.get("alias")
    members = memcache.get( "members/%s" % room ) or []    
    member = None
    for m in members:
      if m['ip'] == ip:
        member = m
      elif m['last'] < (datetime.datetime.now()+datetime.timedelta(seconds=-10)): 
        members.remove(m)
 
    if member is None:
      member = {'ip': ip }
      members.insert(0,member)
    member['alias'] = alias
    member['last'] = datetime.datetime.now()
    memcache.set( "members/%s" % room, members, MAX_TIME )  

    chats = memcache.get( "chats/%s" % room ) or []
    chats.sort( lambda a,b: cmp(b['date'],a['date']) )
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write( "{ chats: [" )
    count = 0
    for chat in chats:
      if chat['date'] > d:
        if count > 0:
          self.response.out.write(',')
        self.response.out.write( '{alias: "%s", text: "%s", date: "%s"}' % (chat['alias'], chat['text'].rstrip().replace('\n','\\n'), chat['date']) )
        count = count + 1
    self.response.out.write( "], members: [" )

    count = 0
    for member in members:
      if count > 0:
        self.response.out.write(',')
      self.response.out.write('{alias: "%s", ip: "%s"}' % (member['alias'], member['ip']) )
      count = count + 1
    self.response.out.write( "]}" )

    #Chat.gql('WHERE alias = :1', 'foo')

  def post(self,room):
    chat = {}
    chat['text'] = self.request.get('text')
    chat['alias'] = self.request.get('alias')
    chat['date'] = datetime.datetime.now()
    chats = memcache.get('chats/%s' % room) or []
    chats.insert(0,chat)
    if len(chats) > MAX_CHATS: 
      chats.pop()
    memcache.set('chats/%s' % room, chats, MAX_TIME)

#    chat = Chat()
#    chat.text = self.request.get('text')
#    chat.put()

    self.response.out.write("ok")

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/chat/(.*)', ChatAJAX),
                                      ('/([^/]+)/?(.*)', MainPage),
                                     ],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()

