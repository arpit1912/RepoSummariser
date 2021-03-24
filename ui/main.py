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
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("../../atlastk")

try:
  import atlastk
except:
  import pip
  pip.main(['install', 'atlastk'])
  import atlastk

fields = []

obj = RepoSummariser("9ab3c7cf2a89afde31a4a30dec51c7bbaf2de1f8")
obj.rate_check()

def ac_connect(dom):
  dom.inner("", open( "Main.html").read() )
  dom.focus( "token")

def ac_submit(dom):
  username = dom.get_value("reponame")
  reponame = dom.get_value("username")
  token = dom.get_value("token")
  print(reponame,username,token)
  obj = RepoSummariser(token)
  obj.initialise_repo(username,reponame)
  obj.start_processing()
  dom.alert("Hello, {}!".format(reponame+username+token))
  dom.focus( "token")

def ac_clear(dom):
  if ( dom.confirm("Are you sure?" ) ):
    dom.set_value("token", "" )
    dom.set_value("username", "" )
    dom.set_value("reponame", "" )
  dom.focus( "token")

callbacks = {
  "": ac_connect,
  "Submit": ac_submit,
  "Clear": ac_clear,
}
    
atlastk.launch(callbacks, None, open("Head.html").read())
