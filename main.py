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


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(template.render('views/index.html', {}))

    def post(self):
        # Clear database of previous results
        clear_database()

        job = cgi.escape(self.request.get("job"))
        location = cgi.escape(self.request.get("location"))
        
        if len(location) < 1:
            location = "San Jose, CA"
        if len(job) < 1:
            job = "Software Engineer"

        indeed_job = job.replace(" ", "+")
        indeed_loc = location.replace(" ", "+")
        indeed_loc = indeed_loc.replace(",", "%2C")

        dice_job = job.replace(" ", "+")
        dice_loc = location.replace(" ", "+")
        dice_loc = dice_loc.replace(",", "%2C")

        indeed_url = "http://www.indeed.com/jobs?q=%s&l=%s" % (indeed_job, indeed_loc)
        dice_url = "https://www.dice.com/jobs?q=%s&l=%s" % (dice_job, dice_loc)

        indeed = urlopen(indeed_url)
        indeed_soup = BeautifulSoup(indeed, "html.parser")

        dice = urlopen(dice_url)
        dice_soup = BeautifulSoup(dice, "html.parser")

        # INDEED -----------------------------------------------------------------
        bad_query = indeed_soup.find_all("div", {"class": "bad_query"})
        invalid_location = indeed_soup.find_all("div", {"class": "invalid_location"})

        if len(bad_query) == 0 and len(invalid_location) == 0:
            titles = indeed_soup.find_all("a", {"data-tn-element": "jobTitle"})
            companies = indeed_soup.findAll("span", {"class", "company"})
            loc = indeed_soup.find_all("span", {"class": "location"})
            desc = indeed_soup.find_all("span", {"class": "summary"})
            # jobURLS = indeed_soup.find_all("a", {"class": "jobtitle"})
            jobURLS = indeed_soup.find_all("a", {"class": "turnstileLink"})

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

            # DICE -------------------------------------------------------------------

            dice_jobs = dice_soup.findAll('div', {'class': 'serp-result-content'})

            locations = dice_soup.find_all("li", {"class": "location"})
            # diceJobURLS = dice_soup.find_all("a", {"class": "dice-btn-link"})
            for job, loc in zip(dice_jobs, locations):
                d_job = Job()
                exists = job.find("a", {"class": "dice-btn-link"}).get("title")
                if exists:
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
            print("Bad search query. Please check your spelling")

        # Query database for new jobs
        d_jobs = Job.query(Job.site == "dice").fetch()
        i_jobs = Job.query(Job.site == "indeed").fetch()
        self.response.out.write(template.render('views/index.html', {'d_jobs': d_jobs, 'i_jobs': i_jobs}))


def getWalkScore(location):
    geocodeAddr = location.replace(" ", "+")
    geocodeAPIKey = 'AIzaSyCWjiF1IVs-eYNkWjU5PEFesKYAC0HSQJo'
    geocodeUrl = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s' % (geocodeAddr, geocodeAPIKey)
    response = urllib2.urlopen(geocodeUrl)  # gets http response object
    string = response.read().decode('utf-8')  # converts http response object from 'bytes' to string
    json_obj = json.loads(string)
    geocodeCoord = json_obj['results'][0]['geometry']['location']
    geocodeLat = geocodeCoord['lat']
    geocodeLon = geocodeCoord['lng']

    walkScoreAddress = location.replace(" ", "%20")
    walkScoreAddress = walkScoreAddress.replace(",", "")
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
    return walkScoreInfo


class JobViewHandler(webapp2.RequestHandler):
    def get(self, job_id):
        job = ndb.Key(urlsafe=job_id).get()
        yelp = get_yelp(job.location)
        glassdoor = getGlassdoor(job.company)
        walkScore = getWalkScore(job.location)
        self.response.out.write(template.render('views/job.html', {'job': job, 'yelp': yelp, 'glassdoor': glassdoor, 'walkScore': walkScore}))


def get_yelp(location):
    ''' Querys for top 5 results using YELP api. ''' 
    response = query_api('local flavor', location)
    results = []
    for business in response:
        location = {}
        if 'name' in business:
            location['name'] = business['name']
        if 'rating' in business:
            location['rating'] = business['rating']
        if 'url' in business:
            location['url'] = business['url']
        if 'image_url' in business:
            location['image_url'] = business['image_url']
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


def getGlassdoor(company):
    company = company.replace(" ", "%20")
    glassPID = "49973"
    glassKey = "g2TIGvm8cb9"
    glassURL = "http://api.glassdoor.com/api/api.htm?v=1&format=json&t.p=%s&t.k=%s&action=employers&q=%s" % (
    glassPID, glassKey, company)
    # had to do the next line just to get it to work

    request = urllib2.Request(glassURL, headers={'User-Agent': 'Mozilla/5.0'})  # The assembled request
    response = urllib2.urlopen(request)
    string = response.read().decode('utf-8')  # converts http response object from 'bytes' to string
    json_obj = json.loads(string)

    company_dict = json_obj["response"]["employers"]
    if company_dict:
        glassDoorDictList = []
        glassDoorDict = {}
        if "overallRating" in company_dict[0]:
            glassDoorDict["overallRating"] = company_dict[0]["overallRating"]
        if "squareLogo" in company_dict[0]:
            glassDoorDict["squareLogo"] = company_dict[0]["squareLogo"]
        if "website" in company_dict[0]:
            glassDoorDict["website"] = company_dict[0]["website"]
        if "cultureAndValuesRating" in company_dict[0]:
            glassDoorDict["culture"] = company_dict[0]["cultureAndValuesRating"]
        if "seniorLeadershipRating" in company_dict[0]:
            glassDoorDict["seniorLeadership"] = company_dict[0]["seniorLeadershipRating"]
        if "compensationAndBenefitsRating" in company_dict[0]:
            glassDoorDict["compensation"] = company_dict[0]["compensationAndBenefitsRating"]
        if "careerOpportunitiesRating" in company_dict[0]:
            glassDoorDict["careerOpportunities"] = company_dict[0]["careerOpportunitiesRating"]
        if "sectorName" in company_dict[0]:
            glassDoorDict["sectorName"] = company_dict[0]["sectorName"]
        if "pros" in company_dict[0]["featuredReview"]:
            glassDoorDict["featuredPro"] = company_dict[0]["featuredReview"]["pros"]
        if "jobTitle" in company_dict[0]["featuredReview"]:
            glassDoorDict["featuredJobTitle"] = company_dict[0]["featuredReview"]["jobTitle"]
        if "cons" in company_dict[0]["featuredReview"]:
            glassDoorDict["featuredCons"] = company_dict[0]["featuredReview"]["cons"]
        if "overall" in company_dict[0]["featuredReview"]:
            glassDoorDict["featuredRating"] = company_dict[0]["featuredReview"]["overall"]
        if "ceo" in company_dict[0]:
            if "name" in company_dict[0]["ceo"]:
                glassDoorDict["ceoName"] = company_dict[0]["ceo"]["name"]
            if "numberOfRatings" in company_dict[0]["ceo"]:
                glassDoorDict["ceoNumRatings"] = company_dict[0]["ceo"]["numberOfRatings"]
            if "pctApprove" in company_dict[0]["ceo"]:
             glassDoorDict["ceoApprovalRating"] = company_dict[0]["ceo"]["pctApprove"]
            if "src" in company_dict[0]["ceo"]["image"]:
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
