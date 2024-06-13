import requests
from bs4 import BeautifulSoup as bs

from .base import FilingBase

class Filing(FilingBase):

    def get_a_13f_filing(self, qtr_year, amend_filing=True):
        return self.get_13f_filing(qtr_year, amend_filing)

    def filings_to_excel(self, simplified=True, inc_cover_page_tabs=False):
        return self.convert_filings_to_excel(simplified, inc_cover_page_tabs)

    def latest_13f_filing(self, simplified=True, amend_filing=True):
        return self.get_latest_13f_filing(simplified, amend_filing)
    
    @property
    def latest_13f_portfolio_value(self):
        return self.get_latest_13f_value()

    @property
    def latest_13f_count_holdings(self):
        return self.get_latest_13f_num_holdings()

    @property
    def latest_13f_filing_detailed(self):
        return self.get_latest_13f_filing(simplified=False,ignore_amendments=False)

    @property
    def latest_13f_filing_cover_page(self):
        return self.get_latest_13f_filing_cover_page()
    
    
    
