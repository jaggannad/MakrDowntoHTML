from google.appengine.ext import ndb


class UserInfo(ndb.Model):
    user_name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    profilepic = ndb.StringProperty(default='')
    isOnline = ndb.BooleanProperty(required=True)


class HtmlContent(ndb.Model):
    markup_content = ndb.TextProperty(required=True)
    markdown_content = ndb.TextProperty(required=True)
    created_by = ndb.StringProperty(required=True)
    description = ndb.StringProperty(required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)


class Session(ndb.Model):
    session_id = ndb.StringProperty(required=True)
    user_name = ndb.StringProperty(required=True)
    user_email = ndb.StringProperty(required=True)

