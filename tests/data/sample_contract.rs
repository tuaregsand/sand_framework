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
