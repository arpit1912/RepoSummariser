# Importing the Libraries
from github import Github
import requests
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
        print(data)
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
    
    def get_all_user_repos(self):
        
        user_names = []
        with open(f"data/{self.repo}_all_users.json",) as inpFile:
            user_names = json.load(inpFile)['users']
        user_names = user_names[:10]
        data = {}
        for username in user_names:
            print(username)
            query_url = f"https://api.github.com/users/{username}/repos"
            pprint(query_url)
            params = {
                    "state": "open",
                    }
            headers = {'Authorization': f'token {self.token}'}
            r = requests.get(query_url, headers=headers, params=params)
            data[f"{username}"] = r.json()
        print(data)
        with open(f"data/{self.repo}_all_users_repo.json","w") as outfile:
            json.dump(data,outfile)
    
    def repo_details(self,owner,repo):
        query_url = f"https://api.github.com/repos/{owner}/{repo}"
        params = {
            "state": "open",
        }
        headers = {'Authorization': f'token {self.token}'}
        r = requests.get(query_url, headers=headers, params=params)
        return r.json()            
    
    def calculated_contribution(self,owner,main_repo):
        
        contributor_list = []
        with open(f"data/{main_repo}_contributors.json",) as inpFile:
            contributor_list = json.load(inpFile)
            
        total_contributions = 0
        user_contribution = 0
        for contributor in contributor_list:
            if(contributor['contributions'] > 0):
                total_contributions += contributor['contributions']
                if(contributor['login'] == owner):
                    print(contributor['login'], " this is the match we found")
                    user_contribution = contributor['contributions']
            
        
        return total_contributions, user_contribution
    
    def filter_valid_repos(self):
        
        user_repos = []
        with open(f"data/{self.repo}_all_users_repo.json",) as inpFile:
            user_repos = json.load(inpFile)
        
        data = {}
        for user,repos in user_repos.items():
            temp_repo_list = []
            for repo in repos:
                
                if repo['fork'] is True:
                    # if the repo is forked from somewhere else
                    owner,reponame = repo['full_name'].split("/")
                    original_repo_data = self.repo_details(owner,reponame)
                    # find the complete detail of the Repo
                    
                    if original_repo_data.get('source') !=None: # this field stores the original repo holder
                        main_owner,main_repo = original_repo_data['source']['full_name'].split("/") # find the owner and name 
                        
                        temp_owner,temp_repo = self.owner, self.repo
                        self.initialise_repo(main_owner,main_repo)
                        self.get_contributors_list()
                        self.initialise_repo(temp_owner,temp_repo)
                        
                        total_contri,user_contri = self.calculated_contribution(owner,main_repo)
                        
                        print(total_contri," THis is the ontri ",user_contri, " for the user ", user)
                        
                        if(user_contri > 0):
                            temp_repo_list.append(original_repo_data['source'])    
                            print(total_contri, user_contri)
                    
            data[f"{user}"] = temp_repo_list
         
        with open(f"data/{self.repo}_all_users_filtered_repo.json","w") as outfile:
            json.dump(data,outfile)   
    
    def RepoExploration(self):
        repos = []
        with open(f"data/{self.repo}_all_users_filtered_repo.json",) as inpFile:
            repos = json.load(inpFile)
        #pprint(repos)
        DATA = {}
        for user,repos_data in repos.items():
            data = {}
            for repo_data in repos_data:
                
                owner,repo = repo_data['full_name'].split('/')
                print(user,owner,repo)
                count = 2
                query_url = f"https://api.github.com/repos/{owner}/{repo}/commits?page=1&per_page=10000"
                params = {
                    "state": "open",
                }
                headers = {'Authorization': f'token {self.token}'}
                r = requests.get(query_url, headers=headers, params=params)
                data[f"{owner}_{repo}"] = r.json()
    
                while(len(r.json())!=0):
                    query_url = f"https://api.github.com/repos/{owner}/{repo}/commits?page={count}&per_page=10000"
                    params = {
                            "state": "open",
                            }
                    headers = {'Authorization': f'token {self.token}'}
                    r = requests.get(query_url, headers=headers, params=params)
                    data[f"{owner}_{repo}"] = data[f"{owner}_{repo}"] + r.json()
                    count = count + 1
            DATA[f"{user}"] = data
                
        with open(f"data/{self.repo}_users_repo_commits.json","w") as outfile:
            json.dump(DATA,outfile,indent=4)
    
    def filtered_commits(self):
        data = {}
        print(f"data/{self.repo}_users_repo_commits.json")
        with open(f"data/{self.repo}_users_repo_commits.json",) as inpFile:
            data = json.load(inpFile)
        
        new_data = {}
        for user,repos in data.items():
            temp = {}
            for repo_name,commits in repos.items():
                usefull_commits = []
                #total_commits = len(repo)
                for commit in commits:
                    #print(commit["author"])
                    if commit["author"] != None and commit["author"]["login"] == user:
                        print(user,commit["author"]["login"],usefull_commits)
                        usefull_commits.append(commit["sha"])
                    
                temp[repo_name] = usefull_commits
                
            new_data[user] = temp
        with open(f"data/{self.repo}_users_repo_sha_usefull_commits.json","w") as outfile:
            json.dump(new_data,outfile,indent=4)
    
    def commit_sha_exploration(self):
        data = {}
        with open(f"data/{self.repo}_users_repo_sha_usefull_commits.json",) as Inpfile:
            data = json.load(Inpfile)
        
        user_data = {}
        for user,repos_dict in data.items():
            repo_data = {}
            
            for repo_name, shas in repos_dict.items():
            
                total_add = 0
                total_del = 0
                
                total_files = []
                
                owner = repo_name.split("_")[0]
                repo = repo_name[len(owner)+1:]
                print(owner,repo)
                
                for sha in shas:
                    message = []
                    query_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
                    params = {
                            "state": "open",
                            }
                    headers = {'Authorization': f'token {self.token}'}
                    print(query_url)
                    r = requests.get(query_url, headers=headers, params=params)
                    temp = r.json()
                    
                    #adding a basic check to remove asset files like images
                    @arpit1912 check if below condition works
                    if (temp["stats"]["additions"] != 0 and temp["stats"]["deletions"] != 0) : 
                        total_add += temp["stats"]["additions"]
                        total_del += temp["stats"]["deletions"]
                        #temp_message = temp["message"]
                        message.append(temp["commit"]["message"])
                        files = temp["files"]
                        for file in files:
                            temp_file = {}
                            for key,val in file.items():
                                if key == "filename" or key == "status" or key == "additions" or key == "deletions" or key == "patch":
                                    temp_file[key] = val
                            #print(temp_file)
                            temp_file["message"] = message
                            total_files.append(temp_file)
                            #print(total_files)
                        
                    #print (sha)
                repo_data[repo_name] = {"additions": total_add,"deletions": total_del,"files":total_files}
            user_data[user] = repo_data
        
        with open(f"data/{self.repo}_users_repo_files_data.json","w") as outfile:
            json.dump(user_data,outfile,indent=4)
        
    def rate_check(self):
        query_url = f"https://api.github.com/rate_limit"
        print(query_url)
        headers = {'Authorization': f'token {self.token}'}
        r = requests.get(query_url, headers=headers)
        pprint(r.json())
        #pprint(repos)
                 
classObject = RepoSummariser("64549044554cf80b6a794f7a3642cfc8d218ae17")
classObject.initialise_repo("arpit1912","SE-gamedev")
#classObject.get_contributors_list()
#lassObject.get_contributor_login()        
#classObject.get_all_user_repos()
#classObject.filter_valid_repos()
#classObject.RepoExploration()
#classObject.filtered_commits()
#classObject.rate_check()
classObject.commit_sha_exploration()
