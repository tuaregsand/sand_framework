import os
import sys
import pytest
from pathlib import Path

# Add the project root to Python path to make imports work
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from agents.contract_analysis.security_scanner import SecurityScanner

@pytest.fixture
def scanner():
    return SecurityScanner()

@pytest.mark.asyncio
async def test_reentrancy_detection(scanner):
    code = """
async def transfer_tokens(ctx):
    # Vulnerable: external call before state change
    await ctx.accounts.token_program.invoke_signed(
        "transfer",
        {"amount": 100}
    )
    ctx.accounts.vault.balance -= 100  # State change after external call
    """
    issues = await scanner.scan(code)
    reentrancy_issues = [i for i in issues if i["id"] == "REENTRANCY"]
    assert len(reentrancy_issues) == 1
    assert reentrancy_issues[0]["severity"] == "critical"

@pytest.mark.asyncio
async def test_missing_access_control(scanner):
    code = """
# Missing access control
pub fn admin_function(ctx):
    ctx.accounts.treasury.withdraw(1000)
    """
    issues = await scanner.scan(code)
    access_issues = [i for i in issues if i["id"] == "NO_ACCESS_CONTROL"]
    assert len(access_issues) == 1
    assert access_issues[0]["severity"] == "high"

@pytest.mark.asyncio
async def test_proper_access_control(scanner):
    code = """
@requires_auth
pub fn admin_function(ctx):
    ctx.accounts.treasury.withdraw(1000)
    """
    issues = await scanner.scan(code)
    access_issues = [i for i in issues if i["id"] == "NO_ACCESS_CONTROL"]
    assert len(access_issues) == 0

@pytest.mark.asyncio
async def test_input_validation(scanner):
    code = """
def process_amount(amount: int):
    # Missing validation
    return amount * 2
    """
    issues = await scanner.scan(code)
    validation_issues = [i for i in issues if i["id"] == "NO_INPUT_VALIDATION"]
    assert len(validation_issues) == 1
    assert validation_issues[0]["severity"] == "medium"

@pytest.mark.asyncio
async def test_pda_validation(scanner):
    code = """
async def create_account(ctx):
    # Missing PDA validation
    pda = await find_program_address([b"seed"], ctx.program_id)
    ctx.accounts.new_account = pda
    """
    issues = await scanner.scan(code)
    pda_issues = [i for i in issues if i["id"] == "INVALID_PDA"]
    assert len(pda_issues) == 1
    assert pda_issues[0]["severity"] == "high"

@pytest.mark.asyncio
async def test_proper_pda_validation(scanner):
    code = """
async def create_account(ctx):
    pda = await find_program_address([b"seed"], ctx.program_id)
    assert verify_program_address(pda, [b"seed"], ctx.program_id)
    ctx.accounts.new_account = pda
    """
    issues = await scanner.scan(code)
    pda_issues = [i for i in issues if i["id"] == "INVALID_PDA"]
    assert len(pda_issues) == 0

@pytest.mark.asyncio
async def test_arithmetic_validation(scanner):
    code = """
def calculate_rewards(amount, rate):
    # Unchecked arithmetic
    return amount * rate
    """
    issues = await scanner.scan(code)
    arithmetic_issues = [i for i in issues if "arithmetic" in i["id"].lower()]
    assert len(arithmetic_issues) > 0

@pytest.mark.asyncio
async def test_error_handling(scanner):
    # Test invalid code to check error handling
    code = "invalid python syntax {"
    issues = await scanner.scan(code)
    assert len(issues) == 1
    assert issues[0]["id"] == "SYNTAX_ERROR"
    assert issues[0]["severity"] == "critical"

@pytest.mark.asyncio
async def test_multiple_vulnerabilities(scanner):
    code = """
pub fn unsafe_transfer(ctx, amount):
    # Multiple issues:
    # 1. No access control
    # 2. No input validation
    # 3. Reentrancy vulnerability
    await ctx.accounts.token_program.invoke_signed("transfer", {"amount": amount})
    ctx.accounts.vault.balance = ctx.accounts.vault.balance - amount
    """
    issues = await scanner.scan(code)
    assert len(issues) >= 3  # Should find at least 3 issues
