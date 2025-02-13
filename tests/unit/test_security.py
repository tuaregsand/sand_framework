import pytest
from agents.contract_analysis.security_scanner import SecurityScanner
from agents.contract_analysis.analyzer import SecurityScanner as AnalyzerSecurityScanner
from unittest.mock import patch

@pytest.fixture
def security_scanner():
    return SecurityScanner()

@pytest.fixture
def sample_vulnerable_contract():
    return """
    pub fn transfer(ctx: Context<Transfer>) -> Result<()> {
        let amount = ctx.accounts.amount;
        **ctx.accounts.from.transfer(ctx.accounts.to, amount)?;
        Ok(())
    }
    """

@pytest.mark.asyncio
async def test_reentrancy_detection(security_scanner, sample_vulnerable_contract):
    issues = await security_scanner.scan(sample_vulnerable_contract)
    
    # Find reentrancy issues
    reentrancy_issues = [i for i in issues if i["category"] == "reentrancy"]
    
    assert len(reentrancy_issues) > 0
    assert reentrancy_issues[0]["severity"] == "critical"
    assert "reentrancy" in reentrancy_issues[0]["description"].lower()

@pytest.mark.asyncio
async def test_access_control(security_scanner):
    contract = """
    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        ctx.accounts.program.data = data;
        Ok(())
    }
    """
    
    issues = await security_scanner.scan(contract)
    
    # Find access control issues
    access_issues = [i for i in issues if i["category"] == "access_control"]
    
    assert len(access_issues) > 0
    assert "authority" in access_issues[0]["description"].lower()

@pytest.mark.asyncio
async def test_input_validation(security_scanner):
    contract = """
    #[account]
    pub struct UserAccount {
        pub balance: u64,
    }
    """
    
    issues = await security_scanner.scan(contract)
    
    # Find input validation issues
    validation_issues = [i for i in issues if i["category"] == "input_validation"]
    
    assert len(validation_issues) > 0
    assert "constraint" in validation_issues[0]["description"].lower()

@pytest.mark.asyncio
async def test_safe_contract(security_scanner):
    contract = """
    pub fn transfer(ctx: Context<Transfer>) -> Result<()> {
        require!(!ctx.accounts.from.is_locked);
        require!(ctx.accounts.from.authority == ctx.accounts.authority.key());
        let amount = ctx.accounts.amount;
        ctx.accounts.from.transfer(ctx.accounts.to, amount)?;
        Ok(())
    }
    """
    
    issues = await security_scanner.scan(contract)
    
    # Should not find critical issues
    critical_issues = [i for i in issues if i["severity"] == "critical"]
    assert len(critical_issues) == 0

@pytest.mark.asyncio
async def test_multiple_vulnerabilities(security_scanner):
    contract = """
    pub fn complex_operation(ctx: Context<Operation>) -> Result<()> {
        let value = ctx.accounts.value + 100;
        ctx.accounts.program.data = value;
        invoke(instruction, account_infos)?;
        Ok(())
    }
    """
    
    issues = await security_scanner.scan(contract)
    
    # Should find multiple issues
    assert len(issues) >= 3  # Should find at least 3 issues:
                            # 1. Unchecked arithmetic
                            # 2. Missing authority check
                            # 3. Unsafe CPI

@pytest.mark.asyncio
async def test_error_handling(security_scanner):
    contract = """
    pub fn process(ctx: Context<Process>) -> Result<()> {
        invoke(instruction, account_infos)
    }
    """
    
    issues = await security_scanner.scan(contract)
    
    # Find error handling issues
    error_issues = [i for i in issues if i["category"] == "error_handling"]
    
    assert len(error_issues) > 0
    assert "error handling" in error_issues[0]["description"].lower()

@pytest.mark.asyncio
async def test_pda_validation(security_scanner):
    contract = """
    let (pda, _) = Pubkey::find_program_address(&[b"seed"], program_id);
    """
    
    issues = await security_scanner.scan(contract)
    
    # Find PDA validation issues
    pda_issues = [i for i in issues if "pda" in i["category"].lower()]
    
    assert len(pda_issues) > 0
    assert "bump" in pda_issues[0]["description"].lower()

@pytest.mark.asyncio
async def test_pattern_loading(security_scanner):
    # Verify that vulnerability patterns are loaded
    assert security_scanner.vulnerability_patterns != {}
    assert "reentrancy" in security_scanner.vulnerability_patterns

@pytest.mark.asyncio
async def test_empty_contract(security_scanner):
    issues = await security_scanner.scan("")
    assert isinstance(issues, list)
    assert len(issues) == 0

@pytest.mark.asyncio
async def test_reentrancy_detection_analyzer():
    scanner = AnalyzerSecurityScanner()
    vulnerable_code = """
    function withdraw() public {
        uint amount = balances[msg.sender];
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        balances[msg.sender] = 0;
    }
    """
    results = await scanner.scan(vulnerable_code)
    vulnerabilities = [v for v in results if v["type"] == "reentrancy"]
    assert len(vulnerabilities) > 0
    assert vulnerabilities[0]["severity"] == "high"

@pytest.mark.asyncio
async def test_access_control_analyzer():
    scanner = AnalyzerSecurityScanner()
    vulnerable_code = """
    function setOwner(address newOwner) public {
        owner = newOwner;
    }
    """
    results = await scanner.scan(vulnerable_code)
    vulnerabilities = [v for v in results if v["type"] == "access_control"]
    assert len(vulnerabilities) > 0

@pytest.mark.asyncio
async def test_input_validation_analyzer():
    scanner = AnalyzerSecurityScanner()
    vulnerable_code = """
    function transfer(address to, uint256 amount) public {
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }
    """
    results = await scanner.scan(vulnerable_code)
    vulnerabilities = [v for v in results if v["type"] == "input_validation"]
    assert len(vulnerabilities) > 0

@pytest.mark.asyncio
async def test_error_handling_analyzer():
    scanner = AnalyzerSecurityScanner()
    vulnerable_code = """
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    """
    results = await scanner.scan(vulnerable_code)
    vulnerabilities = [v for v in results if v["type"] == "error_handling"]
    assert len(vulnerabilities) > 0

@pytest.mark.asyncio
async def test_pda_validation_analyzer():
    scanner = AnalyzerSecurityScanner()
    vulnerable_code = """
    #[account]
    pub struct GameAccount {
        pub authority: Pubkey,
        pub score: u64,
    }
    
    pub fn update_score(ctx: Context<UpdateScore>, new_score: u64) -> Result<()> {
        ctx.accounts.game.score = new_score;
        Ok(())
    }
    """
    results = await scanner.scan(vulnerable_code)
    vulnerabilities = [v for v in results if v["type"] == "pda_validation"]
    assert len(vulnerabilities) > 0
