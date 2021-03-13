# Importing the Libraries
from github import Github
import requests
import os
import json
from pprint import pprint

class RepoSummariser:
    
    def __init__(self,token):
        self.token = token
        self.g = Github(token)
    
    def initialise_repo(self,owner,repo):
        self.owner = owner
        self.repo = repo
    
    def get_contributors_list(self):
        
        query_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contributors?page=1&per_page=10000"
        params = {
                "state": "open",
            }
        headers = {'Authorization': f'token {self.token}'}
        r = requests.get(query_url, headers=headers, params=params)
        data = r.json()
        count = 2

        while(len(r.json())!=0):
            query_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contributors?page={count}&per_page=10000"
            params = {
                    "state": "open",
                    }
            headers = {'Authorization': f'token {self.token}'}
            r = requests.get(query_url, headers=headers, params=params)
            data = data + r.json()
            count = count + 1
        print(len(data))
        with open(f"data/{self.repo}_contributors.json","w") as outfile:
            json.dump(data,outfile)
    
    def get_contributor_login(self):
        contributor_list = []
        with open(f"data/{self.repo}_contributors.json",) as inpFile:
            contributor_list = json.load(inpFile)
            
        user_names = []
        for user in contributor_list:
            if user.get('login') != None:
                user_names.append(user['login'])
                #pprint(user)
        data = {'users': user_names}
        with open(f"data/{self.repo}_all_users.json","w") as outfile:
            json.dump(data,outfile)
    
    // work need to be done
    def get_all_user_repos(self):
        
        user_names = []
        with open(f"data/{self.repo}_all_users.json",) as inpFile:
            user_names = json.load(inpFile)['users']
        user_names = user_names[:10]
        data = []
        unfiltered_repo_list = []
        for username in user_names:
            print(username)
            query_url = f"https://api.github.com/users/{username}/repos"
            pprint(query_url)
            params = {
                    "state": "open",
                    }
            headers = {'Authorization': f'token {self.token}'}
            r = requests.get(query_url, headers=headers, params=params)
            unfiltered_repo_list.append(r.json())
            data.append({f"{username}":r.json})
        print(data)
        with open(f"data/{self.repo}_all_users_repo.json","w") as outfile:
            json.dump(data,outfile)
    
    

classObject = RepoSummariser("47623b5391cd52f3289b24cbfdfbf19c61092ea0")
classObject.initialise_repo("oppia","oppia")
#classObject.get_contributors_list()

#classObject.get_contributor_login()        
classObject.get_all_user_repos()