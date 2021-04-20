# Importing the Libraries
from github import Github       # The Github Api Library
import requests                 # for Request Handling
import json                     # for Data handling
import mimetypes                # for filtering the files
import re                       # for writing Regular Expressions
from pprint import pprint
from datetime import datetime, date, timedelta

class RepoSummariser:
    
    def __init__(self,token):
        ''' The init will take an active token of a user '''

        self.token = token
        self.g = Github(token)
    
    def initialise_repo(self,owner,repo):
        ''' initialise the owner and the repo name through this function '''

        self.owner = owner
        self.repo = repo
    
    def get_contributors_list(self):
        ''' this Function give the Contributor list of the repo given'''

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
        
        with open(f"data/{self.repo}_contributors.json","w") as outfile:
            json.dump(data,outfile)

    def get_contributor_login(self):
        ''' Find the login details of the contributors'''

        contributor_list = []
        with open(f"data/{self.repo}_contributors.json",) as inpFile:
            contributor_list = json.load(inpFile)
            
        user_names = []
        for user in contributor_list:
            if user.get('login') != None:
                user_names.append(user['login'])

        query_url = f"https://api.github.com/user"
        params = {
            "state": "open",
        }
        headers = {'Authorization': f'token {self.token}'}
        r = requests.get(query_url, headers=headers, params=params)
        
        user_data = r.json()

        self.main_login = user_data['login']
        user_names.append(user_data['login'])
        data = {'users': user_names}

        with open(f"data/{self.repo}_all_users.json","w") as outfile:
            json.dump(data,outfile)
    
    def get_all_user_repos(self):
        ''' Get all the Repo on which the user works using the login details '''
    
        user_names = []
        with open(f"data/{self.repo}_all_users.json",) as inpFile:
            user_names = json.load(inpFile)['users']
    
        user_names = user_names[:10] # considering only 10 users due to limitation in API Calls 
        data = {}
        for username in user_names:
            query_url = f"https://api.github.com/users/{username}/repos"
            pprint(query_url)
            params = {
                    "state": "open",
                    }
            headers = {'Authorization': f'token {self.token}'}
            r = requests.get(query_url, headers=headers, params=params)
            data[f"{username}"] = r.json()
        
        with open(f"data/{self.repo}_all_users_repo.json","w") as outfile:
            json.dump(data,outfile)
    
    def repo_details(self,owner,repo):
        ''' Fetch a more elaborate  detail of the Repo  '''

        query_url = f"https://api.github.com/repos/{owner}/{repo}"
        params = {
            "state": "open",
        }
        headers = {'Authorization': f'token {self.token}'}
        r = requests.get(query_url, headers=headers, params=params)
        #pprint(r.json())
        with open(f"data/{repo}_data.json","w") as outfile:
            json.dump(r.json(),outfile,indent=4)
        
        return r.json()            
    
    def calculated_contribution(self,owner,main_repo):
        '''  calcuate the contribution of a user in the Repo '''

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
        ''' filter the repo based on the user contribution '''
    
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
            json.dump(data,outfile,indent = 4)   
    
    def get_repo_commits(self):
        ''' Find the commits in a repo '''
    
        repos = []
        with open(f"data/{self.repo}_all_users_filtered_repo.json",) as inpFile:
            repos = json.load(inpFile)
    
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
                data[f"{owner}/{repo}"] = r.json()
    
                while(len(r.json())!=0):
                    query_url = f"https://api.github.com/repos/{owner}/{repo}/commits?page={count}&per_page=10000"
                    params = {
                            "state": "open",
                            }
                    headers = {'Authorization': f'token {self.token}'}
                    r = requests.get(query_url, headers=headers, params=params)
                    data[f"{owner}/{repo}"] = data[f"{owner}/{repo}"] + r.json()
                    count = count + 1
    
            DATA[f"{user}"] = data
                
        with open(f"data/{self.repo}_users_repo_commits.json","w") as outfile:
            json.dump(DATA,outfile,indent=4)
    
    def filtered_commits(self):
        ''' store only the relavant commits which are usefull to us'''
    
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
                    print(repo_name, commit["author"])
                    if commit["author"] != None and bool(commit["author"]) and commit["author"]["login"] == user:
                        #print(user,commit["author"]["login"],usefull_commits)
                        usefull_commits.append(commit["sha"])
                    
                temp[repo_name] = usefull_commits
                
            new_data[user] = temp
    
        with open(f"data/{self.repo}_users_repo_sha_usefull_commits.json","w") as outfile:
            json.dump(new_data,outfile,indent=4)
    
    def commit_sha_exploration(self):
        ''' Fetch the data from the filtered commit details '''
    
        data = {}
        with open(f"data/{self.repo}_users_repo_sha_usefull_commits.json",) as Inpfile:
            data = json.load(Inpfile)
        
        repos = {}
        with open(f"data/{self.repo}_all_users_filtered_repo.json",) as inpFile:
            repos = json.load(inpFile)
            
        user_data = {}
        for user,repos_dict in data.items():
           
            repo_data = {}
            
            for repo_name, shas in repos_dict.items():
            
                total_add = 0
                total_del = 0
                
                total_files = []
                
                owner = repo_name.split("/")[0]
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
                    
                    
                    if (temp["stats"]["additions"] != 0 and temp["stats"]["deletions"] != 0) : 
                        total_add += temp["stats"]["additions"]
                        total_del += temp["stats"]["deletions"]
                        #temp_message = temp["message"]
                        message.append(temp["commit"]["message"])
                        files = temp["files"]
                        for file in files:
                            temp_file = {}
                            eligible = True
                            file_type = ""
                            for key,val in file.items():
                                if key == "filename":
                                    file_type = mimetypes.guess_type(val)[0]
                                    if file_type == None:
                                        file_type = "none"
                                    
                                    matchType = re.match( r'(image|video|audio).*', file_type, re.M|re.I)
                                    if matchType:
                                        eligible = False
                                    else:
                                        temp_file["type"] = file_type
                                if key == "filename" or key == "status" or key == "additions" or key == "deletions" or key == "patch":
                                    temp_file[key] = val
                            temp_file["message"] = message
                            temp_file["date"] = temp["commit"]["author"]["date"]
                            if eligible is True:
                                total_files.append(temp_file)
                            
                repo_data[repo_name] = {"additions": total_add,"deletions": total_del,"files":total_files}
            user_data[user] = repo_data
        
        with open(f"data/{self.repo}_users_repo_files_data.json","w") as outfile:
            json.dump(user_data,outfile,indent=4)

    def rate_check(self):
        ''' To check the number of request left for the given token '''

        query_url = f"https://api.github.com/rate_limit"
        print(query_url)
        headers = {'Authorization': f'token {self.token}'}
        r = requests.get(query_url, headers=headers)
        pprint(r.json())

    def get_user_last_year_commits(self,user):
        headers = {'Authorization': f'token {self.token}'}
        query = """
        {{
          user(login: "{user}") {{
            contributionsCollection (from: "{enddate}", to: "{startdate}") {{
              contributionCalendar {{
                totalContributions
                weeks {{
                  contributionDays {{
                    contributionCount
                    weekday
                    date
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        startdate = datetime.utcnow()
        startdate -= timedelta(days = 1)
        print(startdate)
        variables = {
            'user': user,
            'startdate': startdate.strftime("%Y-%m-%dT00:00:00"),
            'enddate': (startdate - timedelta(days = (365))).strftime("%Y-%m-%dT00:00:00")
        }
        print(query.format(**variables))
        request = requests.post('https://api.github.com/graphql', json={'query': query.format(**variables)}, headers=headers)
        #pprint(request.json())
        return request.json()

    def repo_graph_details(self,owner,name):
        
        headers = {'Authorization': f'token {self.token}'}
        query ="""
        {{
          repository(owner: "{owner}", name: "{name}") {{
            repositoryTopics(first: 100) {{
              edges {{
                node {{
                  topic {{
                    name
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        variables = {
           'owner' : owner,
           'name' :  name
        }

        request = requests.post('https://api.github.com/graphql', json={'query': query.format(**variables)}, headers=headers)
        print(query.format(**variables))
        #print(request.json())
        
        data = request.json()
        data = data["data"]["repository"]["repositoryTopics"]["edges"]
        
        return data 
        with open(f"data/temp_graph_data.json","w") as outfile:
            json.dump(request.json(),outfile,indent=4)
    
    def user_analytic_details(self,user):
        
        query_url = f"https://api.github.com/users/{user}"
        params = {
            "state": "open",
        }
        headers = {'Authorization': f'token {self.token}'}
        r = requests.get(query_url, headers=headers, params=params)
        
        data = r.json()
        
        query_url = f"https://api.github.com/users/{user}/orgs"
        
        r = requests.get(query_url, headers=headers, params=params)
        
        data['orgs'] = r.json()
        
        return data
    
    def repo_languages(self,owner,repo):
        
        query_url = f"https://api.github.com/repos/{owner}/{repo}/languages"
        params = {
            "state": "open",
        }
        headers = {'Authorization': f'token {self.token}'}
        r = requests.get(query_url, headers=headers, params=params)
        
        data = r.json()
        return data

    def main_repo_details(self):

        self.repo_details(self.owner,self.repo)   

        repo_data = []
        contributors = []

        with open(f"data/{self.repo}_data.json",) as inpFile:
            repo_data = json.load(inpFile)

        with open(f"data/{self.repo}_contributors.json",) as inpFile:
            contributors = json.load(inpFile)

        tags = self.repo_graph_details(self.owner,self.repo)
        processed_tags = []
        for node in tags:
            processed_tags.append(node['node']['topic']['name'])

        total_commits, garbage =  self.calculated_contribution(self.owner,self.repo)            
        
        repo_processed_data = {
                                         'created_at': repo_data['created_at'],
                                         'updated_at': repo_data['updated_at'],
                                         "description": repo_data["description"],
                                         'size': repo_data['size'],
                                         'has_wiki': repo_data['has_wiki'],
                                         'open_issues_count': repo_data['open_issues_count'],
                                         'watchers_count': repo_data["watchers_count"],
                                         "forks_count":repo_data["forks_count"],
                                         'tags' : processed_tags,
                                         "total_contributors" : len(contributors),
                                         "total_commits" : total_commits,
                                         "languages" : self.repo_languages(self.owner,self.repo)
        }

        pprint(repo_processed_data)
        with open(f"data/{self.repo}_main_data.json","w") as outfile:
            json.dump(repo_processed_data, outfile, indent=4)
        return repo_processed_data

    def repo_analysis_details(self):
        repos_details = []
        with open(f"data/{self.repo}_all_users_filtered_repo.json",) as inpFile:
            repos_details = json.load(inpFile)
        
        user_repo_details = {}
        with open(f"data/{self.repo}_users_repo_files_data.json",) as inpFile:
            user_repo_details = json.load(inpFile)
        
        
        
        for user,repos_data in repos_details.items():
            repos = user_repo_details[user]
            
            for repo_data in repos_data:
                owner,repo = repo_data['full_name'].split('/')
                tags = self.repo_graph_details(owner,repo)
                processed_tags = []
                for node in tags:
                    processed_tags.append(node['node']['topic']['name'])
                
                #print(processed_tags)
                
                repo_processed_data = repos[f"{owner}/{repo}"]
                contributors = []
                with open(f"data/{repo}_contributors.json",) as inpFile:
                    contributors = json.load(inpFile)
                
                repo_processed_data = {  "additions": repo_processed_data["additions"],
                                         "deletions": repo_processed_data["deletions"],
                                         'created_at': repo_data['created_at'],
                                         'updated_at': repo_data['updated_at'],
                                         'size': repo_data['size'],
                                         'has_wiki': repo_data['has_wiki'],
                                         'open_issues_count': repo_data['open_issues_count'],
                                         'watchers_count': repo_data["watchers_count"],
                                         "forks_count":repo_data["forks_count"],
                                         'tags' : processed_tags,
                                         'commit_files': repo_processed_data['files'],
                                          "total_contributors" : len(contributors),
                                          "languages" : self.repo_languages(owner,repo)
                                          }
                repos[f"{owner}/{repo}"] = repo_processed_data
            
            
            ## processing user data from here
            user_data = self.user_analytic_details(user)
            
            user_repo_details[user] = {    'login' : user_data['login'],
                                            'type' : user_data['type'],                                       
                                            'bio': user_data['bio'],
                                            'blog': user_data['blog'],
                                            'company': user_data['company'],
                                            'contributions': self.get_user_last_year_commits(user),
                                            'created_at': user_data['created_at'],
                                            'public_repos': user_data['public_repos'],
                                            'followers': user_data['followers'],
                                            'organizations': user_data['orgs'],
                                            'repos':repos
                                            }
        other_user_data = {}
        main_user_data = {}
        for key,value in user_repo_details.items():
            if key == self.main_login:
                print("main user came!")
                main_user_data[key] = value
            else:
                other_user_data[key] = value

        with open(f"data/{self.repo}_users_repo_complete_data.json","w") as outfile:
            json.dump(other_user_data,outfile,indent=4)


        with open(f"data/user_complete_data.json","w") as outfile:
            json.dump(main_user_data,outfile,indent=4)
   
    def start_processing(self):
        ''' Driving function to run the tool '''

        print( "Starting the Data Extraction Process")
        self.get_contributors_list()
        self.get_contributor_login()
        self.get_all_user_repos()
        self.filter_valid_repos()
        self.get_repo_commits()
        
        self.filtered_commits()
        self.commit_sha_exploration()
        self.repo_analysis_details()
        self.main_repo_details()
        print( "Ending the Data Extraction Process")
    

if __name__ == "__main__":
    classObject = RepoSummariser("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")
    classObject.rate_check()
    classObject.initialise_repo("krish7777","food4all")
    classObject.start_processing()