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
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        user_name = request.form['name']
        user_email = request.form['email']
        user_pass = request.form['password']
        confirm_pass = request.form['repeat_password']
        if UserInfo.query().filter(UserInfo.email == user_email).get():
            flash("Registration Unsuccessful! Email Already Exists!.")
        else:
            if user_pass == confirm_pass:
                if models.UserInfo(user_name=user_name, id=str(uuid.uuid4()), email=user_email, password=user_pass).put():
                    return redirect('/login')
                else:
                    flash("Registration Failed! Server Error, Please Try Again Later!")
            else:
                flash("Registration Unsuccessful! Passwords do not match!.")
    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    session_id = request.cookies.get('access_token')
    if session_id and session_id != '':
        return redirect(url_for('dashboard'))

    if request.method == "POST":
        user_email = request.form['email']
        user_pass = request.form['password']
        user_info = UserInfo.query().filter(UserInfo.email == user_email).get()
        if user_info and user_info.password == user_pass:
            session_details = models.Session(session_id=user_info.key.id(), user_name=user_info.user_name,
                                             user_email=user_info.user_email).put()
            session['user'] = session_details
            return redirect(url_for('/dashboard'))
        else:
            flash("Invalid Credentials! Try again!")
    return render_template("login.html")


@app.route('/google_login')
def google_login():
    params = {
        'client_id': config.get("CLIENT_ID"),
        'scope': config.get("PROFILE_SCOPE"),
        'redirect_uri': config.get("PROFILE_REDIRECT_URI"),
        'access_type': 'offline',
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
        # user_id = str(uuid.uuid4())
        # user = models.UserInfo(id=user_id, email=user_email, user_name=user_name, password=user_id).put()
        # session_id = user.id()

        return redirect('unauthorized')
    else:
        session_id = user.key.id()

    models.Session(session_id=session_id, user_name=user_name, user_email=user_email).put()
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
        user_id = session_id
        user_info = models.UserInfo.query().filter(models.UserInfo.key == ndb.Key(models.UserInfo, user_id)).get()

        cursor = Cursor(urlsafe=cursor)
        content, next_cursor, more = models.HtmlContent.query(models.HtmlContent.team_id == user_info.team_id).\
            order(-models.HtmlContent.timestamp).fetch_page(5, start_cursor=cursor)

        if next_cursor is not None:
            next_cursor = next_cursor.urlsafe()
        else:
            next_cursor = 'none'

        content_list = []
        if content:
            for feeds in content:
                content_list.append({
                    'id': str(feeds.key.id()),
                    'markup_content': Markup(feeds.markup_content),
                    'markdown_content': feeds.markdown_content,
                    'created_by': feeds.created_by,
                    'desc': feeds.description,
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
        user_id = session_id
        user_info = models.UserInfo.query().filter(models.UserInfo.key == ndb.Key(models.UserInfo, user_id)).get()
        if request.method == 'POST':
            markdown_content = request.json['markdown_txt']
            description = request.json['description']
            is_preview = request.json['preview']
            markup_content = markdown2.markdown(markdown_content, extras=["tables"])

            key = 'preview'

            if is_preview == 'false':
                content_id = str(uuid.uuid4())
                key = models.HtmlContent(id=content_id, markup_content=markup_content,
                                         markdown_content=markdown_content,
                                         created_by=user_info.user_name, team_id=user_info.team_id,
                                         description=description).put()
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

        return render_template('new_markdown.html', user_id=user_id, user_name=user_info.user_name,
                               session_exists=session_exists)

    return render_template('access_denied.html')


@app.route('/view', methods=['GET', 'POST'])
def view():
    content_id = request.args.get('content_id')
    html_content = models.HtmlContent.query().filter(
        models.HtmlContent.key == ndb.Key(models.HtmlContent, content_id)).get()
    if html_content:
        return render_template('view_content.html', html_content=Markup(html_content.markup_content))
    return "Oops! No content available."


@app.route('/redefine', methods=['GET', 'POST'])
def redefine():
    session_exists = False
    session_id = request.cookies.get('access_token')
    if session_id and session_id != '':
        session_exists = True
        content_id = request.args.get('content_id')
        feed = models.HtmlContent.query(models.HtmlContent.key == ndb.Key(models.HtmlContent, content_id)).get()
        return render_template('edit_contents.html', markup=Markup(feed.markup_content), markdown=feed.markdown_content,
                               content_id=content_id, session_exists=session_exists)
    return render_template('access_denied.html')


@app.route('/redefine-feed/', methods=['GET', 'POST'])
def redefine_functions():
    if request.method == 'POST':
        markdown_content = request.json['markdown_txt']
        type = request.json['type']
        content_id = request.args.get('content_id')
        markup_content = markdown2.markdown(markdown_content)

        if type == 'post':
            old_content = models.HtmlContent.query(models.HtmlContent.key ==
                                                   ndb.Key(models.HtmlContent, content_id)).get()
            description = old_content.description
            key = models.HtmlContent(id=content_id, markup_content=markup_content, markdown_content=markdown_content,
                                     created_by=old_content.created_by, description=description).put()

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
    session_id = request.cookies.get('access_token')
    if session_id and session_id != '':
        return redirect('profile')
    return render_template("access_denied.html")


@app.route('/fetch_team_members')
def fetch_team_members():
    session_id = request.cookies.get('access_token')
    if session_id and session_id != '':
        user_info = models.UserInfo.query().filter(models.UserInfo.key == ndb.Key(models.UserInfo, session_id)).get()
        if user_info:
            team_members_list = []
            team_members = models.UserInfo.query(models.UserInfo.team_id == user_info.team_id).order(models.UserInfo.user_name)

            for team_member in team_members:
                team_members_list.append(team_member.user_name)

            team_name = models.TeamInfo.query(models.TeamInfo.team_id == user_info.team_id).get().team_name
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
            new_member_team_id = user_info.team_id

            if models.UserInfo.query(models.UserInfo.email == new_member_email).get() is None:
                if models.UserInfo(id=new_member_id, user_name=new_member_name, team_id=new_member_team_id,
                                   email=new_member_email, password=new_member_id).put():
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
        return render_template('add_new_member.html', session_exists=session_exists, user_name=user_info.user_name)
    return redirect(url_for('access_denied'))


if __name__ == "__main__":
    app.run(debug=True)

