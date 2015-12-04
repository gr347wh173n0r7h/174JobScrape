import cgi
import webapp2
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from urllib import *
from bs4 import BeautifulSoup
from models import Job
import Walkscore
import os.path
import webbrowser

class MainHandler(webapp2.RequestHandler):
  def get(self):
    job = cgi.escape(self.request.get("job"))
    location = cgi.escape(self.request.get("location"))

    # TEST DATA
    job = "Software Engineer"
    location = "San Jose, CA"

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

      indeed_list = []
      print titles

      for t, c ,l, d in zip(titles, companies, loc, desc):
        print t
        if t:
          i_job = Job()
          i_job.title = t.get_text().strip()
          i_job.company = c.get_text().strip()
          i_job.location = l.get_text().strip()
          i_job.description = d.get_text().encode("utf8").strip()
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

    self.response.out.write(template.render('views/index.html', {'d_jobs': dice_list, 'i_jobs': indeed_list}))

    def getWalkScore(location):
    geocodeAddr = location.replace(" ", "+")
    geocodeAPIKey = 'AIzaSyCWjiF1IVs-eYNkWjU5PEFesKYAC0HSQJo'
    geocodeUrl = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s' % (geocodeAddr, geocodeAPIKey)
    print(geocodeUrl)

    response = urllib.request.urlopen(geocodeUrl) #gets http response object
    string = response.read().decode('utf-8') #converts http response object from 'bytes' to string
    json_obj = json.loads(string)
    geocodeCoord = json_obj['results'][0]['geometry']['location']
    geocodeLat = geocodeCoord['lat']
    geocodeLon = geocodeCoord['lng']
    print("Lat: %s Lon: %s" % (geocodeLat, geocodeLon))

    walkScoreAddress = location.replace(" ", "%20")
    walkScoreAddress = walkScoreAddress.replace(",", "")
    walkScoreAPIKey = 'e4b2cbd6c86ddbee53852c89a62f1184'
    walkScoreUrl = 'http://api.walkscore.com/score?format=json&address=%s&lat=%s&lon=%s&wsapikey=%s' % (walkScoreAddress, geocodeLat, geocodeLon, walkScoreAPIKey)
    response = urllib.request.urlopen(walkScoreUrl)
    string = response.read().decode('utf-8')
    json_obj = json.loads(string)
    walkScore = json_obj['walkscore']
    print("Walk Score: %s" % walkScore)
    # print(json.dumps(json_obj, indent=4, sort_keys=True))
    print(walkScoreUrl)
    return walkScore


app = webapp2.WSGIApplication([
                            ('/', MainHandler),
  ], debug=True)