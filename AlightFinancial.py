from Webscraper import CustomChrome
from pathlib import Path
import json
from time import sleep

class AFCustomChrome(CustomChrome):
    def __exit__(self, exec_type, exec_value, traceback):
        if self.is_present(self.browser.find_element_by_class_name('fw-Header_Logout')):
            self.browser.find_element_by_class_name('fw-Header_Logout').click()
            self.wait_until_class_name_element_object_found('alert-success')
        print('Closing browser instance')
        self.browser.quit()

if __name__ == '__main__':

    with open(Path.cwd().joinpath('Confidential/confidential.json'), 'r') as confidential:
        confid_json = json.loads(confidential.read())
    af_account = confid_json['alight_financial']

    with AFCustomChrome(incognito=False) as alight_financial:
        alight_financial.browser.get('https://alightfs.netxinvestor.com/nxi/login')
        alight_financial.wait_until_id_element_object_found('dijit_form_ValidationTextBox_1')
        alight_financial.browser.find_element_by_id('dijit_form_ValidationTextBox_1').send_keys(af_account['username'])
        alight_financial.browser.find_element_by_id('dijit_form_ValidationTextBox_2').send_keys(af_account['password'])
        alight_financial.browser.find_element_by_id('dijit_form_Button_0_label').click()
        alight_financial.wait_until_class_name_element_object_found('secQuestion')
        if alight_financial.is_present(alight_financial.browser.find_element_by_class_name('secQuestion')):
            sec_question = alight_financial.browser.find_element_by_class_name('secQuestion').text
            sec_answer = af_account['security_?'][sec_question]
            alight_financial.browser.find_element_by_id('dijit_form_ValidationTextBox_3').send_keys(sec_answer)
            alight_financial.browser.find_element_by_css_selector('.dijitRadio').click()
            alight_financial.browser.find_element_by_id('dijit_form_Button_2_label').click()
        
        sleep(5)
        if len(alight_financial.browser.find_elements_by_class_name('mat-button-wrapper')):
            alight_financial.browser.find_element_by_class_name('mat-button-wrapper').click()

        sleep(5)
        alight_financial.wait_until_id_element_object_found('assetsLabel')
        alight_financial.browser.find_element_by_id('nav-holdings').click()
        
        sleep(5)
        alight_financial.wait_until_class_name_element_object_found('ui-state-default')
        sleep(5)
        positions = alight_financial.browser.find_elements_by_class_name('ui-state-default')

        position_table = {}
        for ind_p, each_p in enumerate(positions[:-1]):
            ticker_symbol = each_p.find_element_by_css_selector('a').text
            each_p.find_element_by_class_name('expander').click()
            sleep(2)
            quantity_of_shares = alight_financial.browser.find_element_by_class_name('netxinvestor-keyvalues-portlet').find_element_by_css_selector('tbody tr td:nth-child(2)').text
            # Click on the 2 year mark
            sleep(5)
            if ind_p != 1:
                alight_financial.browser.find_elements_by_css_selector('#section1 a')[-1].click()
            sleep(2)
            alight_financial.browser.find_element_by_css_selector('g.highcharts-markers.highcharts-series-3.highcharts-tracker').click()
            sleep(2)
            while alight_financial.is_present(alight_financial.browser.find_element_by_id('prev1')):
                alight_financial.browser.find_element_by_id('prev1').click()
                sleep(1)
            transaction_list = []
            while alight_financial.is_present(alight_financial.browser.find_element_by_id('next1')):
                trans_history = alight_financial.browser.find_element_by_class_name('transactionHistoryChartDetail')
                trans_date = trans_history.find_element_by_class_name('buySellDate').text
                raw_trans = trans_history.find_element_by_class_name('transactionsChart').text.split('\n')
                shares = float(raw_trans[1])
                price = float(raw_trans[3])
                transaction_list.append((trans_date, shares, price))
                alight_financial.browser.find_element_by_id('next1').click()
                sleep(1)
            each_p.find_element_by_class_name('expander').click()
            position_table[ticker_symbol] = transaction_list
            numerator = list(map(lambda x: x[1]*x[2], transaction_list))
            denominator = list(map(lambda x: x[1], transaction_list))
            print(sum(numerator)/sum(denominator))
            print(transaction_list)
        print(position_table)