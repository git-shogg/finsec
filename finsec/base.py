import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd
import pdb
import os

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
        self.manager = None
        self._last_100_13f_filings_url = None
        
        self.filings = {}

    def _validate_cik(self, cik):
        """Check if CIK is 10 digit string."""
        if not (isinstance(cik, str) and len(cik) == 10 and cik.isdigit()):
            raise Exception("""Invalid CIK Provided""")
        return cik

    def _get_last_100_13f_filings_url(self):
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
        
        return self._last_100_13f_filings_url
    
    def _get_bs4_text(self, bs4_obj):
        try:
            return bs4_obj.text
        except:
            return "N/A"

    def _recent_qtr_year(self, datetime_o):
        datetime_obj = datetime.strptime(datetime_o, '%Y-%m-%d')
        quarter_dict = {1:4, 2:1, 3:2, 4:3} # Every statement released is for the previous quarter.
        release_qtr = quarter_dict[(datetime_obj.month - 1)//3 + 1]
        year = datetime_obj.year
        return "Q{}-{}".format(release_qtr, year)

    def _parse_13f_url(self, url):
        response = requests.get(_BASE_URL_+url, headers=_REQ_HEADERS_)
        soup = bs(response.text, "html.parser")
        import re

        url_primary_document = soup.find_all('a', attrs = {'href': re.compile('xml')})[1]['href'] # Primary doc is always 2nd in the list.
        url_list_document = soup.find_all('a', attrs = {'href': re.compile('xml')})[3]['href'] # xml list is always 4th in the list.

        response = requests.get(_BASE_URL_+url_primary_document, headers=_REQ_HEADERS_)
        primary_doc = bs(response.text, "xml")

        response = requests.get(_BASE_URL_ + url_list_document, headers=_REQ_HEADERS_)
        list_doc = bs(response.text, "xml")

        # Get primary doc detail
        filing_manager = self._get_bs4_text(primary_doc.find("filingManager").find("name"))
        business_address = self._get_bs4_text(primary_doc.find("street1")) + ", " + self._get_bs4_text(primary_doc.find("city")) + ", " + self._get_bs4_text(primary_doc.find("stateOrCountry")) + ", " + self._get_bs4_text(primary_doc.find("zipCode"))
        submission_type = self._get_bs4_text(primary_doc.find("submissionType"))
        period_of_report = self._get_bs4_text(primary_doc.find("periodOfReport"))

        signature_name = self._get_bs4_text(primary_doc.find("signatureBlock").find("name"))
        signature_title = self._get_bs4_text(primary_doc.find("signatureBlock").find("title"))
        signature_phone = self._get_bs4_text(primary_doc.find("signatureBlock").find("phone"))
        signature_city = self._get_bs4_text(primary_doc.find("signatureBlock").find("city"))
        signature_state = self._get_bs4_text(primary_doc.find("signatureBlock").find("stateOrCountry"))
        signature_date = self._get_bs4_text(primary_doc.find("signatureBlock").find("signatureDate"))

        portfolio_value = int(self._get_bs4_text(primary_doc.find("summaryPage").find("tableValueTotal"))) * 1000
        count_holdings = int(self._get_bs4_text(primary_doc.find("summaryPage").find("tableEntryTotal")))

        filing_cover_page = {
            "filing_manager":filing_manager, 
            "business_address":business_address, 
            "submission_type":submission_type, 
            "period_of_report":period_of_report, 
            "signature_name":signature_name, 
            "signature_title":signature_title, 
            "signature_phone":signature_phone, 
            "signature_city":signature_city, 
            "signature_state":signature_state, 
            "signature_date":signature_date, 
            "portfolio_value":portfolio_value, 
            "count_holdings":count_holdings, 
        }

        # Get list doc detail
        list_of_holdings = list_doc.findAll("infoTable")
        result = []
        for each_holding in list_of_holdings:
            name_of_issuer = self._get_bs4_text(each_holding.find("nameOfIssuer"))
            title_of_class = self._get_bs4_text(each_holding.find("titleOfClass"))
            cusip = self._get_bs4_text(each_holding.find("cusip"))
            holding_value = int(each_holding.find("value").text) * 1000
            share_or_principal_amount = self._get_bs4_text(each_holding.find("shrsOrPrnAmt").find("sshPrnamtType"))
            share_or_principal_amount_count = int(each_holding.find("shrsOrPrnAmt").find("sshPrnamt").text)
            # put_or_call = each_holding.find("SOMETHING").text
            investment_discretion = self._get_bs4_text(each_holding.find("investmentDiscretion"))
            other_manager = self._get_bs4_text(each_holding.find("otherManager"))
            voting_authority_share_or_principal_amount_count_sole = int(each_holding.find("votingAuthority").find("Sole").text)
            voting_authority_share_or_principal_amount_count_shared = int(each_holding.find("votingAuthority").find("Shared").text)
            voting_authority_share_or_principal_amount_count_none = int(each_holding.find("votingAuthority").find("None").text)

            result.append({"Name of issuer":name_of_issuer, "Title of class":title_of_class, "CUSIP":cusip,"Holding value":holding_value,"Share or principal type":share_or_principal_amount,"Share or principal amount count":share_or_principal_amount_count,"Put or call":None, "Investment discretion":investment_discretion, "Other manager":other_manager, "Voting authority sole count":voting_authority_share_or_principal_amount_count_sole, "Voting authority shared count":voting_authority_share_or_principal_amount_count_shared, "Voting authority none count":voting_authority_share_or_principal_amount_count_none})
        
        holdings_table = pd.DataFrame.from_dict(result)

        simplified_columns = ['Name of issuer', 'Title of class', 'CUSIP', 'Share or principal type', 'Put or call','Holding value', 'Share or principal amount count']
        holdings_table_dropped_na = holdings_table[simplified_columns].dropna(axis=1)
        simplified_holdings_table = holdings_table_dropped_na.groupby(holdings_table_dropped_na.columns[:-2].to_list(), sort=False,as_index=False).sum()

        if self.manager == None:
            self.manager = filing_cover_page.get('filing_manager')

        return filing_cover_page, holdings_table, simplified_holdings_table

    def convert_filings_to_excel(self, simplified=True, inc_cover_page_tabs=False):
        """Outputs existing 'self.filings' dictionary to excel. Note that this will overwrite any existing files that may be present."""
        table_type = "Simplified Holdings Table" if simplified == True else "Holdings Table"
        if len(self.filings)>0:
            if os.path.exists('{}.xlsx'.format(self.cik)):
                os.remove('{}.xlsx'.format(self.cik))
            with pd.ExcelWriter('{}.xlsx'.format(self.cik)) as writer: 
                for qtr_year in self.filings:
                    if inc_cover_page_tabs == True:
                        pd.DataFrame.from_dict(self.filings[qtr_year]['Cover Page'],orient='index').to_excel(writer,sheet_name="{}_cover_pg".format(qtr_year))
                    pd.read_json(self.filings[qtr_year][table_type]).to_excel(writer,sheet_name="{}_holdings".format(qtr_year))
        return        

    def get_latest_13f_filing(self, simplified=True):
        """Returns the latest 13F-HR filing."""
        self._get_last_100_13f_filings_url()

        latest_url_date = self._last_100_13f_filings_url[0]

        latest_13f_cover_page, latest_holdings_table, latest_simplified_holdings_table = self._parse_13f_url(latest_url_date[0])

        qtr_year_str = self._recent_qtr_year(latest_url_date[1])
        self.filings.update({
                        qtr_year_str:{
                            "Cover Page":latest_13f_cover_page, 
                            "Period of Report":latest_13f_cover_page['period_of_report'],
                            "Holdings Table":latest_holdings_table.to_json(), 
                            "Simplified Holdings Table":latest_simplified_holdings_table.to_json(), 
                            "Fund Value":latest_13f_cover_page['portfolio_value'], 
                            "Holdings Count":latest_13f_cover_page['count_holdings'],
                            "Simplified Holdings Count":len(latest_simplified_holdings_table),
                            "Latest 13F":True
                            }})
        
        if simplified==True: 
            return latest_simplified_holdings_table
        else: 
            return latest_holdings_table
        
    def get_latest_13f_filing_cover_page(self):
        """Returns the latest 13F-HR filing cover page."""
        latest_qtr_year = [x for x in self.filings.keys() if self.filings[x]['Latest 13F']]
        if len(latest_qtr_year) >0:
            return self.filings[latest_qtr_year[0]]['Cover Page']
        else:
            self.get_latest_13f_filing()
            latest_qtr_year = [x for x in self.filings.keys() if self.filings[x]['Latest 13F']]
            return self.filings[latest_qtr_year[0]]['Cover Page']

    def get_latest_13f_value(self):
        """Returns the latest 13F-HR value of fund value"""
        latest_qtr_year = [x for x in self.filings.keys() if self.filings[x]['Latest 13F']]
        if len(latest_qtr_year) >0:
            return self.filings[latest_qtr_year[0]]['Fund Value']
        else:
            self.get_latest_13f_filing()
            latest_qtr_year = [x for x in self.filings.keys() if self.filings[x]['Latest 13F']]
            return self.filings[latest_qtr_year[0]]['Fund Value']

    def get_latest_13f_num_holdings(self, holdings_type='Simplified Holdings Count'):
        """Returns the latest 13F-HR number of holdings"""
        latest_qtr_year = [x for x in self.filings.keys() if self.filings[x]['Latest 13F']]
        if len(latest_qtr_year) >0:
            return self.filings[latest_qtr_year[0]][holdings_type]
        else:
            self.get_latest_13f_filing()
            latest_qtr_year = [x for x in self.filings.keys() if self.filings[x]['Latest 13F']]
            return self.filings[latest_qtr_year[0]][holdings_type]

    def get_13f_filing(self, qtr_year: str):
        """Returns the requested 13F-HR filing."""
        self._get_last_100_13f_filings_url()
        if len(self.filings) != 0:
            if qtr_year in self.filings:
                return self.filings[qtr_year]["Cover Page"], pd.read_json(self.filings[qtr_year]["Holdings Table"]), pd.read_json(self.filings[qtr_year]["Simplified Holdings Table"])
        filing_url_date = None
        latest_13_f_filing = False
        for index, filing in enumerate(self._last_100_13f_filings_url):
            datetime_obj = datetime.strptime(filing[1], '%Y-%m-%d')
            quarter_dict = {1:4, 2:1, 3:2, 4:3} # Every statement released is for the previous quarter.
            release_qtr = quarter_dict[(datetime_obj.month - 1)//3 + 1]
            year = datetime_obj.year
            if "Q{}-{}".format(release_qtr, year) == qtr_year:
                filing_url_date = filing
                if index == 0:
                    latest_13_f_filing = True
        if filing_url_date == None:
            raise Exception("No filing could be found for the period {}".format(qtr_year))

        cover_page, holdings_table, simplified_holdings_table = self._parse_13f_url(filing_url_date[0])
        self.filings.update({
                        qtr_year:{
                            "Cover Page":cover_page, 
                            "Period of Report":cover_page['period_of_report'],
                            "Holdings Table":holdings_table.to_json(), 
                            "Simplified Holdings Table":simplified_holdings_table.to_json(), 
                            "Fund Value":cover_page['portfolio_value'], 
                            "Holdings Count":cover_page['count_holdings'],
                            "Simplified Holdings Count":len(simplified_holdings_table),
                            "Latest 13F":latest_13_f_filing}})

        return cover_page, holdings_table, simplified_holdings_table

    
    