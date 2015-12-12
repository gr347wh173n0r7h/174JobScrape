import cgi
import webapp2
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from urllib2 import *
from bs4 import BeautifulSoup
from models import Job
import os.path
import webbrowser
from yelp_api import *
import logging

# CS174 Final Project
# Job Scraper
# Team #2 - Sajay Shah, Jordan Petersen, Jordan Melberg, Arjun Nayak
# Donovon Bacon, Jeffery Tran
# Parses Indeed and Dice to find a job
# Uses Yelp, Walkscore, and Glassdoor to gather more information on the location where the job is located and the job itself

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(template.render('views/index.html', {}))

    def post(self):
        # Clear database of previous results
        clear_database()

        job = cgi.escape(self.request.get("job"))
        location = cgi.escape(self.request.get("location"))

        #example query, defaults to searching for a Software Engineer in San Jose
        if len(location) < 1:
            location = "San Jose, CA"
        if len(job) < 1:
            job = "Software Engineer"

        #variables using user's query that are used to search indeed & dice

        indeed_job = job.replace(" ", "+")
        indeed_loc = location.replace(" ", "+")
        indeed_loc = indeed_loc.replace(",", "%2C")

        dice_job = job.replace(" ", "+")
        dice_loc = location.replace(" ", "+")
        dice_loc = dice_loc.replace(",", "%2C")

        #base indeed & dice url where user inputs are added
        indeed_url = "http://www.indeed.com/jobs?q=%s&l=%s" % (indeed_job, indeed_loc)
        dice_url = "https://www.dice.com/jobs?q=%s&l=%s" % (dice_job, dice_loc)

        #initialize beautiful soup object for indeed and dice
        indeed = urlopen(indeed_url)
        indeed_soup = BeautifulSoup(indeed, "html.parser")

        dice = urlopen(dice_url)
        dice_soup = BeautifulSoup(dice, "html.parser")

        # INDEED Parsing
        #check for errors in indeed query
        bad_query = indeed_soup.find_all("div", {"class": "bad_query"})
        invalid_location = indeed_soup.find_all("div", {"class": "invalid_location"})

        #if there are no errors parse info from Indeed
        #Title of job, title of company, location of job, description of job, link for job
        if len(bad_query) == 0 and len(invalid_location) == 0:
            titles = indeed_soup.find_all("a", {"data-tn-element": "jobTitle"})
            companies = indeed_soup.findAll("span", {"class", "company"})
            loc = indeed_soup.find_all("span", {"class": "location"})
            desc = indeed_soup.find_all("span", {"class": "summary"})
            # jobURLS = indeed_soup.find_all("a", {"class": "jobtitle"})
            jobURLS = indeed_soup.find_all("a", {"class": "turnstileLink"})

            #add all job info to i_job
            for t, c, l, d, h in zip(titles, companies, loc, desc, jobURLS):
                print t
                if t:
                    i_job = Job()
                    i_job.title = t.get_text().strip()
                    i_job.company = c.get_text().strip()
                    i_job.location = l.get_text().strip()
                    i_job.description = d.get_text().encode("utf8").strip()
                    i_job.href = h.get("href")
                    i_job.site = "indeed"
                    i_job.put()

            # DICE Parsing
            # parse info into dice_jobs and locations
            dice_jobs = dice_soup.findAll('div', {'class': 'serp-result-content'})

            locations = dice_soup.find_all("li", {"class": "location"})
            # diceJobURLS = dice_soup.find_all("a", {"class": "dice-btn-link"})
            for job, loc in zip(dice_jobs, locations):
                d_job = Job()
                exists = job.find("a", {"class": "dice-btn-link"}).get("title")
                if exists: #if everything exists.. add job info from Dice into d_job
                    d_job = Job()
                    d_job.title = job.find("a", {"class": "dice-btn-link"}).get("title").strip()
                    d_job.company = job.find("li", {"class": "employer"}).get_text().strip()
                    desc = job.find("div", {"class": "shortdesc"}).get_text().encode("utf8")
                    d_job.description = str(desc).strip()
                    d_job.location = loc.get_text()
                    d_job.href = job.find("a", {"class": "dice-btn-link"}).get('href')
                    d_job.site = "dice"
                    # Store to database
                    d_job.put()

        else:
            print("Bad search query. Please check your spelling") #error handling.  If theres a bad query for either indeed or dice print an error

        # Query database for new jobs
        d_jobs = Job.query(Job.site == "dice").fetch()
        i_jobs = Job.query(Job.site == "indeed").fetch()
        self.response.out.write(template.render('views/index.html', {'d_jobs': d_jobs, 'i_jobs': i_jobs}))

#Get walkscore info for the job location
def getWalkScore(location):
    #use google maps API to find lat/long using the job location
    geocodeAddr = location.replace(" ", "+")
    geocodeAPIKey = 'AIzaSyCWjiF1IVs-eYNkWjU5PEFesKYAC0HSQJo'
    geocodeUrl = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s' % (geocodeAddr, geocodeAPIKey)
    response = urllib2.urlopen(geocodeUrl)  # gets http response object
    string = response.read().decode('utf-8')  # converts http response object from 'bytes' to string
    json_obj = json.loads(string)
    geocodeCoord = json_obj['results'][0]['geometry']['location']
    geocodeLat = geocodeCoord['lat'] #latitude of location
    geocodeLon = geocodeCoord['lng'] #longitude of location

    walkScoreAddress = location.replace(" ", "%20")
    walkScoreAddress = walkScoreAddress.replace(",", "")
    #use walk score API + lat/long to get walkscore info for the location of the job
    walkScoreAPIKey = 'e4b2cbd6c86ddbee53852c89a62f1184'
    walkScoreUrl = 'http://api.walkscore.com/score?format=json&address=%s&lat=%s&lon=%s&wsapikey=%s' % (
    walkScoreAddress, geocodeLat, geocodeLon, walkScoreAPIKey)
    response = urllib2.urlopen(walkScoreUrl)
    string = response.read().decode('utf-8')
    json_obj = json.loads(string)
    walkScoreInfo = []
    walkScoreDict = {}
    if json_obj:
        walkScoreDict["walkScore"] = json_obj['walkscore']
        walkScoreDict["link"] = json_obj['ws_link']
        walkScoreDict["logoURL"] = json_obj['logo_url']
        walkScoreDict["desc"] = json_obj['description']
    walkScoreInfo.append(walkScoreDict)
    #return the walkscore info
    return walkScoreInfo

#Full job info using indeed/dice + yelp/glassdoor/walkscore
class JobViewHandler(webapp2.RequestHandler):
    def get(self, job_id):
        job = ndb.Key(urlsafe=job_id).get()
        yelp = get_yelp(job.location) #
        glassdoor = getGlassdoor(job.company)
        walkScore = getWalkScore(job.location)
        self.response.out.write(template.render('views/job.html', {'job': job, 'yelp': yelp, 'glassdoor': glassdoor, 'walkScore': walkScore}))
        #input all info to job.html page

#Get yelp info using location of job found using parsing
def get_yelp(location):
    ''' Querys for top 5 results using YELP api. '''
    response = query_api('local flavor', location) #Yelp API - local flavor https://www.yelp.com/developers/documentation/v2/search_api
    results = []
    for business in response:
        location = {}
        if 'name' in business:
            location['name'] = business['name'] #name of business
        if 'rating' in business:
            location['rating'] = business['rating'] #yelp rating of business
        if 'url' in business:
            location['url'] = business['url'] #url for business
        if 'image_url' in business:
            location['image_url'] = business['image_url'] #business image
        food_type = []
        for a in business['categories']:
            food_type.append(a[0])
        location['categories'] = food_type
        if business['location']['display_address']:
            location_string = ""
            for a in business['location']['display_address']:
                location_string += a + " "
            location['location'] = location_string
        if business['location']['coordinate']:
            coordinates = ""
            for a in business['location']['coordinate']:
                coordinates += str(business['location']['coordinate'][a]) + " "
            location["coordinates"] = coordinates
        results.append(location)
    return results
    #return yelp local flavor results

#Get company info using Glassdoor
def getGlassdoor(company):
    company = company.replace(" ", "%20")
    glassPID = "49973"
    glassKey = "g2TIGvm8cb9"
    glassURL = "http://api.glassdoor.com/api/api.htm?v=1&format=json&t.p=%s&t.k=%s&action=employers&q=%s" % (
    glassPID, glassKey, company)
    # had to do the next line just to get it to work

    request = urllib2.Request(glassURL, headers={'User-Agent': 'Mozilla/5.0'})  # The assembled request

    response = urllib2.urlopen(request)
    logging.info(response)
    string = response.read().decode('utf-8')  # converts http response object from 'bytes' to string
    json_obj = json.loads(string)

    company_dict = json_obj["response"]["employers"]
    #if statements are used to check what info glassdoor has on each company
    if company_dict:
        glassDoorDictList = []
        glassDoorDict = {}
        if "overallRating" in company_dict[0]:
            glassDoorDict["overallRating"] = company_dict[0]["overallRating"] #overall Glassdoor rating
        if "squareLogo" in company_dict[0]:
            glassDoorDict["squareLogo"] = company_dict[0]["squareLogo"] #logo of company
        if "website" in company_dict[0]:
            glassDoorDict["website"] = company_dict[0]["website"] #glassdoor website for company
        if "cultureAndValuesRating" in company_dict[0]:
            glassDoorDict["culture"] = company_dict[0]["cultureAndValuesRating"] #glassdoor culture and values rating of company
        if "seniorLeadershipRating" in company_dict[0]:
            glassDoorDict["seniorLeadership"] = company_dict[0]["seniorLeadershipRating"] #glassdoor senior leadership rating of company
        if "compensationAndBenefitsRating" in company_dict[0]:
            glassDoorDict["compensation"] = company_dict[0]["compensationAndBenefitsRating"] #glassdoor rating for compensation and benefits
        if "careerOpportunitiesRating" in company_dict[0]:
            glassDoorDict["careerOpportunities"] = company_dict[0]["careerOpportunitiesRating"] #glassdoor rating for career opportunities in company
        if "sectorName" in company_dict[0]:
            glassDoorDict["sectorName"] = company_dict[0]["sectorName"]
        if "pros" in company_dict[0]["featuredReview"]:
            glassDoorDict["featuredPro"] = company_dict[0]["featuredReview"]["pros"] #glassdoor featured review for company
        if "jobTitle" in company_dict[0]["featuredReview"]:
            glassDoorDict["featuredJobTitle"] = company_dict[0]["featuredReview"]["jobTitle"]
        if "cons" in company_dict[0]["featuredReview"]:
            glassDoorDict["featuredCons"] = company_dict[0]["featuredReview"]["cons"]
        if "overall" in company_dict[0]["featuredReview"]:
            glassDoorDict["featuredRating"] = company_dict[0]["featuredReview"]["overall"]
        if "ceo" in company_dict[0]: #info on company ceo (if available)
            if "name" in company_dict[0]["ceo"]:
                glassDoorDict["ceoName"] = company_dict[0]["ceo"]["name"]
            if "numberOfRatings" in company_dict[0]["ceo"]:
                glassDoorDict["ceoNumRatings"] = company_dict[0]["ceo"]["numberOfRatings"]
            if "pctApprove" in company_dict[0]["ceo"]:
             glassDoorDict["ceoApprovalRating"] = company_dict[0]["ceo"]["pctApprove"]
            if "image" in company_dict[0]["ceo"].keys():
                glassDoorDict["ceoPicture"] = company_dict[0]["ceo"]["image"]["src"]

        glassDoorDictList.append(glassDoorDict)
        return glassDoorDictList
    return None


def clear_database():
    ''' Clears the temporary database upon new search" '''
    all_objects = Job.query().fetch()
    for a in all_objects:
        a.key.delete()


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/job/(.+)', JobViewHandler),
], debug=True)
