from fpdf import FPDF, HTMLMixin
import json
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import collections, colors, transforms
from pprint import pprint
import statistics
from datetime import datetime
import os
import random
from analyser import Analyser
from tool import RepoSummariser

class ActiveNess(Analyser, RepoSummariser):
    
    def __init__(self,repo,user,token):
        Analyser.__init__(self,repo,user)
        RepoSummariser.__init__(self,token)
        self.initialise_repo(user,repo)
    
    def OSS_score(self,value,avg_range):
        MIN,MAX = avg_range
        MIN = float(MIN)
        MAX = float(MAX)
        if value == 0:
            return 0
        elif value < MIN:
            return 0.2
        elif value >= MIN and value <=MAX:
            return 0.3
        elif value > MAX:
            return 0.45
    
    def PublicRepoCount_score(self,value,avg_range):
        MIN,MAX = avg_range
        MIN = float(MIN)
        MAX = float(MAX)

        if value == 0:
            return 0
        elif value < MIN:
            return 0.2
        elif value >= MIN and value <=MAX:
            return 0.3
        elif value > MAX:
            return 0.45
        
    def Commit_score(self,value,avg_range):
        MIN,MAX = avg_range
        MIN = float(MIN)
        MAX = float(MAX)

        if value == 0:
            return 0
        elif value < MIN:
            return 0.4
        elif value >= MIN and value <=MAX:
            return 0.7
        elif value > MAX:
            return 1
    
    def Age_score(self,value,avg_range):
        MIN,MAX = avg_range
        MIN = float(MIN)
        MAX = float(MAX)

        if value < MIN:
            return 0.1
        elif value >= MIN and value <=MAX:
            return 0.15
        elif value > MAX:
            return 0.2
    
    def Follower_score(self,value,avg_range):
        MIN,MAX = avg_range
        MIN = float(MIN)
        MAX = float(MAX)        
        if value < MIN:
            return 0.1
        elif value >= MIN and value <=MAX:
            return 0.18
        elif value > MAX:
            return 0.25
    
    def Organisation_score(self,HasOrganisation):

        if HasOrganisation is True:
            return 0.15
        else:
            return 0
    
    def UserCommitCountRatio_score(self,ratio):
        
        if ratio < 0.2:
            return 0.2
        elif ratio < 0.4:
            return 0.3
        elif ratio < 0.6:
            return 0.4
        elif ratio < 0.8:
            return 0.5
        elif ratio < 1:
            return 0.6
        elif ratio < 1.4:
            return 0.75
        elif ratio < 1.8:
            return 0.9
        elif ratio < 2:
            return 1
        else:
            return 1.35
        
    def UserAgeRatio_score(self,ratio):
        
        if ratio < 0.2:
            return 0.1
        elif ratio < 0.4:
            return 0.15
        elif ratio < 0.6:
            return 0.2
        elif ratio < 0.8:
            return 0.25
        else:
            return 0.3
      
    def Wiki_score(self,HasWiki):
        if HasWiki is True:
            return 0.2
        else:
            return 0
    
    def OpenIssues_score(self,count):
        
        if count < 50:
            return 0.1
        else:
            return 0.2
    
    def Fork_score(self,count):
        if count < 50:
            return 0.05
        else:
            return 0.1
    
    def Watchers_score(self,count):
        if count < 50:
            return 0.05
        else:
            return 0.1

    def Tags_score(self,HasTags):
        if HasTags is True:
            return 0.15
        else:
            return 0
    
    def Calculate_Score(self,filename = ""):
        
        ContributorData = self.getFileData(filename)
        
        today = datetime.utcnow().year
        userScores = []
        for user,userData in ContributorData.items():
            
            UserStartdate = int(userData['created_at'].split('-')[0])
            user_age = today - UserStartdate

            total_days = 0
            commit = 0
            contribution_details = userData["contributions"]["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
            for weeklydict in contribution_details:
                for dailydict in weeklydict['contributionDays']:
                    total_days += 1
                    commit += (dailydict['contributionCount'])
            
            

            Repo_scores = []

            for reponame,repoData in userData['repos'].items():
                owner,name = reponame.split('/',1)
                
                total_commits,user_commits = self.calculated_contribution(user,name)

                total_contributors = repoData['total_contributors']
                avg_total_commit = total_commits / total_contributors

                commit_ratio = user_commits / avg_total_commit

            

                startdate = int(repoData['created_at'].split('-')[0])
                endDate = int(repoData['updated_at'].split('-')[0])

                Age = endDate - startdate
                Age = Age if Age > 0 else 1

                age_ratio = user_age / Age



                has_wiki = repoData['has_wiki']
                open_issues_count = repoData['open_issues_count']
                fork_count = repoData['forks_count']
                watchers_count = repoData['watchers_count']
                tags = True if len(repoData['tags']) > 0 else False

                score = self.UserCommitCountRatio_score(commit_ratio) + self.UserAgeRatio_score(age_ratio) + self.Wiki_score(has_wiki) + self.OpenIssues_score(open_issues_count) + self.Fork_score(fork_count) + self.Watchers_score(watchers_count) + self.Tags_score(tags)
                
                Repo_scores.append(score)
            print(Repo_scores)

            avg_repo_score = statistics.mean(Repo_scores)
            
            user_avg_commit = commit / total_days
            total_OSS_repos = len(userData['repos'].items())
            public_repos = userData['public_repos']
            
            followers = userData['followers']
            HasOrganisation = True if len(userData['organizations']) > 0 else False
            
            user_score =(   
                            self.OSS_score(total_OSS_repos,self.OpenSourceProjectCount()) + 
                            self.PublicRepoCount_score(public_repos,self.UserPublicRepoCount()) + 
                            self.Commit_score(user_avg_commit,self.CommitsPerDayAvg()) + 
                            self.Age_score(user_age,self.AccountAge()) + 
                            self.Follower_score(followers,self.FollowersCount()) + 
                            self.Organisation_score(HasOrganisation)
                        )
            userScores.append(user_score + avg_repo_score)
        
        print(statistics.mean( userScores))

        return statistics.mean(userScores)
        
            
if __name__ == "__main__":
    score = ActiveNess("food4all","krish7777","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")
    score.Calculate_Score("user_complete_data.json")
