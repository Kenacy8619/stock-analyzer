import yfinance as yf
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def get_stock_analysis(ticker):
    """
    Comprehensive stock analysis function that retrieves financial data for a given ticker
    """
    try:
        # Create ticker object
        stock = yf.Ticker(ticker)
        
        # Get stock info
        info = stock.info
        
        print(f"\n{'='*60}")
        print(f"STOCK ANALYSIS FOR {ticker.upper()}")
        print(f"{'='*60}")
        
        # 1. Latest PE Ratio
        pe_ratio = info.get('trailingPE', 'N/A')
        print(f"\n1. Latest PE Ratio: {pe_ratio}")
        
        # Get financial statements
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        cashflow = stock.cashflow
        
        # 2. Revenue for the past 5 years
        print(f"\n2. Revenue for the past 5 years:")
        if not financials.empty and 'Total Revenue' in financials.index:
            revenue_data = financials.loc['Total Revenue'].sort_index()
            for date, value in revenue_data.items():
                if pd.notna(value):
                    print(f"   {date.year}: ${value:,.0f}")
        else:
            print("   Revenue data not available")
        
        # 3. Operating Income for the past 5 years
        print(f"\n3. Operating Income for the past 5 years:")
        if not financials.empty and 'Operating Income' in financials.index:
            operating_income = financials.loc['Operating Income'].sort_index()
            for date, value in operating_income.items():
                if pd.notna(value):
                    print(f"   {date.year}: ${value:,.0f}")
        else:
            print("   Operating Income data not available")
        
        # 4. Net Income for the past 5 years
        print(f"\n4. Net Income for the past 5 years:")
        if not financials.empty and 'Net Income' in financials.index:
            net_income = financials.loc['Net Income'].sort_index()
            for date, value in net_income.items():
                if pd.notna(value):
                    print(f"   {date.year}: ${value:,.0f}")
        else:
            print("   Net Income data not available")
        
        # 5. Latest Current Assets and Current Liabilities
        print(f"\n5. Latest Current Assets and Current Liabilities:")
        if not balance_sheet.empty:
            latest_bs = balance_sheet.iloc[:, 0]  # Most recent column
            current_assets = latest_bs.get('Current Assets', 'N/A')
            current_liabilities = latest_bs.get('Current Liabilities', 'N/A')
            
            if current_assets != 'N/A':
                print(f"   Current Assets: ${current_assets:,.0f}")
            else:
                print("   Current Assets: N/A")
                
            if current_liabilities != 'N/A':
                print(f"   Current Liabilities: ${current_liabilities:,.0f}")
            else:
                print("   Current Liabilities: N/A")
        else:
            print("   Balance sheet data not available")
        
        # 6. Latest Long Term Debt
        print(f"\n6. Latest Long Term Debt:")
        if not balance_sheet.empty:
            latest_bs = balance_sheet.iloc[:, 0]
            long_term_debt = latest_bs.get('Long Term Debt', 'N/A')
            if long_term_debt != 'N/A':
                print(f"   ${long_term_debt:,.0f}")
            else:
                print("   N/A")
        else:
            print("   Balance sheet data not available")
        
        # 7. Equity for the past 5 years
        print(f"\n7. Stockholders' Equity for the past 5 years:")
        if not balance_sheet.empty and 'Stockholders Equity' in balance_sheet.index:
            equity_data = balance_sheet.loc['Stockholders Equity'].sort_index()
            for date, value in equity_data.items():
                if pd.notna(value):
                    print(f"   {date.year}: ${value:,.0f}")
        else:
            print("   Stockholders' Equity data not available")
        
        # 8. Shares Outstanding for the past 5 years
        print(f"\n8. Shares Outstanding for the past 5 years:")
        shares_outstanding = info.get('sharesOutstanding', 'N/A')
        if shares_outstanding != 'N/A':
            print(f"   Latest: {shares_outstanding:,.0f}")
        else:
            print("   Current shares outstanding not available")
        
        # Try to get historical shares data from balance sheet
        if not balance_sheet.empty and 'Ordinary Shares Number' in balance_sheet.index:
            shares_data = balance_sheet.loc['Ordinary Shares Number'].sort_index()
            for date, value in shares_data.items():
                if pd.notna(value):
                    print(f"   {date.year}: {value:,.0f}")
        
        # 9. Latest Cash Flow Data
        print(f"\n9. Latest Cash Flow Data:")
        if not cashflow.empty:
            latest_cf = cashflow.iloc[:, 0]  # Most recent column
            
            operating_cf = latest_cf.get('Operating Cash Flow', 'N/A')
            investing_cf = latest_cf.get('Investing Cash Flow', 'N/A')
            financing_cf = latest_cf.get('Financing Cash Flow', 'N/A')
            
            if operating_cf != 'N/A':
                print(f"   Operating Cash Flow: ${operating_cf:,.0f}")
            else:
                print("   Operating Cash Flow: N/A")
                
            if investing_cf != 'N/A':
                print(f"   Investing Cash Flow: ${investing_cf:,.0f}")
            else:
                print("   Investing Cash Flow: N/A")
                
            if financing_cf != 'N/A':
                print(f"   Financing Cash Flow: ${financing_cf:,.0f}")
            else:
                print("   Financing Cash Flow: N/A")
        else:
            print("   Cash flow data not available")
        
        # 10. Free Cash Flow for the past 5 years
        print(f"\n10. Free Cash Flow for the past 5 years:")
        if not cashflow.empty:
            if 'Free Cash Flow' in cashflow.index:
                fcf_data = cashflow.loc['Free Cash Flow'].sort_index()
                for date, value in fcf_data.items():
                    if pd.notna(value):
                        print(f"    {date.year}: ${value:,.0f}")
            else:
                # Calculate FCF = Operating Cash Flow - Capital Expenditures
                if 'Operating Cash Flow' in cashflow.index and 'Capital Expenditures' in cashflow.index:
                    operating_cf = cashflow.loc['Operating Cash Flow']
                    capex = cashflow.loc['Capital Expenditures']
                    fcf_calculated = operating_cf + capex  # capex is usually negative
                    fcf_sorted = fcf_calculated.sort_index()
                    print("    (Calculated as Operating Cash Flow - Capital Expenditures)")
                    for date, value in fcf_sorted.items():
                        if pd.notna(value):
                            print(f"    {date.year}: ${value:,.0f}")
                else:
                    print("    Free Cash Flow data not available")
        else:
            print("    Cash flow data not available")
            
        print(f"\n{'='*60}")
        
    except Exception as e:
        print(f"Error retrieving data for {ticker}: {str(e)}")
        print("Please check if the ticker symbol is correct and try again.")

def main():
    """
    Main function to run the stock analyzer
    """
    print("Welcome to the Stock Financial Analyzer!")
    print("This tool provides comprehensive financial analysis for any stock ticker.")
    
    while True:
        ticker = input("\nEnter a stock ticker symbol (or 'quit' to exit): ").strip().upper()
        
        if ticker.lower() == 'quit':
            print("Thank you for using the Stock Financial Analyzer!")
            break
        
        if not ticker:
            print("Please enter a valid ticker symbol.")
            continue
            
        get_stock_analysis(ticker)
        
        continue_analysis = input("\nWould you like to analyze another stock? (y/n): ").strip().lower()
        if continue_analysis not in ['y', 'yes']:
            print("Thank you for using the Stock Financial Analyzer!")
            break

if __name__ == "__main__":
    main()