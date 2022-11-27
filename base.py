import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
import pdb

_BASE_URL_ = 'https://www.sec.gov'
_13F_SEARCH_URL_ = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type=13F-HR&count=100'
_REQ_HEADERS_ = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'HOST': 'www.sec.gov',
                }

class FilingBase():
    def __init__(self, cik):
        
        self.cik = self._validate_cik(cik)
        self.filing_manager = None
        self.sic = None
        self.state_location = None
        self.state_of_incorp = None
        self.fiscal_year_end = None
        self.file_number = None
        self.business_address = None
        self.mailing_address = None
        self.submission_type = None
        self.period_of_report = None
        
        self.signature_name = None
        self.signature_title = None
        self.signature_phone = None
        self.signature_city = None
        self.signature_state = None
        self.signature_date = None

        self.portfolio_value = None
        self.count_holdings = None
        
        self._last_100_13f_filings_url = None

    def _validate_cik(self, cik):
        """Check if CIK is 10 digit string."""
        if not (isinstance(cik, str) and len(cik) == 10 and cik.isdigit()):
            raise Exception("""Invalid CIK Provided""")
        return cik

    def _get_filings(self):
        """Returns list of last 100 13F-HR filings."""
        if self._last_100_13f_filings_url:
            return

        webpage = requests.get(_13F_SEARCH_URL_.format(self.cik),headers=_REQ_HEADERS_)
        soup = bs(webpage.text,"html.parser")
        results_table = soup.find(lambda table: table.has_attr('summary') and table['summary']=="Results")
        
        th = 0
        for headers in results_table.find_all('th'):
            if "Format" in headers.text:
                format_col = th
            elif "Filing Date" in headers.text:
                filing_date_col = th
            th += 1
        
        url_endings = []
        filing_dates = []

        for row in results_table.find_all('tr'):
            tds = row.find_all('td')
            try:
                url_endings.append(tds[format_col].find('a')['href'])
                filing_dates.append(tds[filing_date_col].text)
            except:
                pass
        self._last_100_13f_filings_url = list(zip(url_endings, filing_dates))
        print("Have run get filings")
        return self._last_100_13f_filings_url
    
    def _parse_13f_url(self, url):
        response = requests.get(_BASE_URL_+url, headers=_REQ_HEADERS_)
        soup = bs(response.text, "html.parser")
        import re
        url_xml_document = soup.find_all('a', attrs = {'href': re.compile('xml')}, text=re.compile("primary_doc.xml"))[0]['href']
        
        response = requests.get(_BASE_URL_+url_xml_document, headers=_REQ_HEADERS_)
        soup = bs(response.text, "lxml")
        
        self.business_name = None
        self.sic = None
        self.state_location = None
        self.state_of_incorp = None
        self.fiscal_year_end = None
        self.file_number = None
        self.business_address = None
        self.mailing_address = None


        return None

    def get_latest_filing(self):
        """Returns the latest 13F-HR filing."""
        self._get_filings()
        latest_url_date = self._last_100_13f_filings_url[0]
        import pdb
        pdb.set_trace()
        latest_filing = self._parse_13f_url(latest_url_date[0])
        
        return latest_filing
    
    def get_filing(self, qtr_year: str):
        """Returns the requested 13F-HR filing."""
        self._get_filings()

        for filing in self._last_100_13f_filings_url:
            datetime_obj = datetime.strptime(filing[1], '%Y-%m-%d')
            quarter_dict = {1:4, 2:1, 3:2, 4:3} # Every statement released is for the previous quarter.
            release_qtr = quarter_dict[(datetime_obj.month - 1)//3 + 1]
            year = datetime_obj.year
            if "Q{}-{}".format(release_qtr, year) == qtr_year:
                return filing
        return None
    
