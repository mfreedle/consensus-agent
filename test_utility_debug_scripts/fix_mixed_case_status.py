#!/usr/bin/env python3
"""
Fix mixed case status values in database
Standardize all to lowercase (enum values)
"""
import sqlite3


def fix_mixed_case_statuses():
    print("🔧 Fixing mixed case status values...")
    
    # Connect to database
    conn = sqlite3.connect('agent_mark.db')
    cursor = conn.cursor()
    
    # Check current values
    cursor.execute('SELECT DISTINCT status FROM document_approvals')
    current_statuses = [s[0] for s in cursor.fetchall()]
    print(f"Current status values: {current_statuses}")
    
    # Fix uppercase to lowercase
    mappings = {
        'PENDING': 'pending',
        'APPROVED': 'approved', 
        'REJECTED': 'rejected',
        'EXPIRED': 'expired',
        'AUTO_APPROVED': 'auto_approved'
    }
    
    fixed_count = 0
    for old_value, new_value in mappings.items():
        cursor.execute('UPDATE document_approvals SET status = ? WHERE status = ?', (new_value, old_value))
        count = cursor.rowcount
        if count > 0:
            print(f"✅ Updated {count} records from '{old_value}' to '{new_value}'")
            fixed_count += count
    
    if fixed_count == 0:
        print("ℹ️ No records needed updating")
    
    # Commit changes
    conn.commit()
    
    # Verify fix
    cursor.execute('SELECT DISTINCT status FROM document_approvals')
    final_statuses = [s[0] for s in cursor.fetchall()]
    print(f"Final status values: {final_statuses}")
    
    # Check for any remaining uppercase values
    uppercase_values = [s for s in final_statuses if s.isupper()]
    if uppercase_values:
        print(f"⚠️ Still have uppercase values: {uppercase_values}")
    else:
        print("✅ All status values are now lowercase")
    
    conn.close()
    print("🔧 Status fix completed!")

if __name__ == "__main__":
    fix_mixed_case_statuses()
