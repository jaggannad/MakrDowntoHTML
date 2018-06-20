from Models import models

app = models.Flask(__name__)
app.secret_key = "SYNCMARKDOWN1234567890"

# UserInfo(username="Jagan", id=str(uuid.uuid4()), email="j@g.com", password="pass", profilepic="puppy.jpg", isOnline=False).put()
# UserInfo(username="Parthi", id=str(uuid.uuid4()), email="p@g.com", password="pass", profilepic="mentor.png", isOnline=False).put()
# UserInfo(username="Vasanth", id=str(uuid.uuid4()), email="v@g.com", password="pass", profilepic="hisenberg.jpg", isOnline=False).put()
# UserInfo(username="Lokesh", id=str(uuid.uuid4()), email="l@g.com", password="pass", profilepic="default.jpg", isOnline=False).put()


@app.route('/')
def index():
    if models.session['user']:
        userid = models.session['user']['userid']
        return models.redirect(models.url_for('profile', userid=userid))
    return models.redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if models.request.method == "POST":
        print "in register post method"
        username = models.request.form['name']
        useremail = models.request.form['email']
        userpass = models.request.form['password']
        confirmpass = models.request.form['repeatpassword']
        if models.UserInfo.query().filter(models.UserInfo.email == useremail).get():
            models.flash("Registration Unsuccessful! Email Already Exists!.")
        else:
            if userpass == confirmpass:
                if models.UserInfo(username=username, id=id, email=useremail, password=userpass,
                                   profilepic="default.jpg", isOnline=False).put():
                    return models.redirect('/login')
                else:
                    models.flash("Registration Failed! Server Error, Please Try Again Later!")
            else:
                models.flash("Registration Unsuccessful! Passwords do not match!.")
    return models.render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if models.session['user']:
        userid = models.session['user']['userid']
        return models.redirect(models.url_for('profile', userid=userid))

    if models.request.method == "POST":
        useremail = models.request.form['email']
        userpass = models.request.form['password']
        userinfo = models.UserInfo.query().filter(models.UserInfo.email == useremail).get()
        if userinfo and userinfo.password == userpass:
            sessiondetails = {
                'userid': userinfo.key.id(),
                'useremail': useremail,
                'username': userinfo.username
            }
            models.session['user'] = sessiondetails
            return models.redirect(models.url_for('profile', userid=userinfo.key.id()))
        else:
            models.flash("Invalid Credentials! Try again!")
    return models.render_template("login.html")


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    userid = models.request.args.get('userid')
    userinfo = models.UserInfo.query().filter(models.UserInfo.key == models.ndb.Key(models.UserInfo, userid)).get()
    return models.render_template("getMarkDown.html", userinfo=userinfo, userid=userid)


@app.route('/initialcontents/', defaults={'cursor': None}, methods=['GET', 'POST'])
@app.route('/initialcontents/<cursor>', methods=['GET', 'POST'])
def getinitialcontents(cursor):
    cursor = models.Cursor(urlsafe=cursor)

    content, next_cursor, more = models.HtmlContent.query().order(-models.HtmlContent.timestamp).fetch_page(8, start_cursor=cursor)

    if next_cursor is not None:
        next_cursor = next_cursor.urlsafe()
    else:
        next_cursor = 'none'

    contentlist = []
    if content:
        for feeds in content:
            contentlist.append({
                'id': str(feeds.key.id()),
                'markupcontent': models.Markup(feeds.markupcontent),
                'markdowncontent': feeds.markdowncontent,
                'createdby': feeds.createdby,
                'desc': feeds.description,
                'timestamp': feeds.timestamp
            })
        response = {
            'success': True,
            'Description': 'Posts retrieved successfully',
            'content': contentlist,
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


@app.route('/newmarkdown', methods=['GET', 'POST'])
def newmarkdown():
    userid = models.request.args.get('userid')
    userinfo = models.UserInfo.query().filter(models.UserInfo.key == models.ndb.Key(models.UserInfo, userid)).get()
    if models.request.method == 'POST':
        markdowncontent = models.request.json['markdowntxt']
        description = models.request.json['description']
        isPreview = models.request.json['preview']
        markupcontent = models.markdown2.markdown(markdowncontent)

        key = 'preview'

        if isPreview == 'false':
            contentid = str(models.uuid.uuid4())
            key = models.HtmlContent(id=contentid, markupcontent=markupcontent, markdowncontent=markdowncontent,
                                     createdby=userinfo.username, description=description).put()
        # time.sleep(1);
        if key:
            content = models.Markup(markupcontent)
            response = {
                'success': True,
                'Description': 'Markdown-HTML conversion successful',
                'content': content,
                'createdby': userinfo.username,
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
    return models.render_template('newmarkdown.html', userid=userid, username=userinfo.username)


@app.route('/view', methods=['GET', 'POST'])
def view():
    contentid = models.request.args.get('contentid')
    htmlcontent = models.HtmlContent.query().filter(
        models.HtmlContent.key == models.ndb.Key(models.HtmlContent, contentid)).get()
    if htmlcontent:
        return models.render_template('viewcontent.html', htmlcontent=models.Markup(htmlcontent.markupcontent))
    return "Oops! No content available."


@app.route('/redefine', methods=['GET', 'POST'])
def redefine():
    contentid = models.request.args.get('contentid')
    feed = models.HtmlContent.query(models.HtmlContent.key == models.ndb.Key(models.HtmlContent, contentid)).get()
    return models.render_template('editcontents.html', markup=models.Markup(feed.markupcontent), markdown=feed.markdowncontent,
                                  contentid=contentid)


@app.route('/redefinefeed/', methods=['GET', 'POST'])
def redefinefunctions():
    if models.request.method == 'POST':
        markdowncontent = models.request.json['markdowntxt']
        type = models.request.json['type']
        contentid = models.request.args.get('contentid')
        markupcontent = models.markdown2.markdown(markdowncontent)

        if type == 'post':
            oldcontent = models.HtmlContent.query(models.HtmlContent.key == models.ndb.Key(models.HtmlContent, contentid)).get()
            description = oldcontent.description
            key = models.HtmlContent(id=contentid, markupcontent=markupcontent, markdowncontent=markdowncontent,
                                     createdby=models.session['user']['username'], description=description).put()

            if key:
                response = {
                    'success': True,
                    'desc': 'Posted succesfully',
                    'content': models.Markup(markupcontent),
                    'timestamp': models.time.time()
                }
            else:
                response = {
                    'success': False,
                    'desc': 'Converted succesfully',
                    'content': '',
                    'timestamp': models.time.time()
                }
        else:
            response = {
                'success': True,
                'desc': 'Conversion succesfully',
                'content': models.Markup(markupcontent),
                'timestamp': models.time.time()
            }
    return models.jsonify(response)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    userid = models.request.args.get('userid')
    userinfo = models.UserInfo.query().filter(models.UserInfo.key == models.ndb.Key(models.UserInfo, userid)).get()
    userinfo.isOnline = False
    userinfo.put()
    models.session.pop('user', None)
    return models.redirect(models.url_for('login', message=userid + "Loggedout"))


@app.route('/markdown/html', methods=['GET', 'POST'])
def convertedcontent():
    htmlcontent = models.HtmlContent.query()\
        .filter(models.HtmlContent.key == models.ndb.Key(models.HtmlContent, models.request.args.get('contentid'))).get()
    if htmlcontent:
        # formatted = BeautifulSoup(htmlcontent.content).prettify()
        # joined = Markup("<br>").join(formatted.split("\n"))
        return models.render_template("content.html", content=models.Markup(htmlcontent.markupcontent))
    else:
        return "Sorry No Content Available!"


if __name__ == "__main__":
    app.run(debug=True)

