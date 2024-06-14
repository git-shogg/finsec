"""
Tests for 13F functionality
"""

import pandas as pd

import finsec


class Test:
    def setup_class(self):
        self.cik = "0001067983"
        self.filing = finsec.Filing(self.cik, declared_user="git-shogg")

    def test_cik(self):
        assert self.filing.cik == self.cik

    def test_latest_13f_filing(self):
        df = self.filing.latest_13f_filing()
        assert isinstance(df, pd.DataFrame)
        assert len(self.filing.filings) > 0

    def test_latest_13f_filing_detailed(self):
        df = self.filing.latest_13f_filing_detailed
        assert isinstance(df, pd.DataFrame)

    def test_latest_13f_filing_cover_page(self):
        result = self.filing.latest_13f_filing_cover_page
        assert isinstance(result, dict)

    def test_latest_13f_portfolio_value(self):
        portfolio_value = self.filing.latest_13f_portfolio_value
        assert isinstance(portfolio_value, float)

    def test_latest_13f_count_holdings(self):
        holdings_count = self.filing.latest_13f_count_holdings
        assert isinstance(holdings_count, int)

    def test_get_a_13f_filing(self):
        cover_page, holdings_table, simplified_holdings_table = (
            self.filing.get_a_13f_filing("Q2-2022")
        )
        assert isinstance(cover_page, dict)
        assert isinstance(holdings_table, pd.DataFrame)
        assert isinstance(simplified_holdings_table, pd.DataFrame)
