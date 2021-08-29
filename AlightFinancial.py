from Webscraper import CustomChrome
from pathlib import Path
import json
from time import sleep
from selenium.webdriver.common.by import By
from pprint import pprint

class AFCustomChrome(CustomChrome):
    def __init__(self, af_account, incognito=False, path_to_chrome=None, headless=False, disable_gpu=False, window_size=False, disable_extensions=False) -> None:
        super().__init__(incognito=incognito, path_to_chrome=path_to_chrome, headless=headless, disable_gpu=disable_gpu, window_size=window_size, disable_extensions=disable_extensions)
        self.af_account = af_account
        self.logging_in()
        

    def logging_in(self):
        self.browser.get('https://alightfs.netxinvestor.com/nxi/login')

        self.wait_for_possible_element(self.browser, (By.ID, 'onetrust-accept-btn-handler'), 20)
        if self.browser.find_elements_by_id('onetrust-accept-btn-handler'):
            self.browser.find_element_by_id('onetrust-accept-btn-handler').click()

        self.wait_for_possible_element(self.browser, (By.ID, 'dijit_form_ValidationTextBox_1'), 20)
        self.browser.find_element_by_id('dijit_form_ValidationTextBox_1').send_keys(self.af_account['username'])
        self.browser.find_element_by_id('dijit_form_ValidationTextBox_2').send_keys(self.af_account['password'])
        self.browser.find_element_by_id('dijit_form_Button_0_label').click()
        self.wait_until_class_name_element_object_found(self.browser, 'secQuestion')
        if self.is_present(self.browser.find_element_by_class_name('secQuestion')):
            sec_question = self.browser.find_element_by_class_name('secQuestion').text
            sec_answer = self.af_account['security_?'][sec_question]
            self.browser.find_element_by_id('dijit_form_ValidationTextBox_3').send_keys(sec_answer)
            self.browser.find_element_by_id('dijit_form_RadioButton_1').click()
            self.browser.find_element_by_id('dijit_form_Button_2_label').click()
        
        self.wait_for_possible_element(self.browser, (By.CLASS_NAME, 'mat-button-wrapper'), 20)
        if len(self.browser.find_elements_by_class_name('mat-button-wrapper')):
            self.wait_until_class_name_element_object_found(self.browser, 'mat-button-wrapper', 20)
            self.browser.find_element_by_class_name('mat-button-wrapper').click()

        self.wait_until_id_element_object_found(self.browser, 'assetsLabel', 20)
        self.browser.find_element_by_id('nav-holdings').click()

    def _get_transaction(self, stock_number):
            trans_history = self.browser.find_element_by_css_selector(f'#div{stock_number}')
            trans_date = trans_history.find_element_by_class_name('buySellDate').text
            raw_trans = trans_history.text.split('\n')
            trans_type = raw_trans[0]
            shares = float(raw_trans[3])
            price = float(raw_trans[5])
            return (trans_type, trans_date, shares, price)

    def get_portfolio(self):
        self.wait_until_class_name_element_object_found(self.browser, 'ui-state-default', 20)
        positions = self.browser.find_elements_by_class_name('ui-state-default')

        position_table = {}
        for ind_p, each_p in enumerate(positions[:-1]):
            self.wait_until_css_element_object_found(each_p, '[role="gridcell"] a', 60)
            ticker_symbol = each_p.find_element_by_css_selector('[role="gridcell"] a').text
            self.wait_until_class_name_element_object_found(each_p, 'expander', 60)
            each_p.find_element_by_class_name('expander').click()
            self.wait_until_class_name_element_object_found(each_p, 'netxinvestor-keyvalues-portlet')
            stock_number = ind_p + 1
            self.wait_until_css_element_object_found(self.browser, f'#section{stock_number}', 15)
            # Click on the 2 year mark
            self.browser.find_elements_by_css_selector(f'#section{stock_number} .clickdetails')[9].click()
            self.wait_until_css_element_object_found(each_p, 'g.highcharts-markers.highcharts-series-3.highcharts-tracker', 30)
            sleep(5)
            each_p.find_element_by_css_selector('g.highcharts-markers.highcharts-series-3.highcharts-tracker').click()
            sleep(2)
            while len(self.browser.find_elements_by_css_selector(f'#prev{stock_number}.dijitDisplayNone')) == 0:
                self.browser.find_element_by_id(f'prev{stock_number}').click()
                sleep(1)
            self.wait_until_id_element_object_found(self.browser, f'next{stock_number}')
            transaction_list = []

            transaction_list.append(self._get_transaction(stock_number))

            while len(self.browser.find_elements_by_css_selector(f'#next{stock_number}.dijitDisplayNone')) == 0:
                self.wait_until_id_element_object_found(self.browser, f'next{stock_number}')
                self.browser.find_element_by_id(f'next{stock_number}').click()
        
                transaction_list.append(self._get_transaction(stock_number))

                sleep(1)
            self.wait_until_class_name_element_object_found(each_p, 'expander')
            each_p.find_element_by_class_name('expander').click()
            position_table[ticker_symbol] = transaction_list
            numerator = list(map(lambda x: x[2]*x[3], transaction_list))
            denominator = list(map(lambda x: x[2], transaction_list))
            num_of_shares = sum(denominator)
            print(ticker_symbol)
            print(f"{sum(numerator)/num_of_shares} per share")
            print(f"{num_of_shares} shares")
            pprint(transaction_list)
        pprint(position_table)

    def __exit__(self, exec_type, exec_value, traceback):
        self.wait_for_possible_element(self.browser, (By.CLASS_NAME, 'fw-Header_Logout'))
        if self.is_present(self.browser.find_elements_by_class_name('fw-Header_Logout')):
            self.browser.find_element_by_class_name('fw-Header_Logout').click()
            self.wait_until_class_name_element_object_found(self.browser, 'alert-success')
        print('Closing browser instance')
        self.browser.quit()

if __name__ == '__main__':

    with open(Path('Confidential/confidential.json'), 'r') as confidential:
        confid_json = json.loads(confidential.read())
    af_account = confid_json['alight_financial']

    with AFCustomChrome(af_account, incognito=True, disable_extensions=True) as alight_financial:
        alight_financial.get_portfolio()