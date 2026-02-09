"""Seed initial data: tenant, admin user, and default roles."""

import asyncio
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config import get_settings
from domain.auth.models import Role, User, UserStatus
from shared.auth import hash_password
from shared import scopes as SCOPES

settings = get_settings()


async def seed_initial_data():
    """Create initial tenant, admin user, and default roles."""
    
    # Create async engine and session
    engine = create_async_engine(settings.database_url, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Use a fixed tenant_id for the initial tenant
        tenant_id = uuid4()
        
        print(f"\n✅ Creating initial tenant: {tenant_id}")
        
        # Create Admin role with all scopes
        admin_scopes = list(SCOPES.VALID_SCOPES)  # All available scopes
        admin_role = Role(
            id=uuid4(),
            tenant_id=tenant_id,
            name="Admin",
            scopes=admin_scopes,
        )
        session.add(admin_role)
        await session.flush()
        
        print(f"✅ Created role: {admin_role.name} ({admin_role.id})")
        print(f"   Scopes: {len(admin_scopes)} scopes assigned")
        
        # Create admin user
        admin_user = User(
            id=uuid4(),
            tenant_id=tenant_id,
            username="admin",
            email="admin@webconsig.localhost",
            password_hash=hash_password("admin"),
            status=UserStatus.active,
            role_ids=[str(admin_role.id)],  # Store as JSONB array of strings
        )
        session.add(admin_user)
        await session.flush()
        
        print(f"✅ Created user: {admin_user.username} ({admin_user.email})")
        print(f"   Password: admin")
        print(f"   Tenant ID: {tenant_id}")
        
        # Commit all changes
        await session.commit()
        
        print("\n🎉 Initial seed completed successfully!")
        print("\n📋 Login credentials:")
        print(f"   Username: admin")
        print(f"   Password: admin")
        print(f"   Tenant ID: {tenant_id}")
        print("\n⚠️  Remember to change the admin password after first login!")
    
    await engine.dispose()


if __name__ == "__main__":
    print("🌱 Starting database seed...")
    asyncio.run(seed_initial_data())
