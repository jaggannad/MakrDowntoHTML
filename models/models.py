from google.appengine.ext import ndb


class UserInfo(ndb.Model):
    user_name = ndb.StringProperty(required=True)
    team_id = ndb.StringProperty(default='')
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)


class HtmlContent(ndb.Model):
    markup_content = ndb.TextProperty(required=True)
    markdown_content = ndb.TextProperty(required=True)
    created_by = ndb.StringProperty(required=True)
    team_id = ndb.StringProperty(required=True)
    description = ndb.StringProperty(required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)


class Session(ndb.Model):
    session_id = ndb.StringProperty(required=True)
    user_name = ndb.StringProperty(required=True)
    user_email = ndb.StringProperty(required=True)


class TeamInfo(ndb.Model):
    team_id = ndb.StringProperty(required=True)
    team_name = ndb.StringProperty(required=True)

