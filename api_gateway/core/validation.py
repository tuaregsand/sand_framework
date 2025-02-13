"""
Input validation for smart contracts.
"""
from typing import Dict, Any, Optional
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# Maximum contract size (500KB)
MAX_CONTRACT_SIZE = 500 * 1024

# Maximum number of functions per contract
MAX_FUNCTIONS = 100

# Maximum number of lines per contract
MAX_LINES = 5000

class ContractValidationError(Exception):
    """Contract validation error."""
    pass

async def validate_contract(source_code: str) -> None:
    """
    Validate a smart contract.
    
    Args:
        source_code: Contract source code
        
    Raises:
        ContractValidationError: If contract is invalid
    """
    try:
        # Check contract size
        if len(source_code.encode('utf-8')) > MAX_CONTRACT_SIZE:
            raise ContractValidationError(
                f"Contract size exceeds maximum of {MAX_CONTRACT_SIZE/1024}KB"
            )
            
        # Check number of lines
        lines = source_code.splitlines()
        if len(lines) > MAX_LINES:
            raise ContractValidationError(
                f"Contract has too many lines (max {MAX_LINES})"
            )
            
        # Check number of functions
        function_count = source_code.count('function')
        if function_count > MAX_FUNCTIONS:
            raise ContractValidationError(
                f"Contract has too many functions (max {MAX_FUNCTIONS})"
            )
            
        # Basic syntax check
        if not source_code.strip():
            raise ContractValidationError("Contract is empty")
            
        if 'contract' not in source_code.lower():
            raise ContractValidationError("No contract definition found")
            
    except ContractValidationError:
        raise
    except Exception as e:
        logger.error(f"Error validating contract: {str(e)}")
        raise ContractValidationError("Invalid contract format")
