from google.appengine.ext import ndb


class UserInfo(ndb.Model):
    user_name = ndb.StringProperty(required=True)
    team_id = ndb.StringProperty(repeated=True)
    current_team = ndb.StringProperty(default=None)
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)


class HtmlContentSettings(ndb.Model):
    visibility_all = ndb.BooleanProperty(default=False)
    visibility_some = ndb.BooleanProperty(default=False)
    visibility_none = ndb.BooleanProperty(default=True)

    visibility_list = ndb.JsonProperty()


class HtmlContent(ndb.Model):
    markup_content = ndb.TextProperty(required=True)
    markdown_content = ndb.TextProperty(required=True)
    created_by = ndb.StringProperty(required=True)
    last_modified = ndb.StringProperty(default="None")
    team_id = ndb.StringProperty(required=True)
    description = ndb.TextProperty(required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    settings = ndb.KeyProperty(required=True, kind='HtmlContentSettings')


class Session(ndb.Model):
    session_id = ndb.StringProperty(required=True)
    user_name = ndb.StringProperty(required=True)
    user_email = ndb.StringProperty(required=True)


class TeamInfo(ndb.Model):
    team_id = ndb.StringProperty(required=True)
    team_name = ndb.StringProperty(required=True)


class Domains(ndb.Model):
    domain_names = ndb.StringProperty(repeated=True)

