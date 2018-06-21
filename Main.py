from Models import models

app = models.Flask(__name__)
app.secret_key = "SYNC_MARKDOWN_1234567890"

# models.UserInfo(user_name="Jagan", id=str(models.uuid.uuid4()), email="j@g.com", password="pass", profilepic="puppy.jpg", isOnline=False).put()
# models.UserInfo(user_name="Parthi", id=str(models.uuid.uuid4()), email="p@g.com", password="pass", profilepic="mentor.png", isOnline=False).put()
# models.UserInfo(user_name="Vasanth", id=str(models.uuid.uuid4()), email="v@g.com", password="pass", profilepic="hisenberg.jpg", isOnline=False).put()
# models.UserInfo(user_name="Lokesh", id=str(models.uuid.uuid4()), email="l@g.com", password="pass", profilepic="default.jpg", isOnline=False).put()


@app.route('/')
def index():
    if 'user' in models.session:
        user_id = models.session['user']['user_id']
        return models.redirect(models.url_for('profile', user_id=user_id))
    return models.redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if models.request.method == "POST":
        user_name = models.request.form['name']
        user_email = models.request.form['email']
        user_pass = models.request.form['password']
        confirm_pass = models.request.form['repeat_password']
        if models.UserInfo.query().filter(models.UserInfo.email == user_email).get():
            models.flash("Registration Unsuccessful! Email Already Exists!.")
        else:
            if user_pass == confirm_pass:
                if models.UserInfo(user_name=user_name, id=str(models.uuid.uuid4()), email=user_email, password=user_pass,
                                   profilepic="default.jpg", isOnline=False).put():
                    return models.redirect('/login')
                else:
                    models.flash("Registration Failed! Server Error, Please Try Again Later!")
            else:
                models.flash("Registration Unsuccessful! Passwords do not match!.")
    return models.render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in models.session:
        user_id = models.session['user']['user_id']
        return models.redirect(models.url_for('profile', user_id=user_id))

    if models.request.method == "POST":
        user_email = models.request.form['email']
        user_pass = models.request.form['password']
        user_info = models.UserInfo.query().filter(models.UserInfo.email == user_email).get()
        if user_info and user_info.password == user_pass:
            session_details = {
                'user_id': user_info.key.id(),
                'user_email': user_email,
                'user_name': user_info.user_name
            }
            models.session['user'] = session_details
            return models.redirect(models.url_for('profile', user_id=user_info.key.id()))
        else:
            models.flash("Invalid Credentials! Try again!")
    return models.render_template("login.html")


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = models.request.args.get('user_id')
    user_info = models.UserInfo.query().filter(models.UserInfo.key == models.ndb.Key(models.UserInfo, user_id)).get()
    return models.render_template("get_MarkDown.html", user_info=user_info, user_id=user_id)


@app.route('/initial-contents/', defaults={'cursor': None}, methods=['GET', 'POST'])
@app.route('/initial-contents/<cursor>', methods=['GET', 'POST'])
def get_initial_contents(cursor):
    cursor = models.Cursor(urlsafe=cursor)

    content, next_cursor, more = models.HtmlContent.query().order(-models.HtmlContent.timestamp).\
        fetch_page(8, start_cursor=cursor)

    if next_cursor is not None:
        next_cursor = next_cursor.urlsafe()
    else:
        next_cursor = 'none'

    content_list = []
    if content:
        for feeds in content:
            content_list.append({
                'id': str(feeds.key.id()),
                'markup_content': models.Markup(feeds.markup_content),
                'markdown_content': feeds.markdown_content,
                'created_by': feeds.created_by,
                'desc': feeds.description,
                'timestamp': feeds.timestamp
            })
        response = {
            'success': True,
            'Description': 'Posts retrieved successfully',
            'content': content_list,
            'timestamp': models.time.time(),
            'next_cursor': next_cursor,
            'more': more
        }
    else:
        response = {
            'success': False,
            'Description': 'No posts available',
            'content': None,
            'timestamp': models.time.time()
        }
    return models.jsonify(response)


@app.route('/new_markdown', methods=['GET', 'POST'])
def new_markdown():
    user_id = models.request.args.get('user_id')
    user_info = models.UserInfo.query().filter(models.UserInfo.key == models.ndb.Key(models.UserInfo, user_id)).get()
    if models.request.method == 'POST':
        markdown_content = models.request.json['markdown_txt']
        description = models.request.json['description']
        is_preview = models.request.json['preview']
        markup_content = models.markdown2.markdown(markdown_content)

        key = 'preview'

        if is_preview == 'false':
            content_id = str(models.uuid.uuid4())
            key = models.HtmlContent(id=content_id, markup_content=markup_content, markdown_content=markdown_content,
                                     created_by=user_info.user_name, description=description).put()
        # time.sleep(1);
        if key:
            content = models.Markup(markup_content)
            response = {
                'success': True,
                'Description': 'Markdown-HTML conversion successful',
                'content': content,
                'created_by': user_info.user_name,
                'desc': description,
                'timestamp': models.time.time()
            }
        else:
            response = {
                'success': False,
                'Description': 'Unable to upload to datastore',
                'content': None,
                'timestamp': models.time.time()
            }
        return models.jsonify(response)
    return models.render_template('new_markdown.html', user_id=user_id, user_name=user_info.user_name)


@app.route('/view', methods=['GET', 'POST'])
def view():
    content_id = models.request.args.get('content_id')
    html_content = models.HtmlContent.query().filter(
        models.HtmlContent.key == models.ndb.Key(models.HtmlContent, content_id)).get()
    if html_content:
        return models.render_template('view_content.html', html_content=models.Markup(html_content.markup_content))
    return "Oops! No content available."


@app.route('/redefine', methods=['GET', 'POST'])
def redefine():
    content_id = models.request.args.get('content_id')
    feed = models.HtmlContent.query(models.HtmlContent.key == models.ndb.Key(models.HtmlContent, content_id)).get()
    return models.render_template('edit_contents.html', markup=models.Markup(feed.markup_content),
                                  markdown=feed.markdown_content, content_id=content_id)


@app.route('/redefine-feed/', methods=['GET', 'POST'])
def redefine_functions():
    if models.request.method == 'POST':
        markdown_content = models.request.json['markdown_txt']
        type = models.request.json['type']
        content_id = models.request.args.get('content_id')
        markup_content = models.markdown2.markdown(markdown_content)

        if type == 'post':
            old_content = models.HtmlContent.query(models.HtmlContent.key ==
                                                   models.ndb.Key(models.HtmlContent, content_id)).get()
            description = old_content.description
            key = models.HtmlContent(id=content_id, markup_content=markup_content, markdown_content=markdown_content,
                                     created_by=models.session['user']['username'], description=description).put()

            if key:
                response = {
                    'success': True,
                    'desc': 'Posted successfully',
                    'content': models.Markup(markup_content),
                    'timestamp': models.time.time()
                }
            else:
                response = {
                    'success': False,
                    'desc': 'Converted successfully',
                    'content': '',
                    'timestamp': models.time.time()
                }
        else:
            response = {
                'success': True,
                'desc': 'Conversion successfully',
                'content': models.Markup(markup_content),
                'timestamp': models.time.time()
            }
    return models.jsonify(response)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    user_id = models.request.args.get('user_id')
    user_info = models.UserInfo.query().filter(models.UserInfo.key == models.ndb.Key(models.UserInfo, user_id)).get()
    user_info.isOnline = False
    user_info.put()
    models.session.pop('user', None)
    return models.redirect(models.url_for('login', message=user_id + "Logged-out"))


@app.route('/markdown/html', methods=['GET', 'POST'])
def converted_content():
    html_content = models.HtmlContent.query().\
        filter(models.HtmlContent.key == models.ndb.Key(models.HtmlContent, models.request.args.get('content_id'))).get()
    if html_content:
        # formatted = BeautifulSoup(html_content.content).prettify()
        # joined = Markup("<br>").join(formatted.split("\n"))
        return models.render_template("content.html", content=models.Markup(html_content.markup_content))
    else:
        return "Sorry No Content Available!"


if __name__ == "__main__":
    app.run(debug=True)

