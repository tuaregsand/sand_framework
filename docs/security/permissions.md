# Permissions

{% hint style="info" %}
Understanding and properly configuring permissions is crucial for secure operation of Sand Framework.
{% endhint %}

## Role-Based Access Control

{% tabs %}
{% tab title="User Roles" %}
* **Admin**: Full system access
* **Developer**: Code analysis and AI features
* **Analyst**: Analytics and monitoring
* **Reader**: Read-only access
{% endtab %}

{% tab title="Permissions Matrix" %}
| Feature | Admin | Developer | Analyst | Reader |
|---------|-------|-----------|----------|---------|
| AI Analysis | ✅ | ✅ | ❌ | ❌ |
| Contract Scan | ✅ | ✅ | ❌ | ❌ |
| View Analytics | ✅ | ✅ | ✅ | ✅ |
| Modify Settings | ✅ | ❌ | ❌ | ❌ |
{% endtab %}
{% endtabs %}

## API Permissions

```python
from fastapi import Security
from sand.security import require_permissions

@router.post("/analyze")
@require_permissions(["contract:analyze"])
async def analyze_contract(
    contract: Contract,
    user: User = Security(get_current_user)
):
    pass
```

## File System Permissions

```bash
# Recommended permissions
chmod 644 config.yaml
chmod 600 .env
chmod 755 scripts/*.sh
```

## Database Permissions

```sql
-- Example database roles
CREATE ROLE sand_admin;
CREATE ROLE sand_developer;
CREATE ROLE sand_analyst;
CREATE ROLE sand_reader;

-- Grant permissions
GRANT ALL ON ALL TABLES IN SCHEMA public TO sand_admin;
GRANT SELECT, INSERT ON analysis_results TO sand_developer;
GRANT SELECT ON analytics_data TO sand_analyst;
GRANT SELECT ON public_data TO sand_reader;
```

## Environment Security

{% hint style="warning" %}
Protect sensitive environment variables:
* API keys
* Database credentials
* Private keys
* Service tokens
{% endhint %}

## Contact for Access

For permission-related inquiries or access requests, contact:
* Twitter: [@0xtuareg](https://x.com/0xtuareg)

## Audit Logging

```python
@router.post("/admin/grant-access")
@require_permissions(["admin:grant_access"])
async def grant_access(request: AccessRequest):
    # Log all permission changes
    audit_logger.info(
        f"Access granted to {request.user} "
        f"role={request.role} "
        f"by={current_user.id}"
    )
```

## Best Practices

1. Follow principle of least privilege
2. Regularly audit permissions
3. Remove unused accounts
4. Monitor access patterns
5. Document all role changes

{% hint style="success" %}
Regular security audits help maintain proper permission configuration.
{% endhint %}
