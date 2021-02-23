from dotenv import load_dotenv
load_dotenv()

from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

from instascrape import *
from selenium import webdriver
PATH = "/Users/ardaerzin/chromedriver"
driver = webdriver.Chrome(PATH)

import math
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from .actions import loginFacebook, loginLinkedIn

linkedin_loggedin = False

PATHS={
    "Linkedin": {
        "URL": "https://www.linkedin.com/in/"
    },
    "Instagram": {
        "URL": "https://www.instagram.com/",
        "session_id":'45874604242%3AP0HAvGM9HQkCXb%3A3'
    },
    "Twitch": {
        "URL": "https://www.twitch.tv/",
        "NAME":"/html/body/div[1]/div/div[2]/div[2]/main/div[2]/div[3]/div/div/div[2]/div[1]/div[2]/div/div[2]/div[1]/div[1]/div[2]/a/div/h1",
        "COUNT":"/html/body/div[1]/div/div[2]/div[2]/main/div[2]/div[3]/div/div/div[2]/div[1]/div[2]/div/div[2]/div[1]/div[1]/div[2]/p"
    },
    "Tiktok": {
        "URL": "https://www.tiktok.com/@",
        "NAME":"/html/body/div/div/div[2]/div[2]/div/header/div[1]/div[2]/h2",
        "COUNT":"/html/body/div[1]/div/div[2]/div[2]/div/header/h2[1]/div[2]/strong"
    },
    "Twitter": {
        "URL": "https://twitter.com/",
        "NAME":"/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[2]/div/div/div[1]/div/div[2]/div[1]/div/div[2]/div/span"
    },
    "Youtube": {
        "URL": "https://www.youtube.com/",
        "NAME": "//*[contains(@id, 'text') and contains(@class,'ytd-channel-name')][1]",
        "COUNT": "//*[@id=\"subscriber-count\"]"
    }
}

class Scraper(object):
    def __init__(
        self,
    ):
        self.driver = driver
        self.linkedin_loggedin = False
        self.facebook_loggedin = False

    def login(self, platform):
        loginFunction = None
        if platform == "FACEBOOK":
            loginFunction = loginFacebook
        elif platform == "LINKEDIN":
            loginFunction = loginLinkedIn
        try:
            loginFunction(self.driver, os.getenv(f"{platform}_LOGIN_EMAIL"), os.getenv(f"{platform}_LOGIN_PASSWORD"))
            return True
        except:
            return False

    def scrape_facebook(self, username):
        if not self.facebook_loggedin:
            self.facebook_loggedin = self.login('FACEBOOK')

        scraped = scrape_regular(username, "Facebook")

    def scrape_linkedin(self, username):
        followers = None
        connections = None
        name = None
        
        if not self.linkedin_loggedin:
            self.linkedin_loggedin = self.login('LINKEDIN')
            
        self.driver.get(f"{username}")

        try:
            followers = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[contains(@class, 'pv-recent-activity-section-v2')]/span",
                    )
                )
            ).text
        except:
            followers = 'N/A'

        root = self.driver.find_element_by_class_name("pv-top-card")
        self.name = root.find_elements_by_xpath("//section/div/div/div/*/li")[
            0
        ].text.strip()

        connections = self.driver.find_element_by_class_name(f"{'pv-top-card'}--list-bullet")
        connections = connections.find_elements_by_tag_name("li")[1].text
        
        return {"name": name, "followers": followers, "connections": connections}
        
    def scrape_instagram(self, username):
        insta_user = Profile(f"{PATHS['Instagram']['URL']}{username}/")
        # insta_user = Profile(f"{username}")
        headers = {"user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.57",
           "cookie": f"sessionid={PATHS['Instagram']['session_id']};"}
        insta_user.scrape(headers=headers)
        x = float(insta_user.followers)
        followers = 'N/A' if math.isnan(x) else insta_user.followers
        time.sleep(3)
        return {"name": username, "followers": followers}

    def scrape_regular(self, username, platform):
        subscribers = None
        name = None

        platform_url = f"{username}"
        self.driver.get(platform_url)
        
        try:
            element1 = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, PATHS[platform]["COUNT"])))
            subscribers = element1.text  
                
        except:
            subscribers = "N/A"
        
        return {"followers": subscribers}

    def scrape_twitter(self, username):
        subscribers = None
        platform_url = f"{PATHS['Twitter']['URL']}{username}"
        
        # get url
        self.driver.get(platform_url)
        try:
            uname = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, PATHS["Twitter"]["NAME"]))).text
            subscribers = self.driver.find_element_by_xpath(f"//a[@href='/{uname.replace('@', '')}/followers']/span[1]/span").text
        except:
            print(f"NOOOOTZ {username} {subscribers}")
            subscribers = self.driver.find_element_by_xpath("//div/div[2]/div[@role='button' and @dir='auto'][1]/span[1]/span").text
        
        return {"followers": subscribers}

    def getInfo(self, username, platform):
        try:
            if platform == 'Instagram' :
                info = self.scrape_instagram(username)
            elif platform == 'Linkedin' :
                info = self.scrape_linkedin(username)
            elif platform == 'Facebook' :
                info = self.scrape_facebook(username)
            elif platform == 'Twitter' :
                info = self.scrape_twitter(username)
            else :
                info = self.scrape_regular(username, platform)
            return info
        except:
            pass
        return {"followers": "N/A", "connections": "N/A"}

    def destroy(self):
        self.driver.quit()