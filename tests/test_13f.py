"""
Tests for 13F functionality
"""
import pytest
import finsec
import pandas as pd


class Test(object):
    # @pytest.fixture
    # def fixt(self):
    #     cik = '0001067983'
    #     filing = finsec.Filing(cik)
    #     return cik, filing
    # @pytest.fixture
    # def __init__(self):
    cik = '0001067983'
    filing = finsec.Filing(cik)

    def test_cik(self):
        assert self.filing.cik == self.cik 

    def test_latest_13f_filing(self):
        self.filing.latest_13f_filing
        assert isinstance(self.filing.latest_13f_filing, pd.DataFrame)
        assert len(self.filing.filings)>0

# print(filing.cik)
# pdb.set_trace()
# pdb.set_trace()

# filing.latest_13f_filing
# filing.latest_13f_filing_detailed
# filing.latest_13f_filing_cover_page
# filing.latest_13f_portfolio_value
# filing.latest_13f_count_holdings
# filing.get_a_13f_filing("Q2-2022")
# filing.filings
