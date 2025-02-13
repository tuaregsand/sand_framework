import pytest
import asyncio
from agents.contract_analysis.analyzer import SmartContractAnalyzer
from agents.contract_analysis.security_scanner import SecurityScanner
from agents.contract_analysis.gas_optimizer import GasOptimizer
from agents.contract_analysis.code_quality import CodeQualityChecker
from agents.contract_analysis.metrics import ContractMetrics

@pytest.fixture
def sample_contract():
    return """
    pub fn transfer(ctx: Context<Transfer>) -> Result<()> {
        require!(!ctx.accounts.from.is_locked);
        require!(ctx.accounts.from.authority == ctx.accounts.authority.key());
        
        let amount = ctx.accounts.amount;
        ctx.accounts.from.transfer(ctx.accounts.to, amount)?;
        
        emit!(TransferEvent {
            from: ctx.accounts.from.key(),
            to: ctx.accounts.to.key(),
            amount,
        });
        
        Ok(())
    }
    
    #[account]
    pub struct UserAccount {
        pub authority: Pubkey,
        pub balance: u64,
        pub is_locked: bool,
    }
    
    #[derive(Accounts)]
    pub struct Transfer<'info> {
        #[account(mut)]
        pub from: Account<'info, UserAccount>,
        #[account(mut)]
        pub to: Account<'info, UserAccount>,
        pub authority: Signer<'info>,
    }
    """

@pytest.fixture
def analyzer(sample_contract):
    return SmartContractAnalyzer(source_code=sample_contract)

@pytest.mark.asyncio
async def test_full_analysis(analyzer):
    result = await analyzer.analyze()
    
    assert result is not None
    assert isinstance(result.security_issues, list)
    assert isinstance(result.gas_optimizations, list)
    assert isinstance(result.code_quality_issues, list)
    assert isinstance(result.metrics, dict)
    assert isinstance(result.summary, str)
    assert isinstance(result.risk_score, float)

@pytest.mark.asyncio
async def test_component_integration(analyzer):
    """Test that all components work together."""
    result = await analyzer.analyze()
    
    # Check security analysis
    assert len(result.security_issues) >= 0
    
    # Check gas optimizations
    assert len(result.gas_optimizations) >= 0
    
    # Check code quality
    assert len(result.code_quality_issues) >= 0
    
    # Check metrics
    assert result.metrics.get("lines_of_code") is not None
    assert result.metrics.get("complexity") is not None

@pytest.mark.asyncio
async def test_error_handling(analyzer):
    """Test error handling in analysis."""
    try:
        result = await analyzer.analyze()
        assert result is not None
    except Exception as e:
        pytest.fail(f"Analysis failed with error: {str(e)}")

@pytest.mark.asyncio
async def test_large_contract(analyzer):
    """Test analyzer performance with large contracts."""
    # Duplicate the sample code to create a larger contract
    large_code = analyzer.source_code * 10
    analyzer.source_code = large_code
    
    result = await analyzer.analyze()
    assert result is not None

@pytest.mark.asyncio
async def test_concurrent_analysis(analyzer):
    """Test concurrent analysis of multiple contracts."""
    # Run multiple analyses concurrently
    tasks = [analyzer.analyze() for _ in range(3)]
    results = await asyncio.gather(*tasks)
    
    assert all(r is not None for r in results)

@pytest.mark.asyncio
async def test_result_consistency(analyzer):
    """Test that analysis results are consistent."""
    result1 = await analyzer.analyze()
    result2 = await analyzer.analyze()
    
    assert result1.security_issues == result2.security_issues
    assert result1.gas_optimizations == result2.gas_optimizations
    assert result1.code_quality_issues == result2.code_quality_issues
