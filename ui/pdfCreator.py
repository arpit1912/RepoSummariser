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
from activeness import ActiveNess

class PDF(FPDF, HTMLMixin):
    def __init__(self):
        super().__init__()
        self.WIDTH = 210
        self.HEIGHT = 297
        
    def lines(self):
        self.rect(5.0, 5.0, 200.0,287.0)
        
    def header(self):
        # Custom logo and positioning
        # Create an `assets` folder and put any wide and short image inside
        # Name the image `logo.png`
        #self.image('assets/logo.png', 10, 8, 33)
        self.set_font('Arial', 'B', 11)
        self.cell(self.WIDTH - 80)
        self.cell(60, 1, 'RepoSummariser', 0, 0, 'R')
        self.ln(20)
        
    def footer(self):
        # Page numbers in the footer
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def page_body(self, images):
        # Determine how many plots there are per page and set positions
        # and margins accordingly
        '''
        if len(images) == 3:
            self.image(images[0], 15, 25, self.WIDTH - 30)
            self.image(images[1], 15, self.WIDTH / 2 + 5, self.WIDTH - 30)
            self.image(images[2], 15, self.WIDTH / 2 + 90, self.WIDTH - 30)
        elif len(images) == 2:
            self.image(images[0], 15, 25, self.WIDTH - 30)
            self.image(images[1], 15, self.WIDTH / 2 + 5, self.WIDTH - 30)
        else:
            self.image(images[0], 15, 25, self.WIDTH - 30)
        
        '''
        self.add_page()
        self.lines()
        #page 1 : general main repo stats, user stats
        
        self.set_xy(10.0,17.0)
        self.set_font('Arial', 'B', 18)
        self.set_text_color(186, 80, 100)
        #self.write_html("Analysis of repository + <b> reponame </b>")
        self.multi_cell(w=0, h=14.0, align='C', txt="Analysis of repository "+  reponame  + " and userID " + username, border="")
        
        self.set_xy(10.0,self.get_y() + 2)
        self.set_font('Arial', 'B', 16)
        self.set_text_color(186, 80, 100)
        self.cell(w=0.0, h=10.0, align='L', txt= reponame + " details" , border="T", link=repolink)
        
        self.set_xy(14.0,self.get_y()+10)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.cell(w=18.0, h=9.0, align='L', txt= "About: ", border=0)
        
        self.set_xy(self.get_x(), self.get_y())
        self.set_font('Arial', '', 14)
        self.multi_cell(w=0.0, h=9.0, align='L', txt= repo_about, border=0)
        
        self.set_xy(14, self.get_y())
        self.set_font('Arial', 'B', 14)
        self.cell(w=32.0, h=9.0, align='L', txt= "Project tags: ", border=0)
        
        self.set_xy(self.get_x(), self.get_y())
        self.set_font('Arial', '', 14)
        self.multi_cell(w=0.0, h=9.0, align='L', txt= repo_tags, border=0)
        
        self.set_xy(14.0,self.get_y())
        self.set_font('Arial', 'B', 14)
        self.multi_cell(w=0.0, h=8.0, align='L', txt= "Project stats: ", border=0)
        
        self.set_xy(22.0,self.get_y())
        self.set_font('Arial', '', 13)
        self.multi_cell(w=0.0, h=6.0, align='L', txt= "Project Status: Active (last commit on "+repo_lastcommitdate+")\n" +
                        "Date of creation: " + repo_doc + "\n" +
                        "Contributors: " + repo_contricount + "\n" +
                        "Commits: " + repo_contricount + "\n" +
                        "Forks: " + repo_forkscount + "\n" +
                        "Stars: " + repo_starscount + "\n" +
                        "Open issues: " + repo_openissuecount + "\n", border=0)
        
        #repository language split
        self.set_xy(14.0,self.get_y()+5)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=0.0, h=9.0, align='L', txt= "Languages: \n", border=0)
        self.image('images/language.png', 18.0, self.get_y() + 2.0, self.WIDTH - 40, 15)
        
        #types of contributors accounts
        self.set_xy(14.0,self.get_y() + 25)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=0.0, h=9.0, align='L', txt= "Contributor account types: \n", border=0)
        self.image('images/ContributorType.png', 18.0, self.get_y() + 2.0, self.WIDTH - 40, 15)
        
        
        
        #page 2 : report start with activeness score user and repo, contine
        #decide what text stas to add, charts etc
        
        self.add_page()
        self.lines()
        
        self.set_xy(10.0,15.0)
        self.set_font('Arial', 'B', 22)
        self.set_text_color(186, 80, 100)
        self.cell(w=0, h=15.0, align='C', txt="Analysis report", border="B")
        
        self.set_xy(10.0,45.0)
        self.set_font('Arial', 'B', 20)
        self.cell(w=0.0, h=0.0, align='L', txt= "Activeness score:" , border=0)
        
        self.set_xy(76.0,41.0)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.cell(w=0.0, h=0.0, align='L', txt= username + ": " + user_activescore, border=0)
        
        self.set_xy(76.0,49.0)
        self.cell(w=0.0, h=0.0, align='L', txt= reponame + " contributors (avg): " + repo_activescore, border=0)
        
        self.set_xy(10.0,self.get_y() + 15)
        self.set_font('Arial', 'B', 20)
        self.set_text_color(186, 80, 100)
        self.cell(w=0.0, h=0.0, align='L', txt= "Detailed comparison:" , border=0)
        
        height_y = self.get_y()+12
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=7.0, align='C', txt= reponame + " contributors minimal average", border="R")
        
        self.set_font('Arial', 'B', 12)
        self.set_xy(115.0,height_y)
        self.cell(w=30.0, h=7.0, align='C', txt= username, border="")
        
        self.set_font('Arial', 'B', 10)
        self.set_xy(145.0,height_y)
        self.multi_cell(w=55.0, h=7.0, align='C', txt= reponame + " contributors maximal average", border="L")
        
        #commits per day
        height_y = self.get_y()
        
        self.set_xy(5.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=50.0, h=9.0, align='C', txt= "Commits per day", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= repo_cmin_commitperday, border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=30.0, h=9.0, align='C', txt= user_commitperday, border="")
        
        self.set_xy(145.0,height_y)
        self.multi_cell(w=55.0, h=9.0, align='C', txt= repo_cmax_commitperday, border="L")
        
        #Open source projects contributed to
        height_y = self.get_y()
        
        self.set_xy(5.0,height_y)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=50.0, h=9.0, align='C', txt= "Open source projects count", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= repo_cmin_oscount, border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=30.0, h=9.0, align='C', txt= user_oscount, border="")
        
        self.set_xy(145.0,height_y)
        self.multi_cell(w=55.0, h=9.0, align='C', txt= repo_cmax_oscount, border="L")
        
        #Public repositories
        height_y = self.get_y()
        
        self.set_xy(5.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=50.0, h=9.0, align='C', txt= "Public repositories", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= repo_cmin_publicrepocount, border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=30.0, h=9.0, align='C', txt= user_publicrepocount, border="")
        
        self.set_xy(145.0,height_y)
        self.multi_cell(w=55.0, h=9.0, align='C', txt= repo_cmax_publicrepocount, border="L")
        
        #Account age
        height_y = self.get_y()
        
        self.set_xy(5.0,height_y)
        self.set_font('Arial', 'B', 11)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=50.0, h=9.0, align='C', txt= "Account age (yrs)", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= repo_cmin_accountage, border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=30.0, h=9.0, align='C', txt= user_accountage, border="")
        
        self.set_xy(145.0,height_y)
        self.multi_cell(w=55.0, h=9.0, align='C', txt= repo_cmax_accountage, border="L")
        
        #Followers
        height_y = self.get_y()
        
        self.set_xy(5.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=50.0, h=9.0, align='C', txt= "Followers", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= repo_cmin_followers, border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=30.0, h=9.0, align='C', txt= user_followers, border="")
        
        self.set_xy(145.0,height_y)
        self.multi_cell(w=55.0, h=9.0, align='C', txt= repo_cmax_followers, border="L")
        
        #add more if needed
        #chart plotting these parametera
        
        self.image('images/samplechart.png', 12.0, self.get_y() + 10.0, self.WIDTH - 20)
        
        self.set_xy(10.0,265)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=0.0, h=8.0, align='L', txt= "*Minimal average corresponds to (mean - std dev) while maximal average corresponds to (mean + std dev). 68% of contributors lie within this range", border="")
        
        #page 3 : language split and avg contribution chart
        
        self.add_page()
        self.lines()
        
        self.set_xy(10.0,15.0)
        self.set_font('Arial', 'B', 20)
        self.set_text_color(186, 80, 100)
        self.cell(w=0, h=15.0, align='L', txt="Language usage", border="B")
        
        height_y = self.get_y() + 20
        self.set_xy(15.0,height_y)
        self.set_font('Arial', 'B', 16)
        self.cell(w=0, h=10.0, align='C', txt="Top 5 preferred languages", border="B")
        height_y = self.get_y() + 15
        
        self.set_xy(10.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=45.0, h=9.0, align='C', txt= "Preference order", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= username, border="LR")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=80.0, h=9.0, align='C', txt= reponame + " contributors (average)", border="LR")
        
        #language 1
        height_y = self.get_y()
        self.set_xy(10.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=45.0, h=9.0, align='C', txt= "1.", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= user_languagename[0] + " - "+ user_languagepercent[0], border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=80.0, h=9.0, align='C', txt= repo_languagename[0] + " - "+ repo_languagepercent[0], border="LR")
        
        #language 2
        height_y = self.get_y()
        self.set_xy(10.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=45.0, h=9.0, align='C', txt= "2.", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= user_languagename[1] + " - "+ user_languagepercent[1], border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=80.0, h=9.0, align='C', txt= repo_languagename[1] + " - "+ repo_languagepercent[1], border="LR")
        
        #language 3
        height_y = self.get_y()
        self.set_xy(10.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=45.0, h=9.0, align='C', txt= "3.", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= user_languagename[2] + " - "+ user_languagepercent[2], border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=80.0, h=9.0, align='C', txt= repo_languagename[2] + " - "+ repo_languagepercent[2], border="LR")
        
        #language 4
        height_y = self.get_y()
        self.set_xy(10.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=45.0, h=9.0, align='C', txt= "4.", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= user_languagename[3] + " - "+ user_languagepercent[3], border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=80.0, h=9.0, align='C', txt= repo_languagename[3] + " - "+ repo_languagepercent[3], border="LR")
        
        #language 5
        height_y = self.get_y()
        self.set_xy(10.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=45.0, h=9.0, align='C', txt= "5.", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= user_languagename[4] + " - "+ user_languagepercent[4], border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=80.0, h=9.0, align='C', txt= repo_languagename[4] + " - "+ repo_languagepercent[4], border="LR")
        
        #user language chart
        self.set_xy(14.0,self.get_y()+10)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=0.0, h=9.0, align='L', txt=username + " languages: \n", border=0)
        self.image('images/UserLanguage.png', 18.0, self.get_y() + 2.0, self.WIDTH - 40, 15)
        
        #contributor language chart
        self.set_xy(14.0,self.get_y() + 25)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=0.0, h=9.0, align='L', txt= reponame + " contributors languages\n", border=0)
        self.image('images/RepoLanguage.png', 18.0, self.get_y() + 2.0, self.WIDTH - 40, 15)
        
        self.set_xy(10.0,260)
        self.set_font('Arial', 'I', 10)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=0.0, h=8.0, align='L', txt= "*Others includes all languages excluding C, C++, JAVA, Python, JS, markdown, text, HTML, typescript and css", border="")
        
        
        #page 4 : language split and avg contribution chart
        
        self.add_page()
        self.lines()
        
        self.set_xy(10.0,15.0)
        self.set_font('Arial', 'B', 20)
        self.set_text_color(186, 80, 100)
        self.cell(w=0, h=15.0, align='L', txt="Past year contributions", border="B")
        
        #user daily contribution
        height_y = self.get_y() + 20
        self.set_xy(15.0,height_y)
        self.set_font('Arial', 'B', 15)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=0, h=10.0, align='C', txt="Average commits per day ("+username+") = " + user_commitperday , border="")
        
        self.image('images/usercontrichart.png', 18.0, self.get_y() + 2.0, self.WIDTH - 40)
        
        height_y = self.get_y() + 40
        self.set_xy(15.0,height_y)
        self.set_font('Arial', 'B', 15)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=0, h=10.0, align='C', txt="Average commits per day ("+reponame+" contributors) = " + repo_c_commitperday , border="")
        
        self.image('images/contrichart.png', 18.0, self.get_y() + 2.0, self.WIDTH - 40)
        
        height_y = self.get_y() + 40
        self.set_xy(15.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=0, h=10.0, align='L', txt="Information about activeness score" , border="")
        
    def print_page(self, images):
        # Generates the report
        self.page_body(images)


if __name__ == "__main__":

    analyser = Analyser("food4all","krish7777") 
    score = ActiveNess("food4all","krish7777","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")
    score.Calculate_Score("user_complete_data.json")

    images = ['contrichart.png' , 'language.png' , 'samplechart.png']
    print(analyser.user + '/' + analyser.repo)
    reponame = analyser.user + '/' + analyser.repo
    username = analyser.getMainUser("user_complete_data.json")
    repolink = "https://github.com/" + analyser.user + '/' + analyser.repo 
    mainRepoData = analyser.getMainRepo()
    repo_about = mainRepoData["description"]
    repo_tags = mainRepoData["tagstring"] 
    repo_doc = mainRepoData["created_at"].split('T')[0]
    repo_contricount = str(mainRepoData["total_contributors"])
    repo_lastcommitdate = mainRepoData["updated_at"].split('T')[0]
    repo_openissuecount = str(mainRepoData['open_issues_count'])
    repo_starscount = f"{mainRepoData['watchers_count']}"
    repo_forkscount = f"{mainRepoData['forks_count']}"
    print(repo_openissuecount,repo_starscount )
    repo_activescore = "{0:.2f}".format(score.Calculate_Score())
    repo_languagepercent,repo_languagename = analyser.FileTypeAnalyser()

    #new repo variables added on 08-01-2021

    repo_cmin_commitperday,repo_cmax_commitperday = analyser.CommitsPerDayAvg()
    repo_cmin_oscount,repo_cmax_oscount = analyser.OpenSourceProjectCount()
    repo_cmin_publicrepocount,repo_cmax_publicrepocount = analyser.UserPublicRepoCount()
    repo_cmin_accountage,repo_cmax_accountage = analyser.AccountAge()
    repo_cmin_followers,repo_cmax_followers = analyser.FollowersCount()

    repo_c_commitperday = "{0:.2f}".format( (float(repo_cmin_commitperday) + float(repo_cmax_commitperday)) / 2)


    # language Data will give a tuple of above two list

    user_activescore = "{0:.2f}".format(score.Calculate_Score("user_complete_data.json"))
    user_languagepercent,user_languagename = analyser.FileTypeAnalyser("user_complete_data.json")

    #new user variables added on 08-01-2021 

    user_commitperday = (analyser.CommitsPerDayAvg("user_complete_data.json"))
    user_oscount = (analyser.OpenSourceProjectCount("user_complete_data.json"))
    user_publicrepocount = (analyser.UserPublicRepoCount("user_complete_data.json"))
    user_accountage = (analyser.AccountAge("user_complete_data.json"))
    user_followers = (analyser.FollowersCount("user_complete_data.json"))

    analyser.ContributorsContributionGraph("user_complete_data.json")
    analyser.ContributorsContributionGraph()
    analyser.makeLanguageCharts("user_complete_data.json")
    analyser.detailedGraph("user_complete_data.json")
    analyser.ContributerTypeData()

    pdf = PDF()
    pdf.print_page(images)  
    pdf.output('report/report.pdf', 'F')