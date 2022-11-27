import requests
from bs4 import BeautifulSoup as bs

from .base import FilingBase

class Filing(FilingBase):
    
    def latest_13f(cik: str = ''):
        return None

    

    # @property
    # def filings(self):
    #     return self.get_filings()

    @property
    def latest_filing(self):
        return self.get_latest_filing()
    
    @property
    def filing(self, qtr_year):
        return self.get_filing(qtr_year)