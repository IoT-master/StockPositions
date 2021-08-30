from Webscraper import CustomChrome
from pathlib import Path
import json
from time import sleep
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
        sleep(5)
        self.wait_until_css_element_object_is_clickable(self.browser, '.account-selector--all-accounts-balance', 60)
        self.browser.find_element_by_css_selector('.account-selector--all-accounts-balance').click()

        self.wait_until_css_element_object_is_clickable(self.browser, '.account-selector--tab-all', 60)
        self.browser.find_element_by_class_name('account-selector--tab-all').click()

        account_view = {
            'All Account Value': 0,
            'All Account Change': 0,
            'All Account Percentage:': 0
        }
        while True:
            self.wait_until_class_name_element_object_found(self.browser, 'account-selector--tab-all', 60)
            all_accounts = self.browser.find_element_by_class_name('account-selector--tab-all')
            account_view['All Account Value'] = self.browser.find_element_by_class_name('account-selector--tab-row').text
            account_view['All Account Change'] = all_accounts.get_attribute('data-today-change-value')
            account_view['All Account Percentage:'] = all_accounts.get_attribute('data-today-change-pct-value')
            pprint(account_view)

            self.wait_until_css_element_object_found(self.browser, '#posweb-grid_top-presetviews_refresh_settings_share .posweb-grid_top-refresh-button', 60)
            self.wait_until_css_element_object_is_clickable(self.browser, '#posweb-grid_top-presetviews_refresh_settings_share .posweb-grid_top-refresh-button', 60)
            sleep(2)
            self.browser.find_element_by_css_selector('#posweb-grid_top-presetviews_refresh_settings_share .posweb-grid_top-refresh-button').click()
            sleep(interval)
    
    def __exit__(self, *args):
        self.wait_until_css_element_object_found(self.browser, '.pnlogin .pnls.last-child a')
        self.browser.find_element_by_css_selector('.pnlogin .pnls.last-child a').click()
        super().__exit__(*args)

if __name__ == '__main__':

    with open(Path('Confidential/confidential.json'), 'r') as confidential:
        confid_json = json.loads(confidential.read())
    fi_account = confid_json['fidelity_investments']

    with FidelityChrome(fi_account, incognito=False, disable_extensions=True) as fidelity_investments:
        fidelity_investments.update_investment_values(interval=5)