"""
IDV Sync Job

Periodically checks users with identity_vault_id to see if they've updated
their information in IDV, and syncs any changes to the local database.
"""

import os
import asyncio
import httpx
from datetime import datetime
from app.db import SessionLocal
from app.models.user import User
from app.models.user_address import UserAddress
from app.utils.slack import get_slack_username
from sqlalchemy import or_


IDV_HOST = os.getenv("IDV_HOST", "https://hca.dinosaurbbq.org")
IDV_GLOBAL_PROGRAM_KEY = os.getenv("IDV_GLOBAL_PROGRAM_KEY")

IDV_SYNC_INTERVAL_SECONDS = int(os.getenv("IDV_SYNC_INTERVAL_SECONDS", "3600"))  # Default 1 hour


def get_idv_identity(identity_id: str) -> dict | None:
    """Fetch identity from IDV using the global program key."""
    if not IDV_GLOBAL_PROGRAM_KEY:
        print("❌ IDV_GLOBAL_PROGRAM_KEY not set")
        return None
    
    try:
        response = httpx.get(
            f"{IDV_HOST}/api/v1/identities/{identity_id}",
            headers={"Authorization": f"Bearer {IDV_GLOBAL_PROGRAM_KEY}"},
            timeout=10.0
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  Failed to fetch identity {identity_id}: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️  Error fetching identity {identity_id}: {e}")
        return None


def sync_user_from_idv(db, user: User, idv_data: dict) -> bool:
    """Sync user data from IDV response. Returns True if any changes were made."""
    changed = False
    identity = idv_data.get("identity", idv_data)
    
    # Sync verification status
    new_status = identity.get("verification_status")
    if new_status and new_status != user.verification_status:
        print(f"  📝 Updating verification_status: {user.verification_status} → {new_status}")
        user.verification_status = new_status
        changed = True
    
    # Sync ysws_eligible
    new_ysws = identity.get("ysws_eligible")
    if new_ysws is not None and new_ysws != user.ysws_eligible:
        print(f"  📝 Updating ysws_eligible: {user.ysws_eligible} → {new_ysws}")
        user.ysws_eligible = new_ysws
        changed = True
    
    # Sync slack_id if not already set
    new_slack_id = identity.get("slack_id")
    if new_slack_id and not user.slack_id:
        print(f"  📝 Adding slack_id: {new_slack_id}")
        user.slack_id = new_slack_id
        changed = True
    
    # Sync handle from Slack username if user has slack_id but no handle
    if user.slack_id and not user.handle:
        slack_username = get_slack_username(user.slack_id)
        if slack_username:
            print(f"  📝 Setting handle from Slack username: {slack_username}")
            user.handle = slack_username
            changed = True
    
    # Sync profile info
    if user.profile:
        first_name = identity.get("first_name")
        last_name = identity.get("last_name")
        birthday = identity.get("birthday")
        
        if first_name and not user.profile.first_name:
            print(f"  📝 Adding first_name")
            user.profile.first_name = first_name
            changed = True
        
        if last_name and not user.profile.last_name:
            print(f"  📝 Adding last_name")
            user.profile.last_name = last_name
            changed = True
        
        if birthday and not user.profile.birthday:
            print(f"  📝 Adding birthday")
            try:
                user.profile.birthday = datetime.fromisoformat(birthday.replace("Z", "+00:00"))
                changed = True
            except (ValueError, AttributeError):
                pass
    
    # Sync address
    addresses = identity.get("addresses", [])
    if addresses:
        idv_addr = addresses[0]
        has_address_data = idv_addr.get("line_1")
        
        if has_address_data:
            existing_address = next((a for a in user.addresses if a.is_primary), None)
            
            if not existing_address:
                print(f"  📝 Adding address")
                new_address = UserAddress(
                    user_id=user.user_id,
                    address_line_1=idv_addr.get("line_1", ""),
                    address_line_2=idv_addr.get("line_2"),
                    city=idv_addr.get("city"),
                    state=idv_addr.get("state"),
                    country=idv_addr.get("country_code"),
                    post_code=idv_addr.get("postal_code"),
                    is_primary=True
                )
                db.add(new_address)
                changed = True
            elif not existing_address.address_line_1:
                print(f"  📝 Updating address")
                existing_address.address_line_1 = idv_addr.get("line_1", "")
                existing_address.address_line_2 = idv_addr.get("line_2")
                existing_address.city = idv_addr.get("city")
                existing_address.state = idv_addr.get("state")
                existing_address.country = idv_addr.get("country_code")
                existing_address.post_code = idv_addr.get("postal_code")
                changed = True
    
    # Update idv_country if address has country
    if addresses and addresses[0].get("country_code") and not user.idv_country:
        user.idv_country = addresses[0].get("country_code")
        changed = True
    
    return changed


def find_users_needing_sync(db) -> list[User]:
    """Find users with identity_vault_id who might have incomplete data."""
    return db.query(User).filter(
        User.identity_vault_id.isnot(None),
        or_(
            User.verification_status.is_(None),
            User.verification_status == "needs_submission",
            User.verification_status == "pending",
            User.ysws_eligible.is_(None),
            # Also sync users who have slack_id but no handle
            (User.slack_id.isnot(None)) & (User.handle.is_(None)),
        )
    ).all()


def run_idv_sync():
    """Main sync function."""
    db = SessionLocal()
    
    try:
        print("🔍 [IDV Sync] Finding users needing sync...")
        
        users = find_users_needing_sync(db)
        
        if not users:
            print("✅ [IDV Sync] No users need syncing")
            return
        
        print(f"📦 [IDV Sync] Found {len(users)} user(s) to check")
        
        synced_count = 0
        
        for user in users:
            idv_data = get_idv_identity(user.identity_vault_id)
            
            if idv_data:
                if sync_user_from_idv(db, user, idv_data):
                    synced_count += 1
                    print(f"   ✅ Synced user {user.user_id}")
        
        db.commit()
        print(f"✅ [IDV Sync] Complete. Updated {synced_count}/{len(users)} users.")
        
    except Exception as e:
        print(f"❌ [IDV Sync] Error: {e}")
        db.rollback()
    finally:
        db.close()


async def idv_sync_task():
    """Background task that runs IDV sync periodically."""
    while True:
        try:
            run_idv_sync()
        except Exception as e:
            print(f"❌ [IDV Sync] Task error: {e}")
        
        await asyncio.sleep(IDV_SYNC_INTERVAL_SECONDS)
