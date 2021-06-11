from django.http import response
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from django.apps import AppConfig
import psycopg2
from django.db import connection
import json
import time
from datetime import datetime

class AppConfig(AppConfig):
    name = 'app'

cursor=connection.cursor()