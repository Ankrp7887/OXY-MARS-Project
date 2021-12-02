from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from boltons import iterutils
from lxml import etree
import requests
import time
import re

class Scrappy:
    def __init__(self, url):
        self.url = url

    @staticmethod
    def extract_data(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')
        return soup

    def extract_links(self, links=set()):
        soup = self.extract_data(self.url)
        for link in soup.find_all('h3', class_ = 'card-heading mb-5'):
            links.add(link.a['href'])
        return links

    def find_job_sector(self, sector): # this functions use to identify automatically the job sector accurately
        select = None
        if 'Accounting' in sector:
            select = 'Accounting'
        elif 'Animation' in sector:
            select = 'Animation'
        elif 'Education' in sector:
            select = 'Education'
        elif 'Engineering' in sector:
            select = 'Engineering'
        elif 'Garmnets' in sector:
            select = 'Garmnets'
        elif 'Graphics' in sector:
            select = 'Graphics'
        elif 'Health Care' in sector:
            select = 'Healthcare'
        elif 'Marketing' in sector:
            select = 'Marketing'
        elif 'Mobile' in sector:
            select = 'Mobile'
        elif 'Transportation' in sector:
            select = 'Transportation'
        elif 'Writing' in sector:
            select = 'Writing'
        else: select = 'Support'
        return select


    def copy_data(self, index, job_post_url, username):
        soup = self.extract_data(job_post_url) # get the data in html format
        job_title = soup.find('h1', class_ = 'card-heading text-xlarge').text # job title
        #company_name = soup.find('dd', class_ = "hidden-xs").text.strip() # company name
        location = soup.find('dd', text=re.compile('Japan.*')).text
        indusrty = {
            'Accounting', 'Animation', 'Education', 'Engineering', 'Garmnets', 'Graphics',
            'Health Care', 'Marketing', 'Mobile', 'Support', 'Transportation', 'Writing'
        }
        for sector in indusrty:
            page = soup.find("dd", text=re.compile(sector))
            if page != None:
                break
        job_sector = self.find_job_sector(page.text)
        try:
            job_type = soup.find("dd", text=re.compile("Full Time|Part Time|Freelance|Temporay")).text.split('/')[0].strip()
        except AttributeError:
            job_type = 'Temporary'

        temp = soup.find("dd", text=re.compile('¥\d.*')).text.strip() # placeholder for salary
        try:
            salary = str(re.search(r'\bMonth|Year|Week|Hour\b', temp).group()) + 'ly'
        except AttributeError:
            salary = 'Negotiable'

        try:
            min_salary = temp.split('~')[0].replace(',', ' ').replace(' ', '').replace('¥', '')
            max_salary = temp.split('~')[1].replace(',', ' ').replace(' ', '').replace('¥', '').replace(str(re.search(r'\bMonth|Year|Week|Hour|Negotiable\b', temp.split('~')[1]).group()), '').replace('/', '')
        except:
            min_salary = ''
            max_salary = ''
        key_skills = None
        for i in soup.find_all('div', class_ = 'card-item'):
            for j in i.find_all('ul', class_ = 'list mb-0'):
                for x in j.find_all('li'):
                    key_skills = x.text.strip().replace('  ', '')
        description = soup.find('p', class_ = 'card-item').text.strip()
        job_description = iterutils.chunked(description,120)

        PATH = "C:\chromedriver.exe"
        OPTIONS = webdriver.ChromeOptions()
        OPTIONS.add_argument('--start-maximized')
        OPTIONS.add_argument('--incognito')
        OPTIONS.add_argument('--disable-gpu')
        OPTIONS.add_argument('--disable-geolocation')

        driver = webdriver.Chrome(executable_path = PATH, options = OPTIONS)
        post_jobUrl = 'https://japanplacements.com'
        driver.get(post_jobUrl)
        time.sleep(5)

        #login section
        driver.find_element_by_xpath('//*[@id="careerfy-header"]/div[1]/div/div/div/div/ul/li[2]/a').click()
        driver.find_element_by_name('pt_user_login').send_keys(username)
        driver.find_element_by_name('pt_user_pass').send_keys('!primeHP')
        driver.find_element_by_class_name('jobsearch-login-submit-btn').click()
        time.sleep(5)
        driver.find_element_by_xpath('//*[@id="careerfy-header"]/div[2]/div/div/div/a').click()
        time.sleep(5)

        driver.find_element_by_id('ad-posting-title').send_keys(job_title)
        driver.switch_to.frame("job_detail_ifr")
        driver.find_element_by_id('tinymce').send_keys(job_description)
        driver.switch_to.default_content()
        driver.find_element_by_id('job-sector-selectized').send_keys(job_sector)
        time.sleep(3)
        driver.find_element_by_id('job-sector-selectized').send_keys(Keys.ENTER)

        driver.find_element_by_id('job-type-selectized').send_keys(job_type)
        time.sleep(3)
        driver.find_element_by_id('job-type-selectized').send_keys(Keys.ENTER)

        driver.find_element_by_xpath('//*[@id="job-skills"]/li/input').send_keys(key_skills)
  
        driver.find_element_by_id('jobsearch_job_apply_type-selectized').send_keys('Internal')
        time.sleep(3)
        driver.find_element_by_id('jobsearch_job_apply_type-selectized').send_keys(Keys.ENTER)
    

    # salary
        driver.find_element_by_name('job_salary').send_keys(min_salary)
        driver.find_element_by_name('job_max_salary').send_keys(max_salary)
        driver.find_element_by_xpath('//*[@id="job-posting-form"]/div[2]/ul/li[2]/div/div/div[1]/input').send_keys('Others')
        time.sleep(2)
        driver.find_element_by_xpath('//*[@id="job-posting-form"]/div[2]/ul/li[2]/div/div/div[1]/input').send_keys(Keys.ENTER)
        #experience
        driver.find_element_by_xpath('//*[@id="job-posting-form"]/div[2]/ul/li[3]/div/div/div[1]/input').send_keys('Fresh')
        time.sleep(3)
        driver.find_element_by_xpath('//*[@id="job-posting-form"]/div[2]/ul/li[3]/div/div/div[1]/input').send_keys(Keys.ENTER)

        driver.find_element_by_xpath('//*[@id="job-posting-form"]/div[2]/ul/li[4]/div/div/div[1]/input').send_keys('Any')
        time.sleep(3)
        driver.find_element_by_xpath('//*[@id="job-posting-form"]/div[2]/ul/li[4]/div/div/div[1]/input').send_keys(Keys.ENTER)

        driver.find_element_by_xpath('//*[@id="job-posting-form"]/div[2]/ul/li[5]/div/div/div[1]/input').send_keys('Management')
        time.sleep(3)
        driver.find_element_by_xpath('//*[@id="job-posting-form"]/div[2]/ul/li[5]/div/div/div[1]/input').send_keys(Keys.ENTER)
        #qualifications
        driver.find_element_by_xpath('//*[@id="job-posting-form"]/div[2]/ul/li[6]/div/div/div[1]/input').send_keys("Master’s Degree")
        time.sleep(3)
        driver.find_element_by_xpath('//*[@id="job-posting-form"]/div[2]/ul/li[6]/div/div/div[1]/input').send_keys(Keys.ENTER)
        driver.find_element_by_name('jobsearch_field_location_address').send_keys(location)
        driver.find_element_by_name('terms_cond_check').click()
        driver.find_element_by_css_selector('input[type="submit"]').click()
        #package details
        package = input("choose a package free, after selectiong a package.. enter done : ")
        if package == 'done':
            driver.quit()
        else:
            driver.quit()

    def run(self):
        job_links = self.extract_links()
        username = input('Enter username or email address: ')
        https = 'https://jobs.gaijinpot.com'
        for index, link in enumerate(job_links):
            self.copy_data(index, https+link, username)
          
            

company_url = input('Enter company url : ')
automate_server = Scrappy(company_url)
automate_server.run()
