'''
@arpit1912:

user data to be pulled:
    login
    type : user/organization/enterprize
    'bio': 
    'blog': 
    'company': 
    'created_at': 
    'public_repos':
    followers:
    organizations: query_url = f"https://api.github.com/users/{user}/orgs"

    query:
        query_url = f"https://api.github.com/users/{user}"
        params = {
            "state": "open",
        }
        headers = {'Authorization': f'token {token}'}
        r = requests.get(query_url, headers=headers, params=params)


repo data to be pulled
    created at : 
    updated at :
    "size"
    "has_wiki"
    "forks":
    "open_issues":
    "watchers":
    "network_count":
    "subscribers_count":

    query:
     query_url = f"https://api.github.com/repos/{owner}/{repo}"
        params = {
            "state": "open",
        }
        headers = {'Authorization': f'token {self.token}'}
        r = requests.get(query_url, headers=headers, params=params)
    '''




# Importing the Libraries
from github import Github       # The Github Api Library
import requests                 # for Request Handling
import json                     # for Data handling
import mimetypes                # for filtering the files
import re                       # for writing Regular Expressions
from pprint import pprint


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
        with open(f"data/temp_data.json","w") as outfile:
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
            json.dump(data,outfile)   
    

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
                    #print(commit["author"])
                    if commit["author"] != None and commit["author"]["login"] == user:
                        print(user,commit["author"]["login"],usefull_commits)
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
        print( "Ending the Data Extraction Process")
    
    def Repo_Details(self):
        
        query_url = f"https://api.github.com/users/sam3926"
        print(query_url)
        header = {'Authorization': f'token {self.token}'}
        r = requests.get(query_url,headers = header)
        pprint(r.json())

    def graph_intro(self):
        headers = {'Authorization': f'token {self.token}'}
        query = """
        {
          
            name
            kind
            description
            fields {
              name
            }
          
        }
        """

        request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
        #print(request.json())
        with open(f"data/temp_graph_inspect_data.json","w") as outfile:
            json.dump(request.json(),outfile,indent=4)
        
    def repo_graph_details(self):
        
        headers = {'Authorization': f'token {self.token}'}
        query = """
        {
          repository(owner: "oppia", name: "oppia") {
            repositoryTopics(first: 10) {
              edges {
                node {
                  topic {
                    name
                  }
                }
              }
            }
          }
        }
        """

        request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
        #print(request.json())
        with open(f"data/temp_graph_data.json","w") as outfile:
            json.dump(request.json(),outfile,indent=4)
            
if __name__ == "__main__":
    classObject = RepoSummariser("<token>")
    classObject.rate_check()
    classObject.initialise_repo("arpit1912","SE-gamedev")
    #classObject.start_processing()
    classObject.graph_intro()
    #classObject.Repo_Details()