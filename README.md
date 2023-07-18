# LinkedInEasyApplyBot
An automated bot that can help you to apply for jobs

## Installation 🔌

- Clone the repo `git clone https://github.com/zw-g/LinkedInEasyApplyBot.git`
- Make sure to use `Python 3.11` and make sure `pip` is installed
- Install dependencies with `pip3 install -r requirements.yaml`

## Setup ⚙️

- Configure your LinkedIn credentials in the `config.py` file at lines 3 and 4.
- Adjust the settings in the `config.py` file to suit your needs:
  - `headless`: Determines whether the browser operates in the background or not.
    - If `headless = False`, the browser window will be visible, and you should remain on the webpage to see what the bot is doing.
    - If `headless = True`, the browser will operate in the background, freeing you to do other tasks.
  - `followCompanies`: Indicates whether the bot should follow companies after a successful application. Set `True` for yes and `False` for no.
  - `preferredCv`: If you have multiple CVs, select which one you want the bot to use by setting the corresponding number (1 for the first CV on the list, 2 for the second, etc).
- In the `config.py` file, answer all questions necessary for the bot's operation.

## Use

### How to Run
- To launch the bot, execute the command `python3 linkedin.py` in your terminal. 
- Alternatively, you can run it using your preferred Integrated Development Environment (IDE).

### Bot Actions History:
- To track the actions performed by the bot, check the 'Applied Jobs DATA.csv' file generated in the `/data` folder. This file logs all the job applications made by the bot, and a new file will be created for each different date of operations.

### Answer Job Application Question 💡

- Providing answers to the questions in `questionAnswer.csv` is crucial to help the bot successfully apply for jobs on your behalf, thereby improving your job application success rate.
  - For questions followed by `---single_line_question---`, you are expected to provide a single line or string answer. Write your answer after the comma, but avoid including any commas within your answer. If a comma is necessary, enclose your answer in double-quotes "".
  - For questions followed by `---radio_button---`, the bot expects a binary answer - either Yes or No. Write your chosen option after the comma.
  - For questions followed by `---Select an option, option1, option2, etc---`, you are required to choose one of the given options. Copy your chosen option and paste it after the comma.
