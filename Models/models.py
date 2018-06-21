import markdown2, uuid, time
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, redirect, url_for, Markup, session, flash, jsonify, escape
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor


class UserInfo(ndb.Model):
    user_name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    profilepic = ndb.StringProperty(required=True)
    isOnline = ndb.BooleanProperty(required=True)


class HtmlContent(ndb.Model):
    markup_content = ndb.TextProperty(required=True)
    markdown_content = ndb.TextProperty(required=True)
    created_by = ndb.StringProperty(required=True)
    description = ndb.StringProperty(required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
