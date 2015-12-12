import cgi
import webapp2
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from urllib2 import *
from bs4 import BeautifulSoup
from models import Job
import Walkscore
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

            indeed_list = []
            print titles

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
                    indeed_list.append(i_job)

            # print "---------INDEED--------"
            # for i in indeed_list:
            #   print "Title: " , i.title
            #   print "Company: " , i.company
            #   print "Description: " , i.description
            #   print "Location: ", i.location
            #   print "\n"

            # DICE -------------------------------------------------------------------

            dice_jobs = dice_soup.findAll('div', {'class': 'serp-result-content'})

            dice_list = []
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
                    dice_list.append(d_job)

                    # print "------ DICE -------"
                    # for d in dice_list:
                    #   print "Title: " , d.title
                    #   print "Company: " , d.company
                    #   print "Description: " , d.description
                    #   print "Location: ", d.location
                    #   print "\n"

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
    print("Lat: %s Lon: %s" % (geocodeLat, geocodeLon))

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
    # print(json.dumps(json_obj, indent=4, sort_keys=Truhttp://api.walkscore.com/score?format=json&address=Santa%20Clara%20Valley%20CA&lat=37.2488478&lon=-121.8399593&wsapikey=e4b2cbd6c86ddbee53852c89a62f1184e))
    print(walkScoreUrl)
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
    # company = company.strip()
    glassPID = "49973"
    glassKey = "g2TIGvm8cb9"
    glassURL = "http://api.glassdoor.com/api/api.htm?v=1&format=json&t.p=%s&t.k=%s&action=employers&q=%s" % (
    glassPID, glassKey, company)
    print glassURL
    # had to do the next line just to get it to work

    request = urllib2.Request(glassURL, headers={'User-Agent': 'Mozilla/5.0'})  # The assembled request
    response = urllib2.urlopen(request)
    string = response.read().decode('utf-8')  # converts http response object from 'bytes' to string
    json_obj = json.loads(string)

    company_dict = json_obj["response"]["employers"]
    if company_dict:
        glassDoorDictList = []
        glassDoorDict = {}
        glassDoorDict["overallRating"] = company_dict[0]["overallRating"]
        glassDoorDict["squareLogo"] = company_dict[0]["squareLogo"]
        glassDoorDict["website"] = company_dict[0]["website"]
        glassDoorDict["culture"] = company_dict[0]["cultureAndValuesRating"]
        glassDoorDict["seniorLeadership"] = company_dict[0]["seniorLeadershipRating"]
        glassDoorDict["compensation"] = company_dict[0]["compensationAndBenefitsRating"]
        glassDoorDict["careerOpportunities"] = company_dict[0]["careerOpportunitiesRating"]
        glassDoorDict["sectorName"] = company_dict[0]["sectorName"]
        glassDoorDict["featuredPro"] = company_dict[0]["featuredReview"]["pros"]
        glassDoorDict["featuredJobTitle"] = company_dict[0]["featuredReview"]["jobTitle"]
        glassDoorDict["featuredCons"] = company_dict[0]["featuredReview"]["cons"]
        glassDoorDict["featuredRating"] = company_dict[0]["featuredReview"]["overall"]
        glassDoorDict["ceoName"] = company_dict[0]["ceo"]["name"]
        glassDoorDict["ceoNumRatings"] = company_dict[0]["ceo"]["numberOfRatings"]
        glassDoorDict["ceoApprovalRating"] = company_dict[0]["ceo"]["pctApprove"]
        glassDoorDict["ceoPicture"] = company_dict[0]["ceo"]["image"]["src"]

        glassDoorDictList.append(glassDoorDict)
        return glassDoorDictList
    return None


def clear_database():
    all_objects = Job.query().fetch()
    for a in all_objects:
        a.key.delete()


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/job/(.+)', JobViewHandler),
], debug=True)
