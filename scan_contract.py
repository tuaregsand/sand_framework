#!/usr/bin/env python3
import asyncio
import argparse
import sys
from pathlib import Path
from agents.contract_analysis.security_scanner import SecurityScanner

async def scan_file(file_path: str, output_format: str = 'text'):
    """Scan a smart contract file for security vulnerabilities."""
    try:
        # Read the contract code
        with open(file_path, 'r') as f:
            code = f.read()
        
        # Initialize scanner
        scanner = SecurityScanner()
        
        # Scan the code
        issues = await scanner.scan(code)
        
        # Output results
        if output_format == 'text':
            print(f'\nScanning {file_path}...')
            print('-' * 50)
            
            if not issues:
                print('No security issues found!')
                return
            
            for issue in issues:
                print(f'\nIssue Found:')
                print(f'Type: {issue["name"]}')
                print(f'Severity: {issue["severity"].upper()}')
                print(f'Description: {issue["description"]}')
                print(f'Location: Line {issue["line_number"]}')
                print(f'Code: {issue["snippet"]}')
                
        elif output_format == 'json':
            import json
            print(json.dumps({'file': file_path, 'issues': issues}, indent=2))
            
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error scanning file: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Smart Contract Security Scanner')
    parser.add_argument('file', help='Path to the smart contract file to scan')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                      help='Output format (text or json)')
    
    args = parser.parse_args()
    
    # Run the scanner
    asyncio.run(scan_file(args.file, args.format))

if __name__ == '__main__':
    main()
