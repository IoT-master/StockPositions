from Webscraper import CustomChrome
from pathlib import Path
import json
from time import sleep
from pprint import pprint
# from selenium.webdriver.support.ui import Select

class CSCustomChrome(CustomChrome):
    def __init__(self, fi_account, incognito=False, path_to_chrome=None, headless=False, disable_gpu=False, window_size=False, disable_extensions=False) -> None:
        super().__init__(incognito=incognito, path_to_chrome=path_to_chrome, headless=headless, disable_gpu=disable_gpu, window_size=window_size, disable_extensions=disable_extensions)
        self.fi_account = fi_account
        self.logging_in()
        

    def logging_in(self):
        self.browser.get('https://client.schwab.com/Login/SignOn/CustomerCenterLogin.aspx?ReturnUrl=%2fAreas%2fAccounts%2fPositions')
        self.browser.switch_to.frame(self.browser.find_element_by_id("lmsSecondaryLogin"))
        self.wait_until_id_element_object_found(self.browser, 'LoginId', 20)
        sleep(1)
        self.browser.find_element_by_id('LoginId').send_keys(self.fi_account['username'])
        self.wait_until_id_element_object_found(self.browser, 'Password', 20)
        sleep(1)
        self.browser.find_element_by_id('Password').send_keys(self.fi_account['password'])
        self.wait_until_id_element_object_found(self.browser, 'LoginText', 20)
        sleep(1)
        self.browser.find_element_by_id('LoginText').click()

        self.browser.switch_to.default_content()
        sleep(5)
        self.wait_until_css_element_object_found(self.browser, '.acct-name')
        self.browser.find_element_by_css_selector('.acct-name').click()
        sleep(3)
        # self.wait_until_css_element_object_found(self.browser, '#brkAcc2')
        self.browser.find_element_by_id('brkAcct2').click()

    def get_portfolio(self):
        self.wait_until_css_element_object_found(self.browser, '#lnkRefresh')
        self.browser.find_element_by_id('lnkRefresh').click()
        self.browser.find_element_by_css_selector('.value').text
        # self.browser.find_element_by_css_selector('a.dayChangeOverlayLink').text
        # select = Select(self.browser.find_element_by_class_name('lbl-title'))
        # select.select_by_visible_text('HSA')
        # select.select_by_value('1')
        

    def update_investment_values(self, interval=10):
        sleep(10)

        account_view = {
            'All Account Value': 0,
            'All Account Change': 0,
            'All Account Percentage:': 0
        }
        while True:
            raw_values_list = self.browser.find_element_by_css_selector('a.dayChangeOverlayLink').text.split(' ')
            account_view['All Account Value'] = self.browser.find_element_by_css_selector('.value').text
            account_view['All Account Change'] = raw_values_list[0]
            account_view['All Account Percentage:'] = raw_values_list[1]
            pprint(account_view)

            self.wait_until_css_element_object_found(self.browser, '#lnkRefresh')
            self.browser.find_element_by_id('lnkRefresh').click()
            sleep(interval)
    
    def __exit__(self, *args):
        self.wait_until_css_element_object_found(self.browser, '.logout', 20)
        self.browser.find_element_by_css_selector('.logout').click()
        super().__exit__(*args)

if __name__ == '__main__':

    with open(Path('Confidential/confidential.json'), 'r') as confidential:
        confid_json = json.loads(confidential.read())
    cs_account = confid_json['charles_schwab']

    with CSCustomChrome(cs_account, incognito=False, disable_extensions=True) as charles:
        charles.update_investment_values()