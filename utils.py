import csv, math, sqlite3, time, config, os
from typing import List
from selenium import webdriver


def chromeBrowserOptions():
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-extensions")
    options.add_argument('--disable-gpu')
    if config.headless:
        options.add_argument("--headless")
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--incognito")
    return options


def prRed(prt):
    print(f"\033[91m{prt}\033[00m")


def prGreen(prt):
    print(f"\033[92m{prt}\033[00m")


def prYellow(prt):
    print(f"\033[93m{prt}\033[00m")


def getUrlDataFile():
    url_data = ""
    try:
        file = open('data/urlData.txt', 'r')
        url_data = file.readlines()
    except FileNotFoundError:
        text = "FileNotFound:url_data.txt file is not found. Please run ./data folder exists and check config.py values of yours. Then run the bot again"
        prRed(text)
    return url_data


def jobsToPages(num_of_jobs: str) -> int:
    if ' ' in num_of_jobs:
        space_index = num_of_jobs.index(' ')
        total_jobs = (num_of_jobs[0:space_index])
        total_jobs_int = int(total_jobs.replace(',', ''))
        number_of_pages = math.ceil(total_jobs_int / config.jobsPerPage)
        if number_of_pages > 40:
            number_of_pages = 40
    else:
        number_of_pages = int(num_of_jobs)
    return number_of_pages


def urlToKeywords(url: str) -> List[str]:
    keyword_url = url[url.index("keywords=") + 9:]
    keyword = keyword_url[0:keyword_url.index("&")]
    location_url = url[url.index("location=") + 9:]
    location = location_url[0:location_url.index("&")]
    return [keyword, location]


def writeResults(text: str):
    time_str = time.strftime("%Y%m%d")
    file_name = "Applied Jobs DATA - " + time_str + ".csv"
    try:
        with open("data/" + file_name, encoding="utf-8") as file:
            lines = []
            for line in file:
                if "----" not in line and "Date Applied" not in line:
                    lines.append(line)

        with open("data/" + file_name, 'w', encoding="utf-8") as f:
            f.write("---- Applied Jobs Data ---- created at: " + time_str + "\n")
            f.write(
                "Job Title,Company,Location,Work Place,Posted time,Date Applied,Applicants,Result,URL" + "\n")
            for line in lines:
                f.write(line)
            f.write(text + "\n")

    except:
        with open("data/" + file_name, 'w', encoding="utf-8") as f:
            f.write("---- Applied Jobs Data ---- created at: " + time_str + "\n")
            f.write(
                "Job Title,Company,Location,Work Place,Posted Date,Date Applied,Applicants,Result,URL" + "\n")

            f.write(text + "\n")


class LinkedinUrlGenerate:
    def generateUrlLinks(self):
        path = []
        for location in config.location:
            for keyword in config.keywords:
                url = config.linkJobUrl + "?f_AL=true&keywords=" + keyword + self.jobType() + self.remote() + self.checkJobLocation(
                    location) + self.jobExp() + self.datePosted() + self.salary() + self.sortBy()
                path.append(url)
        return path

    @staticmethod
    def checkJobLocation(job):
        job_loc = "&location=" + job.lower()
        match job.casefold():
            case "asia":
                job_loc += "&geoId=102393603"
            case "europe":
                job_loc += "&geoId=100506914"
            case "northamerica":
                job_loc += "&geoId=102221843&"
            case "southamerica":
                job_loc += "&geoId=104514572"
            case "australia":
                job_loc += "&geoId=101452733"
            case "africa":
                job_loc += "&geoId=103537801"

        return job_loc

    @staticmethod
    def jobExp():
        job_exp_array = config.experienceLevels
        first_job_exp = job_exp_array[0]
        job_exp = ""
        match first_job_exp:
            case "Internship":
                job_exp = "&f_E=1"
            case "Entry level":
                job_exp = "&f_E=2"
            case "Associate":
                job_exp = "&f_E=3"
            case "Mid-Senior level":
                job_exp = "&f_E=4"
            case "Director":
                job_exp = "&f_E=5"
            case "Executive":
                job_exp = "&f_E=6"
        for index in range(1, len(job_exp_array)):
            match job_exp_array[index]:
                case "Internship":
                    job_exp += "%2C1"
                case "Entry level":
                    job_exp += "%2C2"
                case "Associate":
                    job_exp += "%2C3"
                case "Mid-Senior level":
                    job_exp += "%2C4"
                case "Director":
                    job_exp += "%2C5"
                case "Executive":
                    job_exp += "%2C6"

        return job_exp

    @staticmethod
    def datePosted():
        date_posted = ""
        match config.datePosted[0]:
            case "Any Time":
                date_posted = ""
            case "Past Month":
                date_posted = "&f_TPR=r2592000&"
            case "Past Week":
                date_posted = "&f_TPR=r604800&"
            case "Past 24 hours":
                date_posted = "&f_TPR=r86400&"
        return date_posted

    @staticmethod
    def jobType():
        job_type_array = config.jobType
        first_job_type = job_type_array[0]
        job_type = ""
        match first_job_type:
            case "Full-time":
                job_type = "&f_JT=F"
            case "Part-time":
                job_type = "&f_JT=P"
            case "Contract":
                job_type = "&f_JT=C"
            case "Temporary":
                job_type = "&f_JT=T"
            case "Volunteer":
                job_type = "&f_JT=V"
            case "Internship":
                job_type = "&f_JT=I"
            case "Other":
                job_type = "&f_JT=O"
        for index in range(1, len(job_type_array)):
            match job_type_array[index]:
                case "Full-time":
                    job_type += "%2CF"
                case "Part-time":
                    job_type += "%2CP"
                case "Contract":
                    job_type += "%2CC"
                case "Temporary":
                    job_type += "%2CT"
                case "Volunteer":
                    job_type += "%2CV"
                case "Internship":
                    job_type += "%2CI"
                case "Other":
                    job_type += "%2CO"
        job_type += "&"
        return job_type

    @staticmethod
    def remote():
        remote_array = config.remote
        first_job_remote = remote_array[0]
        job_remote = ""
        match first_job_remote:
            case "On-site":
                job_remote = "f_WT=1"
            case "Remote":
                job_remote = "f_WT=2"
            case "Hybrid":
                job_remote = "f_WT=3"
        for index in range(1, len(remote_array)):
            match remote_array[index]:
                case "On-site":
                    job_remote += "%2C1"
                case "Remote":
                    job_remote += "%2C2"
                case "Hybrid":
                    job_remote += "%2C3"

        return job_remote

    @staticmethod
    def salary():
        salary = ""
        match config.salary[0]:
            case "$40,000+":
                salary = "f_SB2=1&"
            case "$60,000+":
                salary = "f_SB2=2&"
            case "$80,000+":
                salary = "f_SB2=3&"
            case "$100,000+":
                salary = "f_SB2=4&"
            case "$120,000+":
                salary = "f_SB2=5&"
            case "$140,000+":
                salary = "f_SB2=6&"
            case "$160,000+":
                salary = "f_SB2=7&"
            case "$180,000+":
                salary = "f_SB2=8&"
            case "$200,000+":
                salary = "f_SB2=9&"
        return salary

    @staticmethod
    def sortBy():
        sort_by = ""
        match config.sort[0]:
            case "Recent":
                sort_by = "sort_by=DD"
            case "Relevant":
                sort_by = "sort_by=R"
        return sort_by


def get_db_filename():
    return 'data/' + config.email + '_applied_history.db'


def init_db():
    db_filename = get_db_filename()
    if not os.path.exists(db_filename):
        os.makedirs(os.path.dirname(db_filename), exist_ok=True)
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                     (url TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()


def write_applied_URL(url):
    conn = sqlite3.connect(get_db_filename())
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO history VALUES (?)", (url,))
    conn.commit()
    conn.close()


def check_applied(url):
    conn = sqlite3.connect(get_db_filename())
    c = conn.cursor()
    c.execute("SELECT url FROM history WHERE url = ?", (url,))
    result = c.fetchone()
    conn.close()
    return not (result is not None)


def load_qa_dict():
    try:
        with open('questionAnswer.csv', mode='r') as infile:
            reader = csv.reader(infile)
            qa_dict = {rows[0]: rows[1] for rows in reader}
    except FileNotFoundError:
        qa_dict = {}
        with open('questionAnswer.csv', mode='w') as outfile:
            pass
    return qa_dict


def add_to_qa_dict(question, answer):
    with open('questionAnswer.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([question, answer])
