import markdown2, uuid, time
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, redirect, url_for, Markup, session, flash, jsonify, escape
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor


class UserInfo(ndb.Model):
    username = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    profilepic = ndb.StringProperty(required=True)
    isOnline = ndb.BooleanProperty(required=True)


class HtmlContent(ndb.Model):
    markupcontent = ndb.TextProperty(required=True)
    markdowncontent = ndb.TextProperty(required=True)
    createdby = ndb.StringProperty(required=True)
    description = ndb.StringProperty(required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
