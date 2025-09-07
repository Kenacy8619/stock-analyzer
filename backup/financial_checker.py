import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import tkinter as tk
from tkinter import ttk, messagebox
import warnings
warnings.filterwarnings('ignore')

class FinancialHealthChecker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stock Financial Health Checker")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Stock Financial Health Checker", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input section
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, columnspan=3, pady=(0, 20), sticky=(tk.W, tk.E))
        
        ttk.Label(input_frame, text="Enter Stock Ticker:").grid(row=0, column=0, padx=(0, 10))
        self.ticker_entry = ttk.Entry(input_frame, width=15)
        self.ticker_entry.grid(row=0, column=1, padx=(0, 10))
        
        analyze_btn = ttk.Button(input_frame, text="Analyze", command=self.analyze_stock)
        analyze_btn.grid(row=0, column=2)
        
        # Results frame
        self.results_frame = ttk.Frame(main_frame)
        self.results_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
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
    
    def analyze_stock(self):
        ticker = self.ticker_entry.get().strip().upper()
        if not ticker:
            messagebox.showerror("Error", "Please enter a ticker symbol")
            return
            
        try:
            # Clear previous results
            for widget in self.results_frame.winfo_children():
                widget.destroy()
                
            # Create loading label
            loading_label = ttk.Label(self.results_frame, text=f"Analyzing {ticker}...", 
                                    font=('Arial', 12))
            loading_label.grid(row=0, column=0, pady=20)
            self.root.update()
            
            # Get stock data
            stock = yf.Ticker(ticker)
            info = stock.info
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            cashflow = stock.cashflow
            
            # Remove loading label
            loading_label.destroy()
            
            # Create results header
            header_label = ttk.Label(self.results_frame, text=f"Financial Health Analysis for {ticker}", 
                                   font=('Arial', 14, 'bold'))
            header_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
            
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
            
        except Exception as e:
            messagebox.showerror("Error", f"Error analyzing {ticker}: {str(e)}")
    
    def display_results(self, results):
        """Display the analysis results with tick/cross symbols"""
        
        # Create canvas and scrollbar for results
        canvas = tk.Canvas(self.results_frame, bg='white')
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Display each result
        for i, (description, passed) in enumerate(results):
            # Create frame for each result
            result_frame = ttk.Frame(scrollable_frame)
            result_frame.grid(row=i+1, column=0, sticky=(tk.W, tk.E), pady=5, padx=10)
            
            # Symbol (✓ or ✗)
            symbol = "✓" if passed else "✗"
            color = "green" if passed else "red"
            
            symbol_label = tk.Label(result_frame, text=symbol, font=('Arial', 20, 'bold'), 
                                  fg=color, bg='white')
            symbol_label.grid(row=0, column=0, padx=(0, 15))
            
            # Description
            desc_label = tk.Label(result_frame, text=description, font=('Arial', 11), 
                                bg='white', anchor='w')
            desc_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
            
            result_frame.columnconfigure(1, weight=1)
        
        # Summary
        passed_count = sum(1 for _, passed in results if passed)
        total_count = len(results)
        
        summary_frame = ttk.Frame(scrollable_frame)
        summary_frame.grid(row=len(results)+2, column=0, sticky=(tk.W, tk.E), pady=20, padx=10)
        
        summary_text = f"Financial Health Score: {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)"
        summary_label = ttk.Label(summary_frame, text=summary_text, font=('Arial', 12, 'bold'))
        summary_label.grid(row=0, column=0)
        
        # Pack canvas and scrollbar
        canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.rowconfigure(1, weight=1)
        scrollable_frame.columnconfigure(0, weight=1)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FinancialHealthChecker()
    app.run()
