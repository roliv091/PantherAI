import re
import PyPDF2
from typing import List, Dict, Any
from datetime import datetime
import io

def parse_pdf(file_path: str) -> List[Dict[str, Any]]:
    """Parse PDF and extract tasks using regex patterns"""
    tasks = []
    
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            # Extract tasks using regex patterns
            tasks = extract_tasks_from_text(text)
            
    except Exception as e:
        print(f"Error parsing PDF: {e}")
    
    return tasks

def extract_tasks_from_text(text: str) -> List[Dict[str, Any]]:
    """Extract tasks from text using regex patterns"""
    tasks = []
    
    # Common task patterns
    task_patterns = [
        r'(assignment|project|quiz|midterm|final|exam|homework|hw)\s*[:\-]?\s*([^,\n]+?)(?:\s*,\s*)?(?:due\s*[:\-]?\s*)?([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,\s*\d{4})?)?(?:\s*[,\-]?\s*(\d+(?:\.\d+)?%))?',
        r'(due\s*[:\-]?\s*)?([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,\s*\d{4})?)\s*[:\-]?\s*(assignment|project|quiz|midterm|final|exam|homework|hw)\s*[:\-]?\s*([^,\n]+?)(?:\s*[,\-]?\s*(\d+(?:\.\d+)?%))?',
        r'([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,\s*\d{4})?)\s*[:\-]?\s*([^,\n]+?)\s*[:\-]?\s*(assignment|project|quiz|midterm|final|exam|homework|hw)(?:\s*[,\-]?\s*(\d+(?:\.\d+)?%))?'
    ]
    
    for pattern in task_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        
        for match in matches:
            groups = match.groups()
            
            # Extract title, due date, and weight
            title = ""
            due = None
            weight = None
            
            if len(groups) >= 3:
                # Try to identify which group is which
                for i, group in enumerate(groups):
                    if group and group.strip():
                        group_lower = group.lower().strip()
                        
                        # Check if it's a task type
                        if any(task_type in group_lower for task_type in ['assignment', 'project', 'quiz', 'midterm', 'final', 'exam', 'homework', 'hw']):
                            continue
                        
                        # Check if it's a date
                        if re.search(r'[A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?', group):
                            due = parse_date(group.strip())
                            continue
                        
                        # Check if it's a percentage
                        if re.search(r'\d+(?:\.\d+)?%', group):
                            weight = float(re.search(r'(\d+(?:\.\d+)?)', group).group(1))
                            continue
                        
                        # Otherwise, it's likely the title
                        if not title:
                            title = group.strip()
            
            # If we found a title, add the task
            if title:
                task = {
                    "title": title,
                    "due": due,
                    "weight": weight
                }
                tasks.append(task)
    
    return tasks

def parse_date(date_str: str) -> str:
    """Parse date string and return ISO format"""
    try:
        # Common month names
        months = {
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'may': '05', 'june': '06', 'july': '07', 'august': '08',
            'september': '09', 'october': '10', 'november': '11', 'december': '12',
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
            'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
        }
        
        # Extract month and day
        match = re.search(r'([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?', date_str.lower())
        if match:
            month_name = match.group(1)
            day = match.group(2).zfill(2)
            
            if month_name in months:
                month = months[month_name]
                # Assume current year
                year = datetime.now().year
                return f"{year}-{month}-{day}"
    
    except Exception as e:
        print(f"Error parsing date: {e}")
    
    return None
