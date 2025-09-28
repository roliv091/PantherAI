import pandas as pd
import numpy as np
import PyPDF2
import re
from typing import Dict, Any, List
from datetime import datetime
import io

# In-memory storage for finance data
_finance_df = None

def ingest_csv(csv_bytes: bytes) -> Dict[str, Any]:
    """Ingest CSV file and normalize data"""
    global _finance_df
    
    try:
        # Read CSV
        df = pd.read_csv(io.BytesIO(csv_bytes))
        
        # Normalize column names
        df.columns = df.columns.str.lower().str.strip()
        
        # Try to identify columns
        date_col = None
        desc_col = None
        amount_col = None
        
        for col in df.columns:
            if 'date' in col or 'time' in col:
                date_col = col
            elif 'desc' in col or 'memo' in col or 'note' in col:
                desc_col = col
            elif 'amount' in col or 'value' in col or 'total' in col:
                amount_col = col
        
        # If we can't identify columns, use first three
        if not all([date_col, desc_col, amount_col]):
            cols = df.columns.tolist()
            date_col = cols[0] if len(cols) > 0 else None
            desc_col = cols[1] if len(cols) > 1 else None
            amount_col = cols[2] if len(cols) > 2 else None
        
        # Normalize data
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        if amount_col:
            df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce')
        
        # Store normalized dataframe
        _finance_df = df
        
        return {
            "ok": True,
            "rows": len(df),
            "columns": df.columns.tolist()
        }
        
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }

def metrics() -> Dict[str, Any]:
    """Calculate finance metrics from stored data"""
    global _finance_df
    
    if _finance_df is None:
        return {
            "ok": False,
            "error": "No finance data available"
        }
    
    try:
        df = _finance_df.copy()
        
        # Get amount column
        amount_col = None
        for col in df.columns:
            if 'amount' in col or 'value' in col or 'total' in col:
                amount_col = col
                break
        
        if not amount_col:
            amount_col = df.columns[2] if len(df.columns) > 2 else df.columns[0]
        
        # Calculate totals by category (using description)
        desc_col = None
        for col in df.columns:
            if 'desc' in col or 'memo' in col or 'note' in col:
                desc_col = col
                break
        
        if not desc_col:
            desc_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        # Group by description and sum amounts
        totals = df.groupby(desc_col)[amount_col].sum().to_dict()
        
        # Calculate roundups (ceil difference for debits)
        debits = df[df[amount_col] < 0][amount_col].sum()
        credits = df[df[amount_col] > 0][amount_col].sum()
        roundups = abs(debits) - abs(credits)
        roundups = max(0, roundups)  # Only positive roundups
        
        # Simple runway calculation (assuming monthly expenses)
        monthly_expenses = abs(debits) / 12  # Rough estimate
        current_balance = credits + debits
        runway_days = (current_balance / monthly_expenses * 30) if monthly_expenses > 0 else 0
        
        return {
            "ok": True,
            "totals": totals,
            "roundups": roundups,
            "runway_days": int(runway_days)
        }
        
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }

def ingest_pdf(file_path: str) -> Dict[str, Any]:
    """Ingest PDF statement and extract transactions"""
    global _finance_df
    
    try:
        # Extract text from PDF
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        # Parse transactions from text
        transactions = extract_transactions_from_text(text)
        
        if not transactions:
            return {
                "ok": False,
                "error": "No transactions found in PDF"
            }
        
        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        
        # Normalize data
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # Store normalized dataframe
        _finance_df = df
        
        return {
            "ok": True,
            "rows": len(df),
            "columns": df.columns.tolist()
        }
        
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }

def extract_transactions_from_text(text: str) -> List[Dict[str, Any]]:
    """Extract transactions from bank statement text using regex patterns"""
    transactions = []
    
    # Common bank statement patterns
    patterns = [
        # Pattern 1: Date Description Amount (most common)
        # Example: "01/15/2024 STARBUCKS COFFEE -$5.50"
        r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\s+([A-Za-z0-9\s\*\#\-\&\.]+?)\s+[\$\-\+]?([\d,]+\.?\d{0,2})',
        
        # Pattern 2: Date Amount Description
        # Example: "01/15/2024 -$5.50 STARBUCKS COFFEE"
        r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\s+[\$\-\+]?([\d,]+\.?\d{0,2})\s+([A-Za-z0-9\s\*\#\-\&\.]+)',
        
        # Pattern 3: Month Day Description Amount
        # Example: "JAN 15 STARBUCKS COFFEE -$5.50"
        r'([A-Z]{3}\s+\d{1,2})\s+([A-Za-z0-9\s\*\#\-\&\.]+?)\s+[\$\-\+]?([\d,]+\.?\d{0,2})',
        
        # Pattern 4: More flexible date formats
        # Example: "2024-01-15 STARBUCKS COFFEE $5.50"
        r'(\d{4}[\-\/]\d{1,2}[\-\/]\d{1,2})\s+([A-Za-z0-9\s\*\#\-\&\.]+?)\s+[\$\-\+]?([\d,]+\.?\d{0,2})',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        
        for match in matches:
            groups = match.groups()
            
            if len(groups) >= 3:
                date_str = groups[0].strip()
                
                # Determine which group is description and which is amount
                if pattern == patterns[1]:  # Date Amount Description pattern
                    amount_str = groups[1].strip()
                    desc_str = groups[2].strip()
                else:  # Date Description Amount pattern
                    desc_str = groups[1].strip()
                    amount_str = groups[2].strip()
                
                # Clean up description (remove extra spaces, special chars)
                desc_str = re.sub(r'\s+', ' ', desc_str).strip()
                desc_str = re.sub(r'[*#]+', '', desc_str).strip()
                
                # Skip if description is too short or seems invalid
                if len(desc_str) < 3 or desc_str.isdigit():
                    continue
                
                # Parse date
                parsed_date = parse_statement_date(date_str)
                if not parsed_date:
                    continue
                
                # Parse amount
                amount_str = amount_str.replace(',', '').replace('$', '').strip()
                try:
                    amount = float(amount_str)
                    
                    # Determine if it's debit or credit based on context
                    # Look for negative indicators in the original text around this match
                    match_start = match.start()
                    match_end = match.end()
                    context = text[max(0, match_start-20):min(len(text), match_end+20)]
                    
                    # Check for debit indicators
                    if any(indicator in context.lower() for indicator in ['-', 'debit', 'withdrawal', 'purchase', 'fee']):
                        amount = -abs(amount)
                    elif any(indicator in context.lower() for indicator in ['credit', 'deposit', 'payment received', 'refund']):
                        amount = abs(amount)
                    else:
                        # If no clear indicator, assume purchases are negative
                        if any(keyword in desc_str.lower() for keyword in ['coffee', 'gas', 'grocery', 'uber', 'amazon', 'store', 'restaurant']):
                            amount = -abs(amount)
                
                except ValueError:
                    continue
                
                transaction = {
                    "date": parsed_date,
                    "description": desc_str,
                    "amount": amount
                }
                
                transactions.append(transaction)
    
    # Remove duplicates (same date, description, and amount)
    seen = set()
    unique_transactions = []
    for trans in transactions:
        key = (trans["date"], trans["description"], trans["amount"])
        if key not in seen:
            seen.add(key)
            unique_transactions.append(trans)
    
    return unique_transactions

def parse_statement_date(date_str: str) -> str:
    """Parse various date formats from bank statements"""
    try:
        # Month abbreviations
        months = {
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
            'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
        }
        
        date_str = date_str.lower().strip()
        
        # Pattern: "jan 15" or "jan 15, 2024"
        month_day_match = re.search(r'([a-z]{3})\s+(\d{1,2})(?:,?\s*(\d{4}))?', date_str)
        if month_day_match:
            month_name = month_day_match.group(1)
            day = month_day_match.group(2).zfill(2)
            year = month_day_match.group(3) or str(datetime.now().year)
            
            if month_name in months:
                month = months[month_name]
                return f"{year}-{month}-{day}"
        
        # Pattern: "01/15/2024", "1/15/24", "01-15-2024"
        numeric_match = re.search(r'(\d{1,2})[\/-](\d{1,2})[\/-](\d{2,4})', date_str)
        if numeric_match:
            month = numeric_match.group(1).zfill(2)
            day = numeric_match.group(2).zfill(2)
            year = numeric_match.group(3)
            
            # Handle 2-digit years
            if len(year) == 2:
                year = '20' + year if int(year) < 50 else '19' + year
            
            return f"{year}-{month}-{day}"
        
        # Pattern: "2024-01-15"
        iso_match = re.search(r'(\d{4})[\/-](\d{1,2})[\/-](\d{1,2})', date_str)
        if iso_match:
            year = iso_match.group(1)
            month = iso_match.group(2).zfill(2)
            day = iso_match.group(3).zfill(2)
            return f"{year}-{month}-{day}"
    
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}")
    
    return None
