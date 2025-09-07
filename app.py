from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

class FinancialHealthChecker:
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
            
            # Check if we got valid data
            if not info or len(info) < 5:
                raise ValueError(f"No data found for ticker {ticker}")
                
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            cashflow = stock.cashflow
            
            # Analysis results
            checks = []
            
            # 1. PE/PEG Ratio Check
            pe_ratio = info.get('trailingPE', None)
            peg_ratio = info.get('trailingPegRatio', None)
            
            pe_good = pe_ratio is not None and pe_ratio < 25
            peg_good = peg_ratio is not None and peg_ratio < 1
            check1_pass = pe_good or peg_good
            
            pe_text = f"PE: {pe_ratio:.2f}" if pe_ratio else "PE: N/A"
            peg_text = f"PEG: {peg_ratio:.2f}" if peg_ratio else "PEG: N/A"
            checks.append({
                'id': 1,
                'name': 'P/E < 25 || PEG < 1.0',
                'description': 'Valuation metrics',
                'passed': bool(check1_pass),
                'details': f'{pe_text}, {peg_text}'
            })
            
            # 2. Revenue Trend (5 years)
            check2_pass = False
            revenue_details = "No data available"
            if not financials.empty and 'Total Revenue' in financials.index:
                revenue_data = financials.loc['Total Revenue'].sort_index()
                check2_pass = self.check_trend_with_regression(revenue_data, increasing=True)
                revenue_details = "Positive trend detected" if check2_pass else "No clear growth trend"
            checks.append({
                'id': 2,
                'name': 'Revenue Growth',
                'description': '5-year increasing trend',
                'passed': bool(check2_pass),
                'details': revenue_details
            })
            
            # 3. Operating Income Trend
            check3_pass = False
            op_details = "No data available"
            if not financials.empty and 'Operating Income' in financials.index:
                op_income_data = financials.loc['Operating Income'].sort_index()
                check3_pass = self.check_trend_with_regression(op_income_data, increasing=True)
                op_details = "Consistent growth pattern" if check3_pass else "Declining or flat trend"
            checks.append({
                'id': 3,
                'name': 'Operating Income Growth',
                'description': '5-year increasing trend',
                'passed': bool(check3_pass),
                'details': op_details
            })
            
            # 4. Net Income Trend
            check4_pass = False
            net_details = "No data available"
            if not financials.empty and 'Net Income' in financials.index:
                net_income_data = financials.loc['Net Income'].sort_index()
                check4_pass = self.check_trend_with_regression(net_income_data, increasing=True)
                net_details = "Strong profitability trend" if check4_pass else "Declining profitability"
            checks.append({
                'id': 4,
                'name': 'Net Income Growth',
                'description': '5-year increasing trend',
                'passed': bool(check4_pass),
                'details': net_details
            })
            
            # 5. Current Assets vs Current Liabilities
            check5_pass = False
            liquidity_details = "No data available"
            if not balance_sheet.empty:
                latest_bs = balance_sheet.iloc[:, 0]
                current_assets = latest_bs.get('Current Assets', None)
                current_liabilities = latest_bs.get('Current Liabilities', None)
                if current_assets is not None and current_liabilities is not None:
                    check5_pass = current_assets > current_liabilities
                    ratio = current_assets / current_liabilities
                    liquidity_details = f"Current ratio: {ratio:.2f}" if check5_pass else f"Poor liquidity - ratio: {ratio:.2f}"
                else:
                    liquidity_details = "Balance sheet data incomplete"
            checks.append({
                'id': 5,
                'name': 'Current Assets > Current Liabilities',
                'description': 'Liquidity position',
                'passed': bool(check5_pass),
                'details': liquidity_details
            })
            
            # 6. Long-term Debt to Net Profit Ratio
            check6_pass = False
            debt_details = "No data available"
            if not balance_sheet.empty and not financials.empty:
                latest_bs = balance_sheet.iloc[:, 0]
                long_term_debt = latest_bs.get('Long Term Debt', None)
                if 'Net Income' in financials.index:
                    latest_net_income = financials.loc['Net Income'].iloc[0]
                    if (long_term_debt is not None and latest_net_income is not None and 
                        latest_net_income > 0):
                        debt_ratio = long_term_debt / latest_net_income
                        check6_pass = debt_ratio < 4
                        debt_details = f"Debt/Profit ratio: {debt_ratio:.2f}" if check6_pass else f"High debt ratio: {debt_ratio:.2f}"
                    else:
                        debt_details = "Insufficient data for calculation"
            checks.append({
                'id': 6,
                'name': 'Long-term Debt/Net Profit < 4',
                'description': 'Debt management',
                'passed': bool(check6_pass),
                'details': debt_details
            })
            
            # 7. Equity Trend
            check7_pass = False
            equity_details = "No data available"
            if not balance_sheet.empty and 'Stockholders Equity' in balance_sheet.index:
                equity_data = balance_sheet.loc['Stockholders Equity'].sort_index()
                check7_pass = self.check_trend_with_regression(equity_data, increasing=True)
                equity_details = "Growing shareholder value" if check7_pass else "Declining equity trend"
            checks.append({
                'id': 7,
                'name': 'Stockholders\' Equity Growth',
                'description': '5-year increasing trend',
                'passed': bool(check7_pass),
                'details': equity_details
            })
            
            # 8. Shares Outstanding Trend (decreasing is good)
            check8_pass = False
            shares_details = "No data available"
            if not balance_sheet.empty and 'Ordinary Shares Number' in balance_sheet.index:
                shares_data = balance_sheet.loc['Ordinary Shares Number'].sort_index()
                check8_pass = self.check_trend_with_regression(shares_data, increasing=False)
                shares_details = "Active share repurchase program" if check8_pass else "No significant buyback activity"
            checks.append({
                'id': 8,
                'name': 'Shares Outstanding Decreasing',
                'description': 'Share buyback trend',
                'passed': bool(check8_pass),
                'details': shares_details
            })
            
            # 9. Cash Flow Comparison
            check9_pass = False
            cf_details = "No data available"
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
                cf_details = "Strong operational cash generation" if check9_pass else "Weak cash flow position"
            checks.append({
                'id': 9,
                'name': 'Operating CF > Investing & Financing CF',
                'description': 'Cash flow strength',
                'passed': bool(check9_pass),
                'details': cf_details
            })
            
            # 10. Free Cash Flow Trend
            check10_pass = False
            fcf_details = "No data available"
            if not cashflow.empty:
                if 'Free Cash Flow' in cashflow.index:
                    fcf_data = cashflow.loc['Free Cash Flow'].sort_index()
                    check10_pass = self.check_trend_with_regression(fcf_data, increasing=True)
                    fcf_details = "Consistent FCF improvement" if check10_pass else "Declining free cash flow"
                elif ('Operating Cash Flow' in cashflow.index and 
                      'Capital Expenditures' in cashflow.index):
                    operating_cf = cashflow.loc['Operating Cash Flow']
                    capex = cashflow.loc['Capital Expenditures']
                    fcf_calculated = operating_cf + capex  # capex is usually negative
                    check10_pass = self.check_trend_with_regression(fcf_calculated, increasing=True)
                    fcf_details = "Improving calculated FCF" if check10_pass else "Declining calculated FCF"
            checks.append({
                'id': 10,
                'name': 'Free Cash Flow Growth',
                'description': '5-year increasing trend',
                'passed': bool(check10_pass),
                'details': fcf_details
            })
            
            # Generate detailed analysis text
            detailed_analysis = self.generate_detailed_analysis(ticker, info, financials, balance_sheet, cashflow)
            
            return {
                'success': True,
                'checks': checks,
                'detailedAnalysis': detailed_analysis
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_detailed_analysis(self, ticker, info, financials, balance_sheet, cashflow):
        """Generate detailed financial analysis text"""
        analysis = f"STOCK ANALYSIS FOR {ticker}\n"
        analysis += "=" * 60 + "\n\n"
        
        # PE/PEG ratios
        pe_ratio = info.get('trailingPE', 'N/A')
        peg_ratio = info.get('trailingPegRatio', 'N/A')
        analysis += f"1. Latest PE Ratio: {pe_ratio}\n"
        analysis += f"   PEG Ratio: {peg_ratio}\n\n"
        
        # Revenue
        analysis += "2. Revenue for the past 5 years:\n"
        if not financials.empty and 'Total Revenue' in financials.index:
            revenue_data = financials.loc['Total Revenue'].sort_index()
            for date, value in revenue_data.items():
                if pd.notna(value):
                    analysis += f"   {date.year}: ${value:,.0f}\n"
        else:
            analysis += "   Revenue data not available\n"
        analysis += "\n"
        
        # Operating Income
        analysis += "3. Operating Income for the past 5 years:\n"
        if not financials.empty and 'Operating Income' in financials.index:
            operating_income = financials.loc['Operating Income'].sort_index()
            for date, value in operating_income.items():
                if pd.notna(value):
                    analysis += f"   {date.year}: ${value:,.0f}\n"
        else:
            analysis += "   Operating Income data not available\n"
        analysis += "\n"
        
        # Net Income
        analysis += "4. Net Income for the past 5 years:\n"
        if not financials.empty and 'Net Income' in financials.index:
            net_income = financials.loc['Net Income'].sort_index()
            for date, value in net_income.items():
                if pd.notna(value):
                    analysis += f"   {date.year}: ${value:,.0f}\n"
        else:
            analysis += "   Net Income data not available\n"
        analysis += "\n"
        
        # Current Assets and Liabilities
        analysis += "5. Latest Current Assets and Current Liabilities:\n"
        if not balance_sheet.empty:
            latest_bs = balance_sheet.iloc[:, 0]
            current_assets = latest_bs.get('Current Assets', 'N/A')
            current_liabilities = latest_bs.get('Current Liabilities', 'N/A')
            
            if current_assets != 'N/A':
                analysis += f"   Current Assets: ${current_assets:,.0f}\n"
            else:
                analysis += "   Current Assets: N/A\n"
                
            if current_liabilities != 'N/A':
                analysis += f"   Current Liabilities: ${current_liabilities:,.0f}\n"
            else:
                analysis += "   Current Liabilities: N/A\n"
        else:
            analysis += "   Balance sheet data not available\n"
        analysis += "\n"
        
        # Long-term Debt
        analysis += "6. Latest Long Term Debt:\n"
        if not balance_sheet.empty:
            latest_bs = balance_sheet.iloc[:, 0]
            long_term_debt = latest_bs.get('Long Term Debt', 'N/A')
            if long_term_debt != 'N/A':
                analysis += f"   ${long_term_debt:,.0f}\n"
            else:
                analysis += "   N/A\n"
        else:
            analysis += "   Balance sheet data not available\n"
        analysis += "\n"
        
        # Stockholders' Equity
        analysis += "7. Stockholders' Equity for the past 5 years:\n"
        if not balance_sheet.empty and 'Stockholders Equity' in balance_sheet.index:
            equity_data = balance_sheet.loc['Stockholders Equity'].sort_index()
            for date, value in equity_data.items():
                if pd.notna(value):
                    analysis += f"   {date.year}: ${value:,.0f}\n"
        else:
            analysis += "   Stockholders' Equity data not available\n"
        analysis += "\n"
        
        # Shares Outstanding
        analysis += "8. Shares Outstanding for the past 5 years:\n"
        shares_outstanding = info.get('sharesOutstanding', 'N/A')
        if shares_outstanding != 'N/A':
            analysis += f"   Latest: {shares_outstanding:,.0f}\n"
        else:
            analysis += "   Current shares outstanding not available\n"
        
        # Try to get historical shares data from balance sheet
        if not balance_sheet.empty and 'Ordinary Shares Number' in balance_sheet.index:
            shares_data = balance_sheet.loc['Ordinary Shares Number'].sort_index()
            for date, value in shares_data.items():
                if pd.notna(value):
                    analysis += f"   {date.year}: {value:,.0f}\n"
        analysis += "\n"
        
        # Latest Cash Flow Data
        analysis += "9. Latest Cash Flow Data:\n"
        if not cashflow.empty:
            latest_cf = cashflow.iloc[:, 0]
            
            operating_cf = latest_cf.get('Operating Cash Flow', 'N/A')
            investing_cf = latest_cf.get('Investing Cash Flow', 'N/A')
            financing_cf = latest_cf.get('Financing Cash Flow', 'N/A')
            
            if operating_cf != 'N/A':
                analysis += f"   Operating Cash Flow: ${operating_cf:,.0f}\n"
            else:
                analysis += "   Operating Cash Flow: N/A\n"
                
            if investing_cf != 'N/A':
                analysis += f"   Investing Cash Flow: ${investing_cf:,.0f}\n"
            else:
                analysis += "   Investing Cash Flow: N/A\n"
                
            if financing_cf != 'N/A':
                analysis += f"   Financing Cash Flow: ${financing_cf:,.0f}\n"
            else:
                analysis += "   Financing Cash Flow: N/A\n"
        else:
            analysis += "   Cash flow data not available\n"
        analysis += "\n"
        
        # Free Cash Flow
        analysis += "10. Free Cash Flow for the past 5 years:\n"
        if not cashflow.empty:
            if 'Free Cash Flow' in cashflow.index:
                fcf_data = cashflow.loc['Free Cash Flow'].sort_index()
                for date, value in fcf_data.items():
                    if pd.notna(value):
                        analysis += f"    {date.year}: ${value:,.0f}\n"
            else:
                # Calculate FCF = Operating Cash Flow - Capital Expenditures
                if 'Operating Cash Flow' in cashflow.index and 'Capital Expenditures' in cashflow.index:
                    operating_cf = cashflow.loc['Operating Cash Flow']
                    capex = cashflow.loc['Capital Expenditures']
                    fcf_calculated = operating_cf + capex  # capex is usually negative
                    fcf_sorted = fcf_calculated.sort_index()
                    analysis += "    (Calculated as Operating Cash Flow - Capital Expenditures)\n"
                    for date, value in fcf_sorted.items():
                        if pd.notna(value):
                            analysis += f"    {date.year}: ${value:,.0f}\n"
                else:
                    analysis += "    Free Cash Flow data not available\n"
        else:
            analysis += "    Cash flow data not available\n"
        analysis += "\n"
        
        return analysis

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze/<ticker>')
def analyze_stock(ticker):
    try:
        checker = FinancialHealthChecker()
        result = checker.analyze_stock(ticker.upper())
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
