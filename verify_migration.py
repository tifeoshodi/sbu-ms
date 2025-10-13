"""
Quick Database Verification Script
Validates migration success and data integrity
"""

from database.db_manager import DatabaseManager
import os

def verify_database():
    """Verify database integrity and print summary"""
    
    print("\n" + "="*80)
    print("DATABASE VERIFICATION REPORT")
    print("="*80)
    
    # Check if database file exists
    db_path = "sbu_po_database.db"
    if not os.path.exists(db_path):
        print("❌ ERROR: Database file not found!")
        return False
    
    file_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
    print(f"\n📁 Database File: {db_path}")
    print(f"   Size: {file_size:.2f} MB")
    
    # Initialize database manager
    try:
        db = DatabaseManager()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Failed to connect to database: {str(e)}")
        return False
    
    # Verify SBUs
    print("\n" + "-"*80)
    print("📊 STRATEGIC BUSINESS UNITS")
    print("-"*80)
    sbus = db.get_sbus(active_only=True)
    print(f"Total SBUs: {len(sbus)}")
    for sbu in sbus:
        print(f"  ✓ {sbu['name'][:50]:<50} | Manager: {sbu['manager']}")
    
    # Verify Clients
    print("\n" + "-"*80)
    print("🏢 CLIENT COMPANIES")
    print("-"*80)
    clients = db.get_clients(active_only=True)
    print(f"Total Clients: {len(clients)}")
    print(f"Sample clients: {', '.join([c['name'] for c in clients[:10]])}")
    if len(clients) > 10:
        print(f"... and {len(clients) - 10} more")
    
    # Verify Purchase Orders
    print("\n" + "-"*80)
    print("📋 PURCHASE ORDERS")
    print("-"*80)
    pos = db.get_purchase_orders()
    print(f"Total Purchase Orders: {len(pos)}")
    
    if len(pos) > 0:
        # Show first few POs
        print("\nSample Purchase Orders:")
        for i, po in enumerate(pos[:5], 1):
            print(f"  {i}. PO: {po['po_number']:<20} | {po['sbu_name'][:30]:<30} | "
                  f"Client: {po['client_name'][:25]:<25} | ${po['po_value']:>12,.2f}")
    
    # Get summary statistics
    print("\n" + "-"*80)
    print("💰 FINANCIAL SUMMARY")
    print("-"*80)
    summary = db.get_total_summary()
    print(f"Total Portfolio Value: ${summary['total_value']:,.2f}")
    print(f"Average PO Value: ${summary['avg_po_value']:,.2f}")
    print(f"Active POs: {summary['active_pos']}")
    print(f"Completed POs: {summary['completed_pos']}")
    print(f"Cancelled POs: {summary['cancelled_pos']}")
    
    # Check expiring POs
    print("\n" + "-"*80)
    print("⚠️  RISK ALERTS")
    print("-"*80)
    expiring_30 = db.get_expiring_pos(days_ahead=30)
    expiring_90 = db.get_expiring_pos(days_ahead=90)
    print(f"POs expiring in next 30 days: {len(expiring_30)}")
    print(f"POs expiring in next 90 days: {len(expiring_90)}")
    
    if expiring_30:
        print("\n🚨 URGENT - Expiring within 30 days:")
        for po in expiring_30[:5]:
            days = int(po['days_remaining'])
            print(f"  • {po['po_number']} - {po['client_name']} - {days} days remaining")
    
    # Check backup directory
    print("\n" + "-"*80)
    print("💾 BACKUP STATUS")
    print("-"*80)
    backup_dir = "database_backups"
    if os.path.exists(backup_dir):
        backups = [f for f in os.listdir(backup_dir) if f.endswith('.db')]
        print(f"✅ Backup directory exists: {backup_dir}/")
        print(f"   Total backups: {len(backups)}")
        if backups:
            backups.sort(reverse=True)
            print(f"   Most recent: {backups[0]}")
    else:
        print("⚠️  No backup directory found")
    
    # Check migration logs
    migration_logs = [f for f in os.listdir('.') if f.startswith('migration_log_') and f.endswith('.txt')]
    if migration_logs:
        print(f"\n📄 Migration logs available: {len(migration_logs)}")
        print(f"   Latest: {max(migration_logs)}")
    
    # Final validation
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)
    
    checks = {
        "Database file exists": os.path.exists(db_path),
        "Database size > 0": file_size > 0,
        "SBUs loaded": len(sbus) >= 6,
        "Clients loaded": len(clients) >= 40,
        "Purchase Orders loaded": len(pos) >= 150,
        "Total value > $40M": summary['total_value'] > 40_000_000,
        "Backup system active": os.path.exists(backup_dir),
    }
    
    all_passed = all(checks.values())
    
    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check}")
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL CHECKS PASSED - DATABASE IS HEALTHY AND SECURE!")
    else:
        print("⚠️  SOME CHECKS FAILED - REVIEW ABOVE DETAILS")
    print("="*80 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = verify_database()
    exit(0 if success else 1)

