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

'''
Class to create the final PDF report using PyFPDF python library. Takes all the data analytics and charts generated and generates a pdf report of the same.
NOTE: PDF generated is stored in report directory
'''
class PDF(FPDF, HTMLMixin):
    def __init__(self):
    '''
    Constructor; allows setting up the page format, the orientation and the unit of measurement used in all methods
    '''    
        super().__init__()
        self.WIDTH = 210
        self.HEIGHT = 297
        
    def lines(self):
    '''
    Method to add a border around the page by drawing a rectangle with coordinates specified
    '''    
        self.rect(5.0, 5.0, 200.0,287.0)
        
    def header(self):
    '''
    Method to render the page header. It is automatically called when a new page is added by method add_page()
    '''
        #set font, font formatting and size
        self.set_font('Arial', 'B', 11)
        #add header text, aligned to right
        self.cell(self.WIDTH - 80)
        self.cell(60, 1, 'RepoSummariser', 0, 0, 'R')
        #line break
        self.ln(20)
        
    def footer(self):
    '''
    Method to render the page footer. It is automatically called when a new page is added by method add_page()
    '''
        # Page numbers in the footer
        #set y position where footer is to be added
        self.set_y(-15)
        #set text formatting
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        #add page number in centre of footer
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def page_body(self):
    '''
    Method to render the page body. This is where the entire report is created
    '''
        #page 1 : title page, includes general details about the repository
        self.add_page()
        self.lines()
        
        #page title
        self.set_xy(10.0,17.0)
        self.set_font('Arial', 'B', 18)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=0, h=14.0, align='C', txt="Analysis of repository "+  self.reponame  + " and userID " + self.username, border="")
        
        #Subtitle: repository name
        self.set_xy(10.0,self.get_y() + 2)
        self.set_font('Arial', 'B', 16)
        self.set_text_color(186, 80, 100)
        self.cell(w=0.0, h=10.0, align='L', txt= self.reponame + " details" , border="T", link=self.repolink)
        
        #repository details printed from here

        #About the repository
        self.set_xy(14.0,self.get_y()+10)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.cell(w=18.0, h=9.0, align='L', txt= "About: ", border=0)
        
        self.set_xy(self.get_x(), self.get_y())
        self.set_font('Arial', '', 14)
        self.multi_cell(w=0.0, h=9.0, align='L', txt= self.repo_about, border=0)
        
        #repository tags
        self.set_xy(14, self.get_y())
        self.set_font('Arial', 'B', 14)
        self.cell(w=32.0, h=9.0, align='L', txt= "Project tags: ", border=0)
        
        self.set_xy(self.get_x(), self.get_y())
        self.set_font('Arial', '', 14)
        self.multi_cell(w=0.0, h=9.0, align='L', txt= self.repo_tags, border=0)
        
        #repository stats
        self.set_xy(14.0,self.get_y())
        self.set_font('Arial', 'B', 14)
        self.multi_cell(w=0.0, h=8.0, align='L', txt= "Project stats: ", border=0)
        
        self.set_xy(22.0,self.get_y())
        self.set_font('Arial', '', 13)
        self.multi_cell(w=0.0, h=6.0, align='L', txt= "Project Status: Active (last commit on "+self.repo_lastcommitdate+")\n" +
                        "Date of creation: " + self.repo_doc + "\n" +
                        "Contributors: " + self.repo_contricount + "\n" +
                        "Commits: " + self.repo_contricount + "\n" +
                        "Forks: " + self.repo_forkscount + "\n" +
                        "Stars: " + self.repo_starscount + "\n" +
                        "Open issues: " + self.repo_openissuecount + "\n", border=0)
        
        #repository language split chart
        self.set_xy(14.0,self.get_y()+5)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=0.0, h=9.0, align='L', txt= "Languages: \n", border=0)
        self.image('images/language.png', 18.0, self.get_y() + 2.0, self.WIDTH - 40, 15)
        
        #types of contributors chart
        self.set_xy(14.0,self.get_y() + 25)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=0.0, h=9.0, align='L', txt= "Contributor account types: \n", border=0)
        self.image('images/ContributorType.png', 18.0, self.get_y() + 2.0, self.WIDTH - 40, 15)
        
        #end of page 1
        
        #page 2 : contains activeness score, comparison between contributors and user
        self.add_page()
        self.lines()
        
        #page 2 title
        self.set_xy(10.0,15.0)
        self.set_font('Arial', 'B', 22)
        self.set_text_color(186, 80, 100)
        self.cell(w=0, h=15.0, align='C', txt="Analysis report", border="B")
        
        #page 2 subtitle: Activeness score
        self.set_xy(10.0,45.0)
        self.set_font('Arial', 'B', 20)
        self.cell(w=0.0, h=0.0, align='L', txt= "Activeness score:" , border=0)
        
        self.set_xy(76.0,41.0)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.cell(w=0.0, h=0.0, align='L', txt= self.username + ": " + self.user_activescore, border=0)
        
        self.set_xy(76.0,49.0)
        self.cell(w=0.0, h=0.0, align='L', txt= self.reponame + " contributors (avg): " + self.repo_activescore, border=0)
        
        #page 2 subtitle: Detailed comparison
        self.set_xy(10.0,self.get_y() + 15)
        self.set_font('Arial', 'B', 20)
        self.set_text_color(186, 80, 100)
        self.cell(w=0.0, h=0.0, align='L', txt= "Detailed comparison:" , border=0)
        
        height_y = self.get_y()+12
        #Comparison table plotting begins here

        #Table headings
        self.set_xy(55.0,height_y)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=7.0, align='C', txt= self.reponame + " contributors minimal average", border="R")
        
        self.set_font('Arial', 'B', 12)
        self.set_xy(115.0,height_y)
        self.cell(w=30.0, h=7.0, align='C', txt= self.username, border="")
        
        self.set_font('Arial', 'B', 10)
        self.set_xy(145.0,height_y)
        self.multi_cell(w=55.0, h=7.0, align='C', txt= self.reponame + " contributors maximal average", border="L")
        
        #Comparison parameter 1: commits per day
        height_y = self.get_y()
        
        self.set_xy(5.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=50.0, h=9.0, align='C', txt= "Commits per day", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= self.repo_cmin_commitperday, border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=30.0, h=9.0, align='C', txt= self.user_commitperday, border="")
        
        self.set_xy(145.0,height_y)
        self.multi_cell(w=55.0, h=9.0, align='C', txt= self.repo_cmax_commitperday, border="L")
        
        #Comparison parameter 2: Open source projects contributed to
        height_y = self.get_y()
        
        self.set_xy(5.0,height_y)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=50.0, h=9.0, align='C', txt= "Open source projects count", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= self.repo_cmin_oscount, border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=30.0, h=9.0, align='C', txt= self.user_oscount, border="")
        
        self.set_xy(145.0,height_y)
        self.multi_cell(w=55.0, h=9.0, align='C', txt= self.repo_cmax_oscount, border="L")
        
        #Comparison parameter 3: Public repositories
        height_y = self.get_y()
        
        self.set_xy(5.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=50.0, h=9.0, align='C', txt= "Public repositories", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= self.repo_cmin_publicrepocount, border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=30.0, h=9.0, align='C', txt= self.user_publicrepocount, border="")
        
        self.set_xy(145.0,height_y)
        self.multi_cell(w=55.0, h=9.0, align='C', txt= self.repo_cmax_publicrepocount, border="L")
        
        #Comparison parameter 4: Account age
        height_y = self.get_y()
        
        self.set_xy(5.0,height_y)
        self.set_font('Arial', 'B', 11)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=50.0, h=9.0, align='C', txt= "Account age (yrs)", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= self.repo_cmin_accountage, border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=30.0, h=9.0, align='C', txt= self.user_accountage, border="")
        
        self.set_xy(145.0,height_y)
        self.multi_cell(w=55.0, h=9.0, align='C', txt= self.repo_cmax_accountage, border="L")
        
        #Comparison parameter 5: Followers
        height_y = self.get_y()
        
        self.set_xy(5.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=50.0, h=9.0, align='C', txt= "Followers", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= self.repo_cmin_followers, border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=30.0, h=9.0, align='C', txt= self.user_followers, border="")
        
        self.set_xy(145.0,height_y)
        self.multi_cell(w=55.0, h=9.0, align='C', txt= self.repo_cmax_followers, border="L")
        
        #Plotting a chart comparing these parametera
        
        self.image('images/samplechart.png', 12.0, self.get_y() + 10.0, self.WIDTH - 20)
        
        self.set_xy(10.0,270)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=0.0, h=8.0, align='L', txt= "*Minimal average corresponds to (mean - std dev) while maximal average corresponds to (mean + std dev). 68% of contributors lie within this range", border="")
        
        #page 2 ends here

        #page 3 : language usage split
        self.add_page()
        self.lines()
        #page 3 title: Language usage
        self.set_xy(10.0,15.0)
        self.set_font('Arial', 'B', 20)
        self.set_text_color(186, 80, 100)
        self.cell(w=0, h=15.0, align='L', txt="Language usage", border="B")
        
        #language preference table plots here
        #table title
        height_y = self.get_y() + 20
        self.set_xy(15.0,height_y)
        self.set_font('Arial', 'B', 16)
        self.cell(w=0, h=10.0, align='C', txt="Top 5 preferred languages", border="B")
        height_y = self.get_y() + 15
        
        #column headings
        self.set_xy(10.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=45.0, h=9.0, align='C', txt= "Preference order", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= self.username, border="LR")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=80.0, h=9.0, align='C', txt= self.reponame + " contributors (average)", border="LR")
        
        #First row: language 1
        height_y = self.get_y()
        self.set_xy(10.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=45.0, h=9.0, align='C', txt= "1.", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt=self.user_languagename[0] + " - "+ self.user_languagepercent[0], border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=80.0, h=9.0, align='C', txt= self.repo_languagename[0] + " - "+ self.repo_languagepercent[0], border="LR")
        
        #Second row: language 2
        height_y = self.get_y()
        self.set_xy(10.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=45.0, h=9.0, align='C', txt= "2.", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= self.user_languagename[1] + " - "+ self.user_languagepercent[1], border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=80.0, h=9.0, align='C', txt= self.repo_languagename[1] + " - "+ self.repo_languagepercent[1], border="LR")
        
        #Third row: language 3
        height_y = self.get_y()
        self.set_xy(10.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=45.0, h=9.0, align='C', txt= "3.", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= self.user_languagename[2] + " - "+ self.user_languagepercent[2], border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=80.0, h=9.0, align='C', txt= self.repo_languagename[2] + " - "+ self.repo_languagepercent[2], border="LR")
        
        #Fourth row: language 4
        height_y = self.get_y()
        self.set_xy(10.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=45.0, h=9.0, align='C', txt= "4.", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= self.user_languagename[3] + " - "+ self.user_languagepercent[3], border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=80.0, h=9.0, align='C', txt= self.repo_languagename[3] + " - "+ self.repo_languagepercent[3], border="LR")
        
        #Fifth row: language 5
        height_y = self.get_y()
        self.set_xy(10.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=45.0, h=9.0, align='C', txt= "5.", border="R")
        
        self.set_xy(55.0,height_y)
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=60.0, h=9.0, align='C', txt= self.user_languagename[4] + " - "+ self.user_languagepercent[4], border="R")
            
        self.set_xy(115.0,height_y)
        self.multi_cell(w=80.0, h=9.0, align='C', txt= self.repo_languagename[4] + " - "+ self.repo_languagepercent[4], border="LR")
        #table ends

        #user language chart
        self.set_xy(14.0,self.get_y()+10)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=0.0, h=9.0, align='L', txt=self.username + " languages: \n", border=0)
        self.image('images/UserLanguage.png', 18.0, self.get_y() + 2.0, self.WIDTH - 40, 15)
        
        #contributor language chart
        self.set_xy(14.0,self.get_y() + 25)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=0.0, h=9.0, align='L', txt= self.reponame + " contributors languages\n", border=0)
        self.image('images/RepoLanguage.png', 18.0, self.get_y() + 2.0, self.WIDTH - 40, 15)
        
        self.set_xy(10.0,260)
        self.set_font('Arial', 'I', 10)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=0.0, h=8.0, align='L', txt= "*Others includes all languages excluding C, C++, JAVA, Python, JS, markdown, text, HTML, typescript and css", border="")
        #page 3 ends
        
        #page 4 : Average contribution data
        
        self.add_page()
        self.lines()
        #page 4 title: Past year contributions
        self.set_xy(10.0,15.0)
        self.set_font('Arial', 'B', 20)
        self.set_text_color(186, 80, 100)
        self.cell(w=0, h=15.0, align='L', txt="Past year contributions", border="B")
        
        #user average daily contribution
        height_y = self.get_y() + 20
        self.set_xy(15.0,height_y)
        self.set_font('Arial', 'B', 15)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=0, h=10.0, align='C', txt="Average commits per day ("+self.username+") = " + self.user_commitperday , border="")
        
        self.image('images/usercontrichart.png', 18.0, self.get_y() + 2.0, self.WIDTH - 40)
        
        #repo contributors average daily contribution
        height_y = self.get_y() + 40
        self.set_xy(15.0,height_y)
        self.set_font('Arial', 'B', 15)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=0, h=10.0, align='C', txt="Average commits per day ("+self.reponame+" contributors) = " + self.repo_c_commitperday , border="")
        
        self.image('images/contrichart.png', 18.0, self.get_y() + 2.0, self.WIDTH - 40)
        
        #Information about activeness score
        height_y = self.get_y() + 40
        self.set_xy(15.0,height_y)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(186, 80, 100)
        self.multi_cell(w=0, h=10.0, align='L', txt="Information about activeness score" , border="")
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)
        self.set_xy(15.0,self.get_y())
        self.multi_cell(w=0, h=8.0, align='L', txt="Activeness score is a whole new measure of a user activity across thier github history. It rates users on a scale from 0-5, and takes into account a variety of things. These include the user's profile history like account age, followers, open-source projects etc. It also looks at all projects the user has contributed to as well as thier contributions in each project, including commits, activity timeline etc. These contributions and the activeness of given project are used for activeness score. The main advantage of activeness score is that the formula is dynamic, and takes into account the wider data distribution to give the user a good understanding on his activity" , border="")
        #page 4 ends


    def print_page(self):
    '''
    method to print the pages of report
    '''
        self.page_body()

    def driver(self,Reponame,Username,token):
    '''
    driver function to get data to generate report
    '''
        analyser = Analyser(Reponame,Username) 
        score = ActiveNess(Reponame,Username,token)

        self.reponame = analyser.user + '/' + analyser.repo
        self.username = analyser.getMainUser("user_complete_data.json")
        self.repolink = "https://github.com/" + analyser.user + '/' + analyser.repo 
        mainRepoData = analyser.getMainRepo()
        self.repo_about = mainRepoData["description"]
        self.repo_tags = mainRepoData["tagstring"] 
        self.repo_doc = mainRepoData["created_at"].split('T')[0]
        self.repo_contricount = str(mainRepoData["total_contributors"])
        self.repo_lastcommitdate = mainRepoData["updated_at"].split('T')[0]
        self.repo_openissuecount = str(mainRepoData['open_issues_count'])
        self.repo_starscount = f"{mainRepoData['watchers_count']}"
        self.repo_forkscount = f"{mainRepoData['forks_count']}"
        self.repo_activescore = "{0:.2f}".format(score.Calculate_Score())
        self.repo_languagepercent,self.repo_languagename = analyser.FileTypeAnalyser()

        #new repo variables added on 08-01-2021

        self.repo_cmin_commitperday,self.repo_cmax_commitperday = analyser.CommitsPerDayAvg()
        self.repo_cmin_oscount,self.repo_cmax_oscount = analyser.OpenSourceProjectCount()
        self.repo_cmin_publicrepocount,self.repo_cmax_publicrepocount = analyser.UserPublicRepoCount()
        self.repo_cmin_accountage,self.repo_cmax_accountage = analyser.AccountAge()
        self.repo_cmin_followers,self.repo_cmax_followers = analyser.FollowersCount()

        self.repo_c_commitperday = "{0:.2f}".format( (float(self.repo_cmin_commitperday) + float(self.repo_cmax_commitperday)) / 2)


        # language Data will give a tuple of above two list

        self.user_activescore = "{0:.2f}".format(score.Calculate_Score("user_complete_data.json"))
        self.user_languagepercent,self.user_languagename = analyser.FileTypeAnalyser("user_complete_data.json")

        #new user variables added on 08-01-2021 

        self.user_commitperday = (analyser.CommitsPerDayAvg("user_complete_data.json"))
        self.user_oscount = (analyser.OpenSourceProjectCount("user_complete_data.json"))
        self.user_publicrepocount = (analyser.UserPublicRepoCount("user_complete_data.json"))
        self.user_accountage = (analyser.AccountAge("user_complete_data.json"))
        self.user_followers = (analyser.FollowersCount("user_complete_data.json"))

        analyser.ContributorsContributionGraph("user_complete_data.json")
        analyser.ContributorsContributionGraph()
        analyser.makeLanguageCharts("user_complete_data.json")
        analyser.detailedGraph("user_complete_data.json")
        analyser.ContributerTypeData()

        self.print_page()  
        self.output(f'report/{Reponame}_report.pdf', 'F')


if __name__ == "__main__":
    pdf = PDF()
    pdf.driver("food4all","krish7777","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")