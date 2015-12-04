import cgi
import webapp2
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from urllib import *
from bs4 import BeautifulSoup
from models import Job

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

app = webapp2.WSGIApplication([
                            ('/', MainHandler),
  ], debug=True)