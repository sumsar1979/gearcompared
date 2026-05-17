#!/usr/bin/env python3
"""Fix UTF-8 encoding artifacts in product JSON files."""
import json

def fix_text(text):
    if not isinstance(text, str):
        return text
    # Replace mangled UTF-8 sequences with clean ASCII equivalents
    replaces = [
        ('\u2013', '-'),     # en dash
        ('\u2014', ' - '),   # em dash
        ('\u00d7', 'x'),     # multiplication sign
        ('\u201c', '"'),     # left double quote
        ('\u201d', '"'),     # right double quote
        ('\u2019', "'"),     # right single quote
        ('\u2018', "'"),     # left single quote
        ('\u00e9', 'e'),     # e acute
        ('\u00b0', ' deg '), # degree
        ('\u2122', ''),      # TM
        ('\u00ae', ''),      # registered
    ]
    for bad, good in replaces:
        text = text.replace(bad, good)
    # Fallback: remove any remaining non-ASCII
    text = text.encode('ascii', errors='replace').decode('ascii')
    text = text.replace('\ufffd', '')
    return text

def fix_dict(d):
    if isinstance(d, dict):
        return {fix_text(k): fix_dict(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [fix_dict(i) for i in d]
    elif isinstance(d, str):
        return fix_text(d)
    return d

paths = [
    r'C:\Users\Eland\.openclaw\workspace\gearcompared\data\products\standing-desks.json',
    r'C:\Users\Eland\.openclaw\workspace\gearcompared\data\products\kitchen-appliances.json',
]

for p in paths:
    data = json.load(open(p, encoding='utf-8'))
    fixed = fix_dict(data)
    json.dump(fixed, open(p, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'Fixed: {p}')
