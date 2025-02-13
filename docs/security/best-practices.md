# Security Best Practices

{% hint style="warning" %}
Security is critical in blockchain development. Follow these guidelines to protect your applications.
{% endhint %}

## Smart Contract Security

### Account Validation
```solana
pub fn process_instruction(program_id: &Pubkey, accounts: &[AccountInfo], input: &[u8]) -> ProgramResult {
    // Always validate account ownership
    if account.owner != program_id {
        return Err(ProgramError::IncorrectProgramId);
    }
    
    // Verify account is writable if needed
    if !account.is_writable {
        return Err(ProgramError::InvalidAccountData);
    }
}
```

### Input Validation
* Validate all instruction data
* Check numerical bounds
* Verify account permissions
* Validate signatures

## API Security

### Authentication
* Use JWT tokens
* Implement role-based access
* Regular token rotation
* Secure token storage

### Rate Limiting
```python
from fastapi import FastAPI, Depends
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

## Environment Security

{% tabs %}
{% tab title="Development" %}
* Use `.env.example` for templates
* Never commit `.env` files
* Use strong development credentials
{% endtab %}

{% tab title="Production" %}
* Use secrets management
* Regular credential rotation
* Audit access logs
* Enable MFA
{% endtab %}
{% endtabs %}

## Deployment Security

### Docker Security
* Use official base images
* Regular security updates
* Minimal container permissions
* Resource limitations

### Kubernetes Security
* Network policies
* Pod security policies
* Secret management
* Regular auditing

## Monitoring

* Log security events
* Set up alerts
* Regular security scans
* Penetration testing

{% hint style="info" %}
Regular security audits are recommended for production deployments.
{% endhint %}
