from Webscraper import CustomChrome
from pathlib import Path
import json
from time import sleep
from selenium.webdriver.common.by import By
from pprint import pprint

class FidelityChrome(CustomChrome):
    def __init__(self, fi_account, incognito=False, path_to_chrome=None, headless=False, disable_gpu=False, window_size=False, disable_extensions=False) -> None:
        super().__init__(incognito=incognito, path_to_chrome=path_to_chrome, headless=headless, disable_gpu=disable_gpu, window_size=window_size, disable_extensions=disable_extensions)
        self.fi_account = fi_account
        self.logging_in()
        

    def logging_in(self):
        self.browser.get('https://digital.fidelity.com/prgw/digital/login/full-page')

        self.wait_until_id_element_object_found(self.browser, 'userId-input', 20)
        sleep(1)
        self.browser.find_element_by_id('userId-input').send_keys(self.fi_account['username'])
        self.wait_until_id_element_object_found(self.browser, 'password', 20)
        sleep(1)
        self.browser.find_element_by_id('password').send_keys(self.fi_account['password'])
        self.wait_until_id_element_object_found(self.browser, 'fs-login-button', 20)
        sleep(1)
        self.browser.find_element_by_id('fs-login-button').click()

    def get_portfolio(self):
        pass

    def update_investment_values(self, interval=10):
        sleep(10)
        self.wait_until_css_element_object_found(self.browser, '.account-selector--all-accounts-balance')
        self.browser.find_element_by_css_selector('.account-selector--all-accounts-balance').click()
        
        while True:
            self.wait_until_id_element_object_found(self.browser, 'tab-2', 20)
            self.browser.find_element_by_id('tab-2').click()
            sleep(interval)
    
    def __exit__(self, *args):
        self.wait_until_css_element_object_found(self.browser, '.pnls.last-child', 20)
        self.browser.find_element_by_css_selector('.pnls.last-child').click()
        super().__exit__(*args)

if __name__ == '__main__':

    with open(Path('Confidential/confidential.json'), 'r') as confidential:
        confid_json = json.loads(confidential.read())
    fi_account = confid_json['fidelity_investments']

    with FidelityChrome(fi_account, incognito=False, disable_extensions=True) as fidelity_investments:
        fidelity_investments.update_investment_values()