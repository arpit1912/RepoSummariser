"""
MIT License

Copyright (c) 2018 Claude SIMON (https://q37.info/s/rmnmqd49)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
"""

"""
Edited by Shreyansh Mehra and Arpit Bandejiya in accordance with above licenses
"""
import os, sys
from github import Github       # The Github Api Library
import requests                 # for Request Handling
import json                     # for Data handling
import mimetypes                # for filtering the files
import re                       # for writing Regular Expressions
from pprint import pprint

from tool import RepoSummariser
from pdfCreator import PDF
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("../../atlastk")


import atlastk


fields = []

    

def ac_connect(dom):
  dom.inner("", open( "Main.html").read() )
  dom.focus( "token")

def ac_clear(dom):
  if ( dom.confirm("Are you sure?" ) ):
    dom.set_value("token", "" )
    dom.set_value("username", "" )
    dom.set_value("reponame", "" )
  dom.focus( "token")

def checktokenvalidity (token):
  obj = RepoSummariser(token)
  try:
    obj.g.get_repo("oppia/oppia")
  except:
      print ('Invalid github access token')
      return False
  else:
    return True

def checkrepovalidity (token, reponame):
  obj = RepoSummariser(token)
  try:
    obj.g.get_repo(reponame)
  except:
      print ('Invalid github access token')
      return False
  else:
    return True

def checkuservalidity (token, username):
  obj = RepoSummariser(token)
  try:
    obj.g.get_user(username)
  except:
      print ('Invalid github access token')
      return False
  else:
    return True

def driver(token,username,reponame):
  
  obj = RepoSummariser(token)
  obj.initialise_repo(username,reponame)
  obj.start_processing()

  pdfCreator = PDF()
  pdfCreator.driver(reponame,username,token)


def ac_submit(dom):
  username = dom.get_value("username")
  reponame = dom.get_value("reponame")
  token = dom.get_value("token")

  #check if submitted token, username, repository are valid or not
  error_params = []
  valid_params = True

  if checktokenvalidity (token) == False:
    error_params.append("Github access token")
    valid_params = False
  if checkrepovalidity (token, reponame) == False:
    error_params.append("Repository name")
    valid_params = False
  if checkuservalidity (token, username) == False:
    error_params.append("Username")
    valid_params = False
  
  if valid_params:
    dom.alert("Submitted! The report once ready will be saved in Reports directory")
    RepoOwner,RepoLocalName = reponame.split('/')
    driver(token,RepoOwner,RepoLocalName)
    dom.set_value("token", "" )
    dom.set_value("username", "" )
    dom.set_value("reponame", "" )
  else:
    error_message = 'Invalid credentials, Check ' + error_params[0]
    for x in range(len(error_params) - 1):
      error_message = error_message + ", " + error_params[x+1]
    
    dom.alert(error_message)
  
  dom.focus( "token")

callbacks = {
  "": ac_connect,
  "Submit": ac_submit,
  "Clear": ac_clear,
}
    
atlastk.launch(callbacks, None, open("Head.html").read())

#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