# Step 1

## Decide on the Data we want to explore

1. List of Contributors in our chosen repo

    1. Contributors details to be explored include:
        1. Commits in that repo
            1. Title
            2. Body
            3. Files changed (eg: md files carry less weight than code files)
            4. Line count
            5. Code( Optional, for now not to be used in analysis )

        2. Timeline and count of their contributions in that repo
            a. To calculate the activeness factor of said user for that repo
            
        3.  Find the other Repo where he/she has contributed ( Find the Similar Data as above repo wise)

        4. Find the major tags of each repo the contributor has commited to and use this to rate user preferred field so that we can add in repo stats percent of total users familiar with a language/field. This can help users better decide whether he/she can help in that project

        5. Personal Details of the Contributor, like organisations, education etc that cann help rate the 'level' of a user (student, professional etc). Such info can be provided in repo stats as well

        6. Analyse Pull Request
            1. To be decided( ex. how to analyse it? should we use commits and PR both?) (discuss with mentor)
            2. Calculate the accepted/All ratio for pull requests made by each user
            3. Calculating the number of pull requests said user has reviewed (code reviews have higher contribution in activeness factor compared to commits/pull requests)
            4. Analysing the PR comments made by user (Optional: can be used as a factor in calculating activeness factor)

    2. For each repo a user has contributed to, calculate a repo score that rates how active that repo is (for this we can use exiting tools, like gitstats, gitinspector and gitcompare). This repo score, along with users activeness factor in that repo are used together to calculate a total user score which rates how active/experienced etc a user is. 

    3. An average of said user score for our chosen repo, along with a detailed breakdown of data can help a user better analyse the level of users contributing to a repo, and thus decide whether its beginner friendly/ alignes with thier skills / has higher chance for them to be able to contribute.

## Other details:

1. Deciding on the types of repositories user has contibuted to be considered while calculating user score. Current rules (to be finalised after discussion with mentor):
    1. any repo with open source license
    2. any repo with open source mentioned in project description
    3. any repo with more than 10 contributors
            
