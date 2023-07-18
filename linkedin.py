import math, os, random, time, re, config, utils, atexit

from datetime import datetime, date
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from utils import prRed, prYellow, prGreen


class Linkedin:
    count_applied = 0
    count_jobs = 0
    qa_dict = {}

    def __init__(self):
        prYellow("🌐 Bot will run in Chrome browser and log in Linkedin for you.")
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=utils.chromeBrowserOptions())
        self.driver.get('https://www.linkedin.com/login')

        prYellow("🔄 Trying to log in linkedin...")
        try:
            self.driver.find_element(By.ID, "username").send_keys(config.email)
            time.sleep(2)
            self.driver.find_element(By.ID, "password").send_keys(config.password)
            time.sleep(2)
            self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Sign in']").click()
            time.sleep(5)

            if self.driver.title == "Security Verification | LinkedIn":
                user_input = input(prYellow("Please enter verification code sent to your email: "))
                self.driver.find_element(By.ID, "input__email_verification_pin").send_keys(user_input)
                time.sleep(2)
                self.driver.find_element(By.ID, "email-pin-submit-button").click()
                time.sleep(5)
        except:
            prRed("❌ Couldn't log in Linkedin by using Chrome. Please check your Linkedin credentials on config files line 7 and 8.")

        self.qa_dict = utils.load_qa_dict()
        utils.init_db()
        atexit.register(self.cleanup)

    def cleanup(self):
        prYellow("applied succeed: " + str(self.count_applied) + " jobs out of " + str(self.count_jobs) + ".")

    @staticmethod
    def generateUrls():
        if not os.path.exists('data'):
            os.makedirs('data')
        try:
            with open('data/urlData.txt', 'w', encoding="utf-8") as file:
                linkedin_job_links = utils.LinkedinUrlGenerate().generateUrlLinks()
                for url in linkedin_job_links:
                    file.write(url + "\n")
            prGreen("✅ Urls are created successfully, now the bot will visit those urls.")
        except:
            prRed("❌ Couldn't generate url, make sure you have /data folder and modified config.py file for your preferences.")

    def linkJobApply(self):
        self.generateUrls()

        url_data = utils.getUrlDataFile()

        for url in url_data:
            self.driver.get(url)

            total_jobs = self.driver.find_element(By.XPATH, '//small').text
            total_pages = utils.jobsToPages(total_jobs)

            url_words = utils.urlToKeywords(url)
            print("\n Category: " + url_words[0] + ", Location: " + url_words[1] + ", Applying " + str(
                total_jobs) + " jobs.")

            for page in range(total_pages):
                current_page_jobs = config.jobsPerPage * page
                url = url + "&start=" + str(current_page_jobs)
                self.driver.get(url)
                time.sleep(random.uniform(1, config.botSpeed))

                offers_per_page = self.driver.find_elements(By.XPATH, '//li[@data-occludable-job-id]')
                offer_ids = []

                time.sleep(random.uniform(1, config.botSpeed))

                for offer in offers_per_page:
                    offer_id = offer.get_attribute("data-occludable-job-id")
                    offer_ids.append(int(offer_id.split(":")[-1]))

                for jobID in offer_ids:
                    offer_page = 'https://www.linkedin.com/jobs/view/' + str(jobID)

                    if utils.check_applied(offer_page):
                        for _ in range(3):
                            try:
                                self.driver.get(offer_page)
                                break
                            except:
                                pass
                        else:
                            raise Exception(f"Failed to load page {offer_page} after 3 attempts")
                        time.sleep(random.uniform(1, config.botSpeed))

                        self.count_jobs += 1

                        job_properties = self.getJobProperties()
                        if "blacklisted" in job_properties:
                            line_to_write = job_properties + "," + "* 🤬 Blacklisted Job skipped," + str(offer_page)
                            utils.write_applied_URL(offer_page)
                            self.displayWriteResults(line_to_write)

                        else:
                            button = self.easyApplyButton()

                            if button is not False:
                                button.click()
                                time.sleep(random.uniform(1, config.botSpeed))
                                try:
                                    self.chooseResume()
                                    self.driver.find_element(By.CSS_SELECTOR,
                                                             "button[aria-label='Submit application']").click()
                                    time.sleep(random.uniform(1, config.botSpeed))

                                    line_to_write = job_properties + "," + "* 🥳 Apply Success," + str(offer_page)
                                    self.count_applied += 1
                                    utils.write_applied_URL(offer_page)
                                    self.displayWriteResults(line_to_write)

                                except:
                                    try:
                                        self.handelQuestions()
                                        self.driver.find_element(By.CSS_SELECTOR,
                                                                 "button[aria-label='Continue to next step']").click()
                                        time.sleep(random.uniform(1, config.botSpeed))

                                        com_percentage = self.driver.find_element(By.XPATH, 'html/body/div[3]/div/div/div[2]/div/div/span').text
                                        percen_number = int(com_percentage[0:com_percentage.index("%")])

                                        result = self.applyProcess(percen_number, offer_page)
                                        line_to_write = job_properties + "," + result
                                        self.displayWriteResults(line_to_write)

                                    except:
                                        line_to_write = job_properties + "," + "* 🥵 Apply Fail," + str(
                                            offer_page)
                                        self.displayWriteResults(line_to_write)
                            else:
                                line_to_write = job_properties + "," + "* 🥱 Applied Pass," + str(offer_page)
                                utils.write_applied_URL(offer_page)
                                self.displayWriteResults(line_to_write)

    @staticmethod
    def displayWriteResults(line_to_write: str):
        try:
            print(line_to_write)
            utils.writeResults(line_to_write)
        except Exception as e:
            prRed("❌ Error in DisplayWriteResults: " + str(e))

    def getJobProperties(self):
        try:
            job_title = self.driver.find_element(By.XPATH, "//h1[contains(@class, 'job-title')]").get_attribute("innerHTML").strip().replace(",", "")
            res = [blItem for blItem in config.blackListTitles if (blItem.lower() in job_title.lower())]
            if len(res) > 0:
                job_title += "(blacklisted title: " + ' '.join(res) + ")"
        except Exception as e:
            if config.displayWarnings:
                prYellow("⚠️ Warning in getting job_title: " + str(e)[0:50])
            job_title = ""

        try:
            job_company = self.driver.find_element(By.XPATH, "//a[contains(@class, 'ember-view t-black t-normal')]").get_attribute("innerHTML").strip().replace(",", "")
            res = [blItem for blItem in config.blacklistCompanies if (blItem.lower() in job_company.lower())]
            if len(res) > 0:
                job_company += "(blacklisted company: " + ' '.join(res) + ")"
        except:
            try:
                job_info_div = self.driver.find_element(By.XPATH, "//div[@class='jobs-unified-top-card__primary-description']")
                job_company = job_info_div.find_element(By.XPATH, ".//a[@data-test-app-aware-link]").text.strip().replace(",", "")
                res = [blItem for blItem in config.blacklistCompanies if (blItem.lower() in job_company.lower())]
                if len(res) > 0:
                    job_company += "(blacklisted company: " + ' '.join(res) + ")"
            except Exception as e:
                if config.displayWarnings:
                    prYellow("⚠️ Warning in getting job_company" + str(e)[0:50])
                job_company = ""

        try:
            job_location = self.driver.find_element(By.XPATH, "//span[contains(@class, 'bullet')]").get_attribute("innerHTML").strip().replace(",", "")
        except:
            try:
                block_text = self.driver.find_element(By.XPATH, '//*[@class="jobs-unified-top-card__primary-description"]').text
                location_info = block_text.split("· ")[1]
                job_location = location_info.split(" (")[0].split(" Reposted")[0].replace(",", "")
            except Exception as e:
                if config.displayWarnings:
                    prYellow("⚠️ Warning in getting job_location: " + str(e)[0:50])
                job_location = ""

        try:
            job_work_place = self.driver.find_element(By.XPATH, "//span[contains(@class, 'workplace-type')]").get_attribute("innerHTML").strip().replace(",", "")
        except:
            try:
                block_text = self.driver.find_element(By.XPATH, '//*[@class="jobs-unified-top-card__primary-description"]').text
                location_info = block_text.split("· ")[1]
                work_type_info = location_info.split(" (")[1]
                job_work_place = work_type_info.split(")")[0]
            except Exception as e:
                if config.displayWarnings:
                    prYellow("⚠️ Warning in getting jobWorkPlace: " + str(e)[0:50])
                job_work_place = ""

        try:
            job_posted_date = self.driver.find_element(By.XPATH, "//span[contains(@class, 'posted-date')]").get_attribute("innerHTML").strip()
        except:
            try:
                block_text = self.driver.find_element(By.XPATH, '//div[@class="jobs-unified-top-card__primary-description"]').text
                match = re.search(r'\d+ (\w+ ago)', block_text)
                if match:
                    job_posted_date = match.group(0)
                else:
                    raise ValueError('No job posted date found')
            except Exception as e:
                if config.displayWarnings:
                    prYellow("⚠️ Warning in getting job_posted_date: " + str(e)[0:50])
                job_posted_date = ""

        try:
            job_applications = self.driver.find_element(By.XPATH, "//span[contains(@class, 'applicant-count')]").get_attribute("innerHTML").strip()
        except:
            try:
                block_text = self.driver.find_element(By.XPATH, '//div[@class="jobs-unified-top-card__primary-description"]').text
                match = re.search(r'\b\d+\s+applicants?\b', block_text)
                if match:
                    job_applications = match.group(0)
                else:
                    raise ValueError('No job applications found')
            except Exception as e:
                if config.displayWarnings:
                    prYellow("⚠️ Warning in getting job_applications: " + str(e)[0:50])
                job_applications = ""

        formatted_date = datetime.now().strftime('%m/%d/%Y')

        text_to_write = job_title + "," + job_company + "," + job_location + "," + job_work_place + "," + job_posted_date + "," + formatted_date + "," + job_applications
        return text_to_write

    def easyApplyButton(self):
        try:
            time.sleep(random.uniform(1, config.botSpeed))
            button = self.driver.find_element(By.XPATH, '//button[contains(@class, "jobs-apply-button") and not(@role="link")]')
            easy_apply_button = button
        except:
            easy_apply_button = False

        return easy_apply_button

    def chooseResume(self):
        try:
            be_sure_include_resume_txt = self.driver.find_element(By.CLASS_NAME, "jobs-document-upload__title--is-required")
            if be_sure_include_resume_txt.text == "Be sure to include an updated resume":
                resumes = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Choose Resume']")
                if len(resumes) == 1:
                    resumes[0].click()
                elif len(resumes) > 1:
                    resumes[config.preferredCv - 1].click()
                else:
                    prRed("❌ No resume has been selected please add at least one resume to your Linkedin account.")
        except:
            pass

    def applyProcess(self, percentage, offer_page):
        apply_pages = math.floor(100 / percentage)
        try:
            for pages in range(apply_pages - 2):
                self.handelQuestions()
                self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Continue to next step']").click()
                time.sleep(random.uniform(1, config.botSpeed))
                try:
                    error_message_element = self.driver.find_element(By.XPATH, '//span[@class="artdeco-inline-feedback__message"]')
                    if error_message_element.text != "":
                        raise Exception('An error occurred!')
                except NoSuchElementException:
                    pass

            self.handelQuestions()
            self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Review your application']").click()
            time.sleep(random.uniform(1, config.botSpeed))

            if config.followCompanies is False:
                self.driver.find_element(By.CSS_SELECTOR, "label[for='follow-company-checkbox']").click()
                time.sleep(random.uniform(1, config.botSpeed))

            self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']").click()
            time.sleep(random.uniform(1, config.botSpeed))

            result = "* 🥳 Apply Success," + str(offer_page)
            self.count_applied += 1
            utils.write_applied_URL(offer_page)
        except:
            result = "* 🥵 Extra info need," + str(offer_page)
        return result

    def handelQuestions(self):
        try:
            linkedin_profile = self.driver.find_element(By.XPATH, '//span[@class="jobs-easy-apply-form-section__group-subtitle t-14"]/p/strong')
            if linkedin_profile:
                input_element = self.driver.find_element(By.XPATH, '//input[@class="artdeco-text-input--input"]')
                input_element.send_keys("https://www.linkedin.com/in/zhaoweigu")
        except:
            try:
                vsi = self.driver.find_element(By.XPATH, '//h3[text()="Voluntary self identification"]')
                if vsi:
                    self.voluntary_self_identification()
            except NoSuchElementException:
                try:
                    question_blocks = self.driver.find_elements(By.CLASS_NAME, 'jobs-easy-apply-form-section__grouping')
                    for block in question_blocks:
                        question, q_type = self.getQuestion(block)
                        if question and q_type:
                            self.answerQuestions(block, question, q_type)
                except:
                    pass

    def voluntary_self_identification(self):
        try:
            self.driver.find_element(By.XPATH, f'//label[@data-test-text-selectable-option__label="{config.gender}"]').click()
            time.sleep(random.uniform(1, config.botSpeed))

            select_element = self.driver.find_element(By.CSS_SELECTOR, "select[data-test-text-entity-list-form-select]")
            select = Select(select_element)
            select.select_by_visible_text(config.raceEthnicity)
            time.sleep(random.uniform(1, config.botSpeed))

            self.driver.find_element(By.XPATH, f'//label[@data-test-text-selectable-option__label="{config.veteranStatus}"]').click()
            time.sleep(random.uniform(1, config.botSpeed))

            self.driver.find_element(By.XPATH, '//label[@data-test-text-selectable-option__label="No, I Don\'t Have A Disability, Or A History/Record Of Having A Disability"]').click()
            time.sleep(random.uniform(1, config.botSpeed))

            div_element = self.driver.find_element(By.XPATH, '//div[@class="artdeco-text-input--container ember-view"]')
            input_element = div_element.find_element(By.XPATH, './input')
            input_element.send_keys(config.legalName)
            time.sleep(random.uniform(1, config.botSpeed))

            today = date.today().strftime("%m/%d/%Y")
            date_input_element = self.driver.find_element(By.XPATH, '//input[@name="artdeco-date"]')
            date_input_element.send_keys(today)
            time.sleep(random.uniform(1, config.botSpeed))
        except:
            pass

    @staticmethod
    def getQuestion(block):
        try:
            single_line_question = block.find_element(By.XPATH, './/label[@class="artdeco-text-input--label"]')
            if single_line_question:
                question = single_line_question.text
                return question, "single_line_question"
        except:
            pass

        try:
            single_line_question = block.find_element(By.XPATH, '//*[@data-test-single-typeahead-entity-form-title]//span[not(@class="visually-hidden")]')
            if single_line_question:
                question = single_line_question.text
                return question, "single_line_question"
        except:
            pass

        try:
            radio_question = block.find_element(By.XPATH, './/span[@data-test-form-builder-radio-button-form-component__title]/span')
            if radio_question:
                question = radio_question.text
                return question, "radio_button"
        except:
            pass

        try:
            entity_list_question = block.find_element(By.XPATH, './/label[@data-test-text-entity-list-form-title]/span[not(contains(@class, "visually-hidden"))]')
            if entity_list_question:
                question = entity_list_question.text
                return question, "entity_list_question"
        except:
            return "", ""

    def answerQuestions(self, block, question, q_type):
        stripped_qa_dict = {re.sub('---.*?---', '', key): value for key, value in self.qa_dict.items()}

        if question in stripped_qa_dict:
            if stripped_qa_dict[question] != "":
                match q_type.casefold():
                    case "single_line_question":
                        try:
                            value = block.find_element(By.CSS_SELECTOR, 'input.artdeco-text-input--input').get_attribute('value')
                            if value:
                                if value != stripped_qa_dict[question]:
                                    text_input = block.find_element(By.CSS_SELECTOR, 'input.artdeco-text-input--input')
                                    text_input.clear()
                                    text_input.send_keys(stripped_qa_dict[question])
                                    time.sleep(random.uniform(1, config.botSpeed))
                            else:
                                text_input = block.find_element(By.CSS_SELECTOR, 'input.artdeco-text-input--input')
                                text_input.send_keys(stripped_qa_dict[question])
                                time.sleep(random.uniform(1, config.botSpeed))
                        except:
                            try:
                                value = block.find_element(By.CSS_SELECTOR, 'input[role="combobox"]').get_attribute('value')
                                if value:
                                    if value != stripped_qa_dict[question]:
                                        text_input = block.find_element(By.CSS_SELECTOR, 'input[role="combobox"]')
                                        text_input.clear()
                                        text_input.send_keys(stripped_qa_dict[question])
                                        time.sleep(random.uniform(1, config.botSpeed))
                                        options = self.driver.find_elements(By.CSS_SELECTOR, 'div.basic-typeahead__triggered-content.fb-single-typeahead-entity__triggered-content[role="listbox"] div')
                                        for option in options:
                                            if option.text == stripped_qa_dict[question]:
                                                option.click()
                                                break
                                        time.sleep(random.uniform(1, config.botSpeed))
                                else:
                                    text_input = block.find_element(By.CSS_SELECTOR, 'input[role="combobox"]')
                                    text_input.send_keys(stripped_qa_dict[question])
                                    time.sleep(random.uniform(1, config.botSpeed))
                                    options = self.driver.find_elements(By.CSS_SELECTOR, 'div.basic-typeahead__triggered-content.fb-single-typeahead-entity__triggered-content[role="listbox"] div')
                                    for option in options:
                                        if option.text == stripped_qa_dict[question]:
                                            option.click()
                                            break
                                    time.sleep(random.uniform(1, config.botSpeed))
                            except Exception as e:
                                if config.displayWarnings:
                                    prYellow(f"An exception of type {type(e).__name__} occurred. Here are is the location: single_line_question1")

                    case "radio_button":
                        try:
                            yes_button_label = block.find_element(By.XPATH, './/label[text()="Yes"]')
                            no_button_label = block.find_element(By.XPATH, './/label[text()="No"]')

                            yes_button_before_color = self.driver.execute_script("return window.getComputedStyle(arguments[0], '::before').getPropertyValue('background-color')", yes_button_label)
                            no_button_before_color = self.driver.execute_script("return window.getComputedStyle(arguments[0], '::before').getPropertyValue('background-color')", no_button_label)

                            if yes_button_before_color != 'rgb(5, 118, 66)' and no_button_before_color != 'rgb(5, 118, 66)':
                                if stripped_qa_dict[question].lower() == "yes":
                                    block.find_element(By.XPATH, './/label[@data-test-text-selectable-option__label="Yes"]').click()
                                    time.sleep(random.uniform(1, config.botSpeed))
                                else:
                                    block.find_element(By.XPATH, './/label[@data-test-text-selectable-option__label="No"]').click()
                                    time.sleep(random.uniform(1, config.botSpeed))
                            elif stripped_qa_dict[question].lower() == "yes" and yes_button_before_color != 'rgb(5, 118, 66)':
                                block.find_element(By.XPATH, './/label[@data-test-text-selectable-option__label="Yes"]').click()
                                time.sleep(random.uniform(1, config.botSpeed))
                            elif stripped_qa_dict[question].lower() == "no" and no_button_before_color != 'rgb(5, 118, 66)':
                                block.find_element(By.XPATH, './/label[@data-test-text-selectable-option__label="No"]').click()
                                time.sleep(random.uniform(1, config.botSpeed))
                        except Exception as e:
                            if config.displayWarnings:
                                prYellow(f"An exception of type {type(e).__name__} occurred. Here are the is location: radio_button1")

                    case "entity_list_question":
                        try:
                            select_element = block.find_element(By.CSS_SELECTOR, 'select[data-test-text-entity-list-form-select]')
                            select_object = Select(select_element)
                            selected_option = select_object.first_selected_option

                            if selected_option.text == "Select an option":
                                select_element = block.find_element(By.CSS_SELECTOR, 'select[data-test-text-entity-list-form-select=""]')
                                select = Select(select_element)
                                answer = stripped_qa_dict[question]
                                select.select_by_visible_text(answer)
                                time.sleep(random.uniform(1, config.botSpeed))
                            elif selected_option.text != stripped_qa_dict[question]:
                                select_element = block.find_element(By.CSS_SELECTOR, 'select[data-test-text-entity-list-form-select=""]')
                                select = Select(select_element)
                                answer = stripped_qa_dict[question]
                                select.select_by_visible_text(answer)
                                time.sleep(random.uniform(1, config.botSpeed))
                        except Exception as e:
                            if config.displayWarnings:
                                prYellow(f"An exception of type {type(e).__name__} occurred. Here are the is location: entity_list_question1")
        else:
            match q_type.casefold():
                case "single_line_question":
                    try:
                        input_field = block.find_element(By.CSS_SELECTOR, 'input.artdeco-text-input--input')
                        entered_value = input_field.get_attribute('value')
                        question_texts = question + "---single_line_question---"
                        self.qa_dict[question_texts] = entered_value
                        utils.add_to_qa_dict(question_texts, self.qa_dict[question_texts])
                    except:
                        try:
                            input_field = block.find_element(By.CSS_SELECTOR, 'input[role="combobox"]')
                            entered_value = input_field.get_attribute('value')
                            question_texts = question + "---single_line_question---"
                            self.qa_dict[question_texts] = entered_value
                            utils.add_to_qa_dict(question_texts, self.qa_dict[question_texts])
                        except Exception as e:
                            if config.displayWarnings:
                                prYellow(f"An exception of type {type(e).__name__} occurred. Here are the is location: single_line_question2")

                case "radio_button":
                    try:
                        yes_button_label = block.find_element(By.XPATH, './/label[text()="Yes"]')
                        no_button_label = block.find_element(By.XPATH, './/label[text()="No"]')

                        yes_button_before_color = self.driver.execute_script("return window.getComputedStyle(arguments[0], '::before').getPropertyValue('background-color')", yes_button_label)
                        no_button_before_color = self.driver.execute_script("return window.getComputedStyle(arguments[0], '::before').getPropertyValue('background-color')", no_button_label)

                        question_texts = question + "---radio_button---"

                        if yes_button_before_color == 'rgb(5, 118, 66)':
                            self.qa_dict[question_texts] = "Yes"
                        elif no_button_before_color == 'rgb(5, 118, 66)':
                            self.qa_dict[question_texts] = "No"
                        else:
                            self.qa_dict[question_texts] = ""

                        utils.add_to_qa_dict(question_texts, self.qa_dict[question_texts])
                    except Exception as e:
                        if config.displayWarnings:
                            prYellow(f"An exception of type {type(e).__name__} occurred. Here are the is location: radio_button2")

                case "entity_list_question":
                    try:
                        select_element = block.find_element(By.CSS_SELECTOR, 'select[data-test-text-entity-list-form-select]')
                        select_object = Select(select_element)
                        selected_option = select_object.first_selected_option
                        options = select_object.options
                        option_texts = question + "---" + ', '.join([option.text for option in options]) + "---"
                        if selected_option.text == "Select an option":
                            self.qa_dict[option_texts] = ""
                        else:
                            self.qa_dict[option_texts] = selected_option.text
                        utils.add_to_qa_dict(option_texts, self.qa_dict[option_texts])
                    except Exception as e:
                        if config.displayWarnings:
                            prYellow(f"An exception of type {type(e).__name__} occurred. Here are the is location: entity_list_question2")


start = time.time()
Linkedin().linkJobApply()
end = time.time()
prYellow("---Took: " + str(round((time.time() - start) / 60)) + " minute(s).")
