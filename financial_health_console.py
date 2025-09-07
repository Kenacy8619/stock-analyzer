import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

class FinancialHealthChecker:
    def __init__(self):
        pass
    
    def check_trend_with_regression(self, data_series, increasing=True):
        """
        Use linear regression to check if data shows increasing/decreasing trend
        Returns True if trend matches expectation, False otherwise
        """
        if len(data_series) < 2:
            return False
            
        # Prepare data for regression
        years = np.array(range(len(data_series))).reshape(-1, 1)
        values = np.array(data_series.values)
        
        # Remove NaN values
        valid_indices = ~np.isnan(values)
        if np.sum(valid_indices) < 2:
            return False
            
        years_clean = years[valid_indices]
        values_clean = values[valid_indices]
        
        # Fit linear regression
        model = LinearRegression()
        model.fit(years_clean, values_clean)
        
        # Check slope direction
        slope = model.coef_[0]
        
        if increasing:
            return slope > 0
        else:
            return slope < 0
    
    def analyze_stock(self, ticker):
        """Analyze stock and return results"""
        try:
            # Get stock data
            stock = yf.Ticker(ticker)
            info = stock.info
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            cashflow = stock.cashflow
            
            print(f"\n{'='*80}")
            print(f"FINANCIAL HEALTH ANALYSIS FOR {ticker.upper()}")
            print(f"{'='*80}")
            
            # Analysis results
            results = []
            
            # 1. PE/PEG Ratio Check
            pe_ratio = info.get('trailingPE', None)
            peg_ratio = info.get('trailingPegRatio', None)
            
            pe_good = pe_ratio is not None and pe_ratio < 25
            peg_good = peg_ratio is not None and peg_ratio < 1
            check1_pass = pe_good or peg_good
            
            pe_text = f"PE: {pe_ratio:.2f}" if pe_ratio else "PE: N/A"
            peg_text = f"PEG: {peg_ratio:.2f}" if peg_ratio else "PEG: N/A"
            results.append((f"1. Valuation ({pe_text}, {peg_text})", check1_pass))
            
            # 2. Revenue Trend (5 years)
            check2_pass = False
            if not financials.empty and 'Total Revenue' in financials.index:
                revenue_data = financials.loc['Total Revenue'].sort_index()
                check2_pass = self.check_trend_with_regression(revenue_data, increasing=True)
            results.append(("2. Revenue Growth Trend", check2_pass))
            
            # 3. Operating Income Trend
            check3_pass = False
            if not financials.empty and 'Operating Income' in financials.index:
                op_income_data = financials.loc['Operating Income'].sort_index()
                check3_pass = self.check_trend_with_regression(op_income_data, increasing=True)
            results.append(("3. Operating Income Growth Trend", check3_pass))
            
            # 4. Net Income Trend
            check4_pass = False
            if not financials.empty and 'Net Income' in financials.index:
                net_income_data = financials.loc['Net Income'].sort_index()
                check4_pass = self.check_trend_with_regression(net_income_data, increasing=True)
            results.append(("4. Net Income Growth Trend", check4_pass))
            
            # 5. Current Assets vs Current Liabilities
            check5_pass = False
            if not balance_sheet.empty:
                latest_bs = balance_sheet.iloc[:, 0]
                current_assets = latest_bs.get('Current Assets', None)
                current_liabilities = latest_bs.get('Current Liabilities', None)
                if current_assets is not None and current_liabilities is not None:
                    check5_pass = current_assets > current_liabilities
            results.append(("5. Current Assets > Current Liabilities", check5_pass))
            
            # 6. Long-term Debt to Net Profit Ratio
            check6_pass = False
            if not balance_sheet.empty and not financials.empty:
                latest_bs = balance_sheet.iloc[:, 0]
                long_term_debt = latest_bs.get('Long Term Debt', None)
                if 'Net Income' in financials.index:
                    latest_net_income = financials.loc['Net Income'].iloc[0]
                    if (long_term_debt is not None and latest_net_income is not None and 
                        latest_net_income > 0):
                        debt_ratio = long_term_debt / latest_net_income
                        check6_pass = debt_ratio < 4
            results.append(("6. Long-term Debt/Net Profit < 4", check6_pass))
            
            # 7. Equity Trend
            check7_pass = False
            if not balance_sheet.empty and 'Stockholders Equity' in balance_sheet.index:
                equity_data = balance_sheet.loc['Stockholders Equity'].sort_index()
                check7_pass = self.check_trend_with_regression(equity_data, increasing=True)
            results.append(("7. Stockholders' Equity Growth Trend", check7_pass))
            
            # 8. Shares Outstanding Trend (decreasing is good)
            check8_pass = False
            if not balance_sheet.empty and 'Ordinary Shares Number' in balance_sheet.index:
                shares_data = balance_sheet.loc['Ordinary Shares Number'].sort_index()
                check8_pass = self.check_trend_with_regression(shares_data, increasing=False)
            results.append(("8. Shares Outstanding Decreasing Trend", check8_pass))
            
            # 9. Cash Flow Comparison
            check9_pass = False
            if not cashflow.empty:
                latest_cf = cashflow.iloc[:, 0]
                operating_cf = latest_cf.get('Operating Cash Flow', None)
                investing_cf = latest_cf.get('Investing Cash Flow', None)
                financing_cf = latest_cf.get('Financing Cash Flow', None)
                
                op_vs_inv = (operating_cf is not None and investing_cf is not None and 
                           operating_cf > abs(investing_cf))
                op_vs_fin = (operating_cf is not None and financing_cf is not None and 
                           operating_cf > abs(financing_cf))
                check9_pass = op_vs_inv and op_vs_fin
            results.append(("9. Operating CF > Investing & Financing CF", check9_pass))
            
            # 10. Free Cash Flow Trend
            check10_pass = False
            if not cashflow.empty:
                if 'Free Cash Flow' in cashflow.index:
                    fcf_data = cashflow.loc['Free Cash Flow'].sort_index()
                    check10_pass = self.check_trend_with_regression(fcf_data, increasing=True)
                elif ('Operating Cash Flow' in cashflow.index and 
                      'Capital Expenditures' in cashflow.index):
                    operating_cf = cashflow.loc['Operating Cash Flow']
                    capex = cashflow.loc['Capital Expenditures']
                    fcf_calculated = operating_cf + capex  # capex is usually negative
                    check10_pass = self.check_trend_with_regression(fcf_calculated, increasing=True)
            results.append(("10. Free Cash Flow Growth Trend", check10_pass))
            
            # Display results
            self.display_results(results)
            
            return results
            
        except Exception as e:
            print(f"Error analyzing {ticker}: {str(e)}")
            return []
    
    def display_results(self, results):
        """Display the analysis results with tick/cross symbols"""
        
        print(f"\n{'FINANCIAL HEALTH CHECK RESULTS':^80}")
        print("="*80)
        
        # Display each result
        for i, (description, passed) in enumerate(results):
            # Symbol (✓ or ✗)
            symbol = "✓" if passed else "✗"
            status = "PASS" if passed else "FAIL"
            
            print(f"{symbol} {description:<60} [{status:>6}]")
        
        # Summary
        passed_count = sum(1 for _, passed in results if passed)
        total_count = len(results)
        percentage = (passed_count/total_count*100) if total_count > 0 else 0
        
        print("="*80)
        print(f"FINANCIAL HEALTH SCORE: {passed_count}/{total_count} ({percentage:.1f}%)")
        
        # Health assessment
        if percentage >= 80:
            assessment = "EXCELLENT - Strong financial health"
        elif percentage >= 60:
            assessment = "GOOD - Solid financial position"
        elif percentage >= 40:
            assessment = "FAIR - Some concerns present"
        else:
            assessment = "POOR - Significant financial risks"
            
        print(f"ASSESSMENT: {assessment}")
        print("="*80)

def run_financial_health_checker():
    """Main function to run the financial health checker"""
    checker = FinancialHealthChecker()
    
    print("Welcome to the Financial Health Checker!")
    print("This tool analyzes 10 key financial metrics to assess stock health.")
    
    while True:
        ticker = input("\nEnter a stock ticker symbol (or 'quit' to exit): ").strip().upper()
        
        if ticker.lower() == 'quit':
            print("Thank you for using the Financial Health Checker!")
            break
        
        if not ticker:
            print("Please enter a valid ticker symbol.")
            continue
            
        print(f"\nAnalyzing {ticker}...")
        checker.analyze_stock(ticker)
        
        continue_analysis = input("\nWould you like to analyze another stock? (y/n): ").strip().lower()
        if continue_analysis not in ['y', 'yes']:
            print("Thank you for using the Financial Health Checker!")
            break

if __name__ == "__main__":
    run_financial_health_checker()
