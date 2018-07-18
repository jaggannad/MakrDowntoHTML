import markdown2, uuid, time
from flask import Flask, render_template, request, redirect, url_for, Markup, session, flash, jsonify, escape, json
from urllib import urlencode

from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.api import taskqueue

from models import models


# models.TeamInfo(team_id='synclio-bab52b3fe8d2', team_name='Synclio').put()
# models.TeamInfo(team_id='distributed-source-bab52b3fe8d2', team_name='Distributed Source').put()

app = Flask(__name__)
app.secret_key = "SYNC_MARKDOWN_1234567890"

config = {
    "CLIENT_ID": '359046576123-hk5bltu4dg9rpiickh0r4uju7rggmpir.apps.googleusercontent.com',
    "CLIENT_SECRET": "t7fYQYBqKKaIEwljdR60ZJwS",
    "PROFILE_SCOPE": "https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email",
    "OAUTH_ENDPOINT": "https://accounts.google.com/o/oauth2/v2/auth",
    "TOKEN_ENDPOINT": "https://www.googleapis.com/oauth2/v4/token",
    # "PROFILE_REDIRECT_URI": "http://localhost:8080/authentication",
    "PROFILE_REDIRECT_URI": "https://syncmarkdown.appspot.com/authentication"
}


def fetch_access_token(code, redirect_uri):
    params = {
        'client_id': config.get("CLIENT_ID"),
        'client_secret': config.get("CLIENT_SECRET"),
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
        'code': code,
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    res = urlfetch.fetch(config.get("TOKEN_ENDPOINT"), method='POST',
                         payload=urlencode(params), headers=headers)  # Getting Token
    return json.loads(res.content)


@app.route('/')
def index():
    session_id = request.cookies.get('access_token')
    if session_id and session_id != '':
        return redirect(url_for('dashboard'))
    return redirect('/google_login')


@app.route('/google_login')
def google_login():
    callback_url = 'None'
    if request.args.get('callback_url'):
        callback_url = request.args.get('callback_url')
    params = {
        'client_id': config.get("CLIENT_ID"),
        'scope': config.get("PROFILE_SCOPE"),
        'redirect_uri': config.get('PROFILE_REDIRECT_URI'),
        'access_type': 'offline',
        'state': callback_url,
        'response_type': 'code',
        'prompt': 'consent',
        'hd': 'anywhere.co'
    }
    return redirect('{}?{}'.format(config.get("OAUTH_ENDPOINT"), urlencode(params)))


@app.route('/authentication')
def authentication():
    if request.args.get('error') == 'access_denied':
        return render_template('access_denied')
    token_data = fetch_access_token(request.args.get('code'), config.get("PROFILE_REDIRECT_URI"))

    headers = {'Authorization': 'Bearer {}'.format(token_data['access_token'])}
    url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    response = urlfetch.fetch(url, headers=headers, method='GET')

    user_data = json.loads(response.content)
    user_email = user_data.get('email')
    user_name = user_data.get('name')
    user = models.UserInfo.query(models.UserInfo.email == user_email).get()
    session_id = ''

    if user is None:
        user_id = str(uuid.uuid4())
        user = models.UserInfo(id=user_id, email=user_email, user_name=user_name, password=user_id).put()
        session_id = user.id()

    else:
        session_id = user.key.id()

    models.Session(session_id=session_id, user_name=user_name, user_email=user_email).put()

    if request.args.get('state') != 'None':
        callback_url = request.args.get('state')
        response = redirect(callback_url)
    else:
        response = redirect('/')
    response.set_cookie('access_token', session_id)

    return response


@app.route('/unauthorized')
def unauthorized():
    return render_template('unauthorized.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    session_exists = False
    session_id = request.cookies.get('access_token')
    if session_id and session_id != '':
        session_exists = True
        user_id = session_id
        user_info = models.UserInfo.query().filter(models.UserInfo.key == ndb.Key(models.UserInfo, user_id)).get()
        return render_template("dashboard.html", user_info=user_info, user_id=user_id, session_exists=session_exists)

    return render_template('access_denied.html')


@app.route('/initial-contents/', defaults={'cursor': None}, methods=['GET', 'POST'])
@app.route('/initial-contents/<cursor>', methods=['GET', 'POST'])
def get_initial_contents(cursor):
    session_id = request.cookies.get('access_token')
    if session_id and session_id != '':
        user_info = models.UserInfo.query().filter(models.UserInfo.key == ndb.Key(models.UserInfo, session_id)).get()

        cursor = Cursor(urlsafe=cursor)
        content, next_cursor, more = models.HtmlContent.query(models.HtmlContent.team_id == user_info.current_team).\
            order(-models.HtmlContent.timestamp).fetch_page(5, start_cursor=cursor)

        if next_cursor is not None:
            next_cursor = next_cursor.urlsafe()
        else:
            next_cursor = 'none'

        content_list = []
        if content:
            for feeds in content:
                settings = feeds.settings.get()
                content_list.append({
                    'id': str(feeds.key.id()),
                    'markup_content': Markup(feeds.markup_content),
                    'markdown_content': feeds.markdown_content,
                    'team_id': feeds.team_id,
                    'created_by': feeds.created_by,
                    'last_modified': feeds.last_modified,
                    'desc': feeds.description,
                    'visibility_all': settings.visibility_all,
                    'visibility_some': settings.visibility_some,
                    'visibility_none': settings.visibility_none,
                    'timestamp': feeds.timestamp
                })
            response = {
                'success': True,
                'Description': 'Posts retrieved successfully',
                'content': content_list,
                'timestamp': time.time(),
                'next_cursor': next_cursor,
                'more': more
            }
        else:
            response = {
                'success': False,
                'Description': 'No posts available',
                'content': None,
                'timestamp': time.time()
            }
        return jsonify(response)


@app.route('/new_markdown', methods=['GET', 'POST'])
def new_markdown():
    session_exists = False
    session_id = request.cookies.get('access_token')
    if session_id and session_id != '':
        session_exists = True

        user_info = models.UserInfo.query().filter(models.UserInfo.key == ndb.Key(models.UserInfo, session_id)).get()
        if request.method == 'POST':
            markdown_content = request.json['markdown_txt']
            description = request.json['description']
            is_preview = request.json['preview']
            markup_content = markdown2.markdown(markdown_content, extras=["tables"])

            key = 'preview'

            if is_preview == 'false':
                content_id = str(uuid.uuid4())
                settings_key = models.HtmlContentSettings(id=content_id).put()
                key = models.HtmlContent(id=content_id, markup_content=markup_content,
                                         markdown_content=markdown_content,
                                         created_by=user_info.user_name, team_id=user_info.current_team,
                                         description=description, settings=settings_key).put()
            # time.sleep(1);
            if key:
                content = Markup(markup_content)
                response = {
                    'success': True,
                    'Description': 'Markdown-HTML conversion successful',
                    'content': content,
                    'created_by': user_info.user_name,
                    'desc': description,
                    'timestamp': time.time()
                }
            else:
                response = {
                    'success': False,
                    'Description': 'Unable to upload to datastore',
                    'content': None,
                    'timestamp': time.time()
                }
            return jsonify(response)

        return render_template('new_markdown.html', user_id=session_id, user_name=user_info.user_name,
                               user_info=user_info, session_exists=session_exists)

    return render_template('access_denied.html')


@app.route('/view', methods=['GET', 'POST'])
def view():
    session_id = request.cookies.get('access_token')
    content_id = request.args.get('content_id')
    if session_id and session_id != '':
        user_info = models.UserInfo.query().filter(models.UserInfo.key == ndb.Key(models.UserInfo, session_id)).get()
        if user_info:
            html_content = models.HtmlContent.query().filter(
                models.HtmlContent.key == ndb.Key(models.HtmlContent, content_id)).get()
            if html_content:
                html_content_settings = html_content.settings.get()
                if html_content_settings.visibility_all or html_content.team_id in user_info.team_id or \
                        user_info.email.split('@')[1] in dict.fromKeys(json.loads(html_content_settings.visibility_list)):
                    return render_template('view_content.html', html_content=Markup(html_content.markup_content))
                return render_template('unauthorized.html')
            return "Oops! No content available."
        return "unable to get user info"
    callback_url = url_for('view', content_id=content_id)
    return redirect(url_for('access_denied', callback_url=callback_url))


@app.route('/create_team', methods=['POST'])
def create_team():
    session_id = request.cookies.get('access_token')
    if session_id and session_id != '' and request.method == "POST":
        user_info = models.UserInfo.query().filter(models.UserInfo.key == ndb.Key(models.UserInfo, session_id)).get()
        response = {
            'success': True,
            'desc': 'Created project successfully',
            'user_name': user_info.user_name,
            'timestamp': time.time()
        }
        project_name = request.json.get('project_name')
        project_id = str(uuid.uuid4())

        if models.TeamInfo(team_id=project_id, team_name=project_name).put():
            user_info.team_id.append(project_id)
            user_info.current_team = project_id
            user_info.put()
            response.update({'current_team': project_id})
            return jsonify(response)

        response = {
            'success': False,
            'desc': 'Unable to create project',
            'timestamp': time.time()
        }
        return jsonify(response)
    return redirect('/access_denied')


@app.route('/fetch_user_projects', methods=['GET'])
def fetch_user_projects():
    session_id = request.cookies.get('access_token')
    if session_id and session_id != '':
        response = {
            'success': True,
            'desc': 'Fetched user projects successfully',
            'timestamp': time.time()
        }
        projects_list = []
        user_info = models.UserInfo.query().filter(models.UserInfo.key == ndb.Key(models.UserInfo, session_id)).get()
        if user_info:
            for team in user_info.team_id:
                team_info = models.TeamInfo.query(models.TeamInfo.team_id == team).get()
                projects_list.append({'team_id': team_info.team_id, 'team_name': team_info.team_name})

            response.update({'projects_list': projects_list})

        else:
            response = {
                'success': False,
                'desc': 'Unable to fetch user projects',
                'timestamp': time.time()
            }
        return jsonify(response)
    return render_template('access_denied.html')


@app.route('/select_project', methods=['POST'])
def select_project():
    session_id = request.cookies.get('access_token')
    if session_id and session_id != '':
        user_info = models.UserInfo.query().filter(models.UserInfo.key == ndb.Key(models.UserInfo, session_id)).get()
        user_info.current_team = request.json.get('project_id')

        user_info_updated = user_info.put().get()
        if user_info_updated:
            response = {
                'success': True,
                'desc': 'Current project updated',
                'user_name': user_info_updated.user_name,
                'current_team': user_info_updated.current_team,
                'timestamp': time.time()
            }
        else:
            response = {
                'success': False,
                'desc': 'Unable to update current project',
                'timestamp': time.time()
            }
        return jsonify(response)
    return render_template('access_denied.html')


@app.route('/fetch_teams')
def fetch_teams():
    team_list = []
    markdown_id = request.args.get('markdown_id')
    markdown_settings = ndb.Key(models.HtmlContentSettings, markdown_id).get()
    print "This is the fetch teams result: ", markdown_settings.visibility_list
    if markdown_settings.visibility_list:
        allowed_teams = json.loads(markdown_settings.visibility_list)

        for team_name, is_checked in allowed_teams.items():
            team_list.append({
                'team_name': team_name,
                'is_checked': is_checked
            })

    response = {
        'success': 'True',
        'desc': 'Teams Fetched Successfully',
        'team_list': team_list,
        'timestamp': time.time()
    }
    return jsonify(response)


@app.route('/add_new_domain', methods=['GET', 'POST'])
def add_new_domain():
    session_id = request.cookies.get('access_token')
    if session_id and session_id != '':
        domain_name = request.json.get('domain_name')
        markdown_id = request.json.get('markdown_id')
        markdown_settings = ndb.Key(models.HtmlContentSettings, markdown_id).get()
        visibility_list = markdown_settings.visibility_list

        domain = {domain_name: True}
        if visibility_list is None:
            visibility_list = json.dumps(domain)
        else:
            domain_list = json.loads(visibility_list)
            domain_list.update(domain)
            visibility_list = json.dumps(domain_list)

        markdown_settings.visibility_list = visibility_list
        markdown_settings.put()
        response = {
            'success': True,
            'desc': 'New Domain Added',
            'timestamp': time.time()
        }
        return jsonify(response)
    return render_template('access_denied.html')


@app.route('/change_visibility', methods=['POST'])
def change_visibility():
    if request.method == 'POST':
        response = {
            'success': True,
            'desc': 'Changed visibility',
            'visibility': True,
            'timestamp': time.time()
        }
        markdown_id = request.json.get('markdown_id')
        team_list = request.json.get('team_list')
        type = request.json.get('type')

        markdown_settings = models.HtmlContentSettings.get_by_id(markdown_id)

        markdown_settings.visibility_all = False
        markdown_settings.visibility_some = False
        markdown_settings.visibility_none = False

        if type == 'visibletosome':
            if team_list:
                markdown_settings.visibility_some = True
                markdown_settings.visibility_list = team_list
            else:
                markdown_settings.visibility_list = []
                markdown_settings.visibility_none = True
                response.update({'visibility': False})

        elif type == 'visibletoall':
            markdown_settings.visibility_all = True
        else:
            markdown_settings.visibility_none = True

        markdown_settings.put()
        return jsonify(response)


@app.route('/redefine', methods=['GET', 'POST'])
def redefine():
    session_exists = False
    session_id = request.cookies.get('access_token')
    if session_id and session_id != '':
        session_exists = True
        content_id = request.args.get('content_id')
        feed = models.HtmlContent.query(models.HtmlContent.key == ndb.Key(models.HtmlContent, content_id)).get()

        user_info = models.UserInfo.query().filter(models.UserInfo.key == ndb.Key(models.UserInfo, session_id)).get()
        feed_settings = feed.settings.get()
        if feed.team_id in user_info.team_id:
            return render_template('edit_contents.html', markup=Markup(feed.markup_content), user_info=user_info,
                                   markdown=feed.markdown_content, content_id=content_id, session_exists=session_exists)
        else:
            return redirect(url_for('unauthorized'))
    return render_template('access_denied.html')


@app.route('/redefine-feed/', methods=['GET', 'POST'])
def redefine_functions():
    session_id = request.cookies.get('access_token')
    if session_id and session_id != '':
        user_info = models.UserInfo.query().filter(models.UserInfo.key == ndb.Key(models.UserInfo, session_id)).get()
        if request.method == 'POST':
            markdown_content = request.json['markdown_txt']
            type = request.json['type']
            content_id = request.args.get('content_id')
            markup_content = markdown2.markdown(markdown_content, extras=["tables"])

            if type == 'post':
                old_content = models.HtmlContent.query(models.HtmlContent.key ==
                                                       ndb.Key(models.HtmlContent, content_id)).get()
                old_content.markdown_content = markdown_content
                old_content.markup_content = markup_content
                old_content.last_modified = user_info.user_name
                key = old_content.put()

                if key:
                    response = {
                        'success': True,
                        'desc': 'Posted successfully',
                        'content': Markup(markup_content),
                        'timestamp': time.time()
                    }
                else:
                    response = {
                        'success': False,
                        'desc': 'Converted successfully',
                        'content': '',
                        'timestamp': time.time()
                    }
            else:
                response = {
                    'success': True,
                    'desc': 'Conversion successfully',
                    'content': Markup(markup_content),
                    'timestamp': time.time()
                }
        return jsonify(response)
    return render_template('access_denied.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session_id = request.cookies.get('access_token')
    if session_id and session_id != '':
        session_info = models.Session.query(models.Session.session_id == session_id).get()
        if session_info:
            session_info.key.delete()

        response = redirect('/')
        response.set_cookie('access_token', '')
        return response
    return render_template("access_denied.html")


@app.route('/markdown/html', methods=['GET', 'POST'])
def converted_content():
    html_content = models.HtmlContent.query().\
        filter(models.HtmlContent.key == ndb.Key(models.HtmlContent, models.request.args.get('content_id'))).get()
    if html_content:
        # formatted = BeautifulSoup(html_content.content).prettify()
        # joined = Markup("<br>").join(formatted.split("\n"))
        return render_template("content.html", content=Markup(html_content.markup_content))
    else:
        return "Sorry No Content Available!"


@app.route('/access_denied')
def access_denied():
    callback_url = None
    if request.args.get('callback_url'):
        callback_url = request.args.get('callback_url')

    session_id = request.cookies.get('access_token')
    if session_id and session_id != '':
        return redirect('profile')

    return render_template("access_denied.html", callback_url=callback_url)


@app.route('/fetch_team_members', methods=['GET', 'POST'])
def fetch_team_members():
    session_id = request.cookies.get('access_token')
    if session_id and session_id != '':
        user_info = models.UserInfo.query().filter(models.UserInfo.key == ndb.Key(models.UserInfo, session_id)).get()
        if user_info:
            team_members_list = []
            team_members = models.UserInfo.query(models.UserInfo.team_id.IN([user_info.current_team])).order(models.UserInfo.user_name)

            if team_members:
                for team_member in team_members:
                    team_members_list.append(team_member.user_name)

                team_name = models.TeamInfo.query(models.TeamInfo.team_id == user_info.current_team).get().team_name
                response = {
                    'success': True,
                    'content': team_members_list,
                    'team_name': team_name,
                    'desc': 'Fetched Team members successfully',
                    'timestamp': time.time()
                }
            else:
                response = {
                    'success': False,
                    'desc': 'Invalid User',
                    'timestamp': time.time()
                }

        return jsonify(response)
    return render_template("access_denied.html")


@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    session_exists = False
    session_id = request.cookies.get('access_token')
    if session_id and session_id != '':
        user_id = session_id
        user_info = models.UserInfo.query().filter(models.UserInfo.key == ndb.Key(models.UserInfo, user_id)).get()
        session_exists = True

        if request.method == "POST":
            new_member_id = str(uuid.uuid4())
            new_member_email = request.json['new_member_email']
            new_member_name = request.json['new_member_name']
            new_member_team_id = user_info.current_team

            if models.UserInfo.query(models.UserInfo.email == new_member_email).get() is None:
                if models.UserInfo(id=new_member_id, user_name=new_member_name, team_id=[new_member_team_id],
                                   current_team=new_member_team_id, email=new_member_email, password=new_member_id).put():
                    response = {
                        'success': True,
                        'desc': 'Member added successfully',
                        'timestamp': time.time()
                    }
                else:
                    response = {
                        'success': False,
                        'desc': 'Unable to add new member. Please try after sometime!',
                        'timestamp': time.time()
                    }
            else:
                response = {
                    'success': False,
                    'desc': 'Member already exists!',
                    'timestamp': time.time()
                }
            return jsonify(response)
        return render_template('add_new_member.html', session_exists=session_exists, user_name=user_info.user_name,
                               user_info=user_info)
    return redirect(url_for('access_denied'))


if __name__ == "__main__":
    app.run(debug=True)

