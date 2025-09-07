# Stock Financial Analyzer

A comprehensive Python tool for analyzing stock financial data using Yahoo Finance.

## Features

This tool retrieves and displays the following financial information for any stock ticker:

1. **Latest PE Ratio** - Price-to-Earnings ratio
2. **Revenue** - Total revenue for the past 5 years
3. **Operating Income** - Operating income for the past 5 years
4. **Net Income** - Net income for the past 5 years
5. **Current Assets & Liabilities** - Latest balance sheet data
6. **Long Term Debt** - Latest long-term debt information
7. **Stockholders' Equity** - Equity data for the past 5 years
8. **Shares Outstanding** - Share count data for the past 5 years
9. **Cash Flow Data** - Latest operating, investing, and financing cash flows
10. **Free Cash Flow** - Free cash flow for the past 5 years

## Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

Enter any valid stock ticker symbol (e.g., AAPL, MSFT, GOOGL) when prompted.

## Example

```
Enter a stock ticker symbol (or 'quit' to exit): AAPL
```

The tool will display comprehensive financial analysis for Apple Inc.

## Dependencies

- yfinance: For retrieving Yahoo Finance data
- pandas: For data manipulation and analysis

## Notes

- Data availability may vary depending on the company and reporting standards
- Some financial metrics may not be available for all companies
- The tool handles missing data gracefully with appropriate error messages
