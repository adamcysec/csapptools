import requests
from datetime import datetime, timedelta
import time

class librariesiolib:
    def __init__(self, api_key):
        self.api_key = api_key

    def new_pypi_packages_past_hours(self, hours=1):
        """Returns pypi packages last updated from n number of hours

        Parameters:
        -----------
        hours : int
            number of hours of packages last updated; default 1

        Returns:
        --------
        target_packages : list
            libraries.io api response
        """

        target_packages = []

        hour_offset = timedelta(hours=hours)
        now = datetime.utcnow()
        last_hour = now - hour_offset

        continue_paging = True
        page_num = 1

        while continue_paging:
            packages_json = self.get_new_pypi_packages(page=page_num)
            
            for package in packages_json:
                latest_release_published_at = package['latest_release_published_at'] # string date # ex. '2023-02-27T22:36:00.813Z'
                package_release_date = datetime.strptime(latest_release_published_at.split(".")[0], "%Y-%m-%dT%H:%M:%S")

                # filter on packages release in the last hour to now
                if package_release_date >= last_hour and package_release_date <= now:
                    target_packages.append(package)
                else:
                    continue_paging = False
                    break # quit loop
            
            page_num +=1 # max page_num is 100

        return target_packages

    def get_new_pypi_packages(self, page=1):
        """Returns the past 100 new packages per page

        The api fails after page 99. Not recommend api to use. 
        
        Parameters:
        ----------- 
        page : int
            api pagination number 

        Returns:
        --------
        packages_json : dict
            libraries.io api response
        """
        
        url = f"https://libraries.io/api/search?order=desc&platforms=PyPI&sort=created_at&per_page=100&page={page}&api_key={self.api_key}"

        response = requests.get(url)
        packages_json = response.json()

        return packages_json

    def get_popular_pypi_packages(self):
        """Returns the past 100 most popular packages per page

        The api fails after page 99.

        Returns:
        --------
        packages_json : dict
            libraries.io api response
        """
        
        url = f"https://libraries.io/api/search?order=desc&platforms=PyPI&sort=rank&per_page=100&page=1&api_key={self.api_key}"

        response = requests.get(url)
        packages_json = response.json()

        return packages_json

    def get_pypi_package(self, package_name):
        """Returns package data for a given package name

        Note. There is a 60 per minute rate limit.

        Parameters:
        -----------
        package_name : str
            pypi package name

        Returns:
        --------
        packages_json : dict
            libraries.io api response
        failure : bool
            returns True for an api error response
        """

        url = f"https://libraries.io/api/pypi/{package_name}?api_key={self.api_key}"
        
        retry = True
        while retry:
            try:
                response = requests.get(url)
                retry = False
            except requests.exceptions.ConnectTimeout:
                print("libraries.io connection failure.. sleeping one hour..")
                time.sleep(3600)

        
        failure = False
        if response.status_code == 429 or response.status_code == 404:
            print(f"failed to get {package_name}; reason: {response.reason}")
            
            if response.status_code == 404:
                failure = False
            else:
                failure = True

            package_json = None
        
        else:
            try:
                package_json = response.json()
            except requests.exceptions.JSONDecodeError:
               failure = 'json'
               package_json = None
            
        return package_json, failure
