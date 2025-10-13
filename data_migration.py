"""
Data Migration Script for SBU Purchase Orders
Cleans, validates, and migrates PO data from Excel files to SQLite database
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import os
import shutil
from database.db_manager import DatabaseManager

# Configure pandas display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

class DataMigrationManager:
    """Handles data cleaning and migration for SBU PO records"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.sbu_mapping = {}
        self.client_mapping = {}
        self.migration_log = []
        self.errors = []
        
    def log(self, message):
        """Log migration progress"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.migration_log.append(log_entry)
        print(log_entry)
        
    def log_error(self, message):
        """Log errors"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_entry = f"[{timestamp}] ERROR: {message}"
        self.errors.append(error_entry)
        print(f"❌ {error_entry}")
        
    def backup_database(self):
        """Create a backup of the database before migration"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_before_migration_{timestamp}.db"
            
            if os.path.exists(self.db.db_path):
                shutil.copy2(self.db.db_path, backup_path)
                self.log(f"✓ Database backed up to: {backup_path}")
                return backup_path
            else:
                self.log("No existing database to backup - will create new one")
                return None
        except Exception as e:
            self.log_error(f"Backup failed: {str(e)}")
            return None
            
    def load_sbu_register(self, filepath="SBU Data/SBU Register.csv"):
        """Load SBU information from the register CSV"""
        try:
            self.log("\n" + "="*80)
            self.log("STEP 1: Loading SBU Register")
            self.log("="*80)
            
            # Read the CSV - it has headers in row 2
            df = pd.read_csv(filepath, skiprows=1)
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            self.log(f"Found {len(df)} SBUs in register")
            
            sbu_count = 0
            for idx, row in df.iterrows():
                try:
                    sbu_name = str(row['SBU NAME']).strip() if pd.notna(row['SBU NAME']) else None
                    shorthand = str(row['S/HAND']).strip() if pd.notna(row['S/HAND']) else None
                    manager = str(row['MANAGER']).strip() if pd.notna(row['MANAGER']) else ""
                    location = str(row['LOCATION']).strip() if pd.notna(row['LOCATION']) else ""
                    
                    if not sbu_name or sbu_name == 'nan':
                        continue
                        
                    # Check if SBU already exists
                    existing_sbus = self.db.get_sbus(active_only=False)
                    existing = next((s for s in existing_sbus if s['name'] == sbu_name), None)
                    
                    if existing:
                        sbu_id = existing['id']
                        self.log(f"  ⚠ SBU already exists: {sbu_name} (ID: {sbu_id})")
                    else:
                        sbu_id = self.db.add_sbu(
                            name=sbu_name,
                            description=f"Strategic Business Unit - {shorthand}",
                            manager=manager,
                            location=location,
                            budget=0.0
                        )
                        self.log(f"  ✓ Added SBU: {sbu_name} (ID: {sbu_id})")
                        sbu_count += 1
                    
                    # Store mapping with both full name and shorthand
                    self.sbu_mapping[sbu_name] = sbu_id
                    if shorthand:
                        self.sbu_mapping[shorthand] = sbu_id
                        
                except Exception as e:
                    self.log_error(f"Failed to add SBU at row {idx}: {str(e)}")
                    
            self.log(f"\n✓ Successfully loaded {sbu_count} new SBUs")
            self.log(f"Total SBUs in mapping: {len(self.sbu_mapping)}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to load SBU register: {str(e)}")
            return False
            
    def read_po_file(self, filepath, sbu_shorthand):
        """Read and clean a PO Excel file"""
        try:
            self.log(f"\n  Reading file: {os.path.basename(filepath)}")
            
            # Try to read with different header configurations
            df = None
            
            # First, try reading to detect the structure
            temp_df = pd.read_excel(filepath, nrows=5)
            
            # Check if first row contains column headers
            if 'S/N' in temp_df.columns or 'PO NUMBER' in temp_df.columns:
                # Headers are in first row
                df = pd.read_excel(filepath)
            else:
                # Headers are in second row (row index 1)
                df = pd.read_excel(filepath, header=1)
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Standardize column names
            column_mapping = {
                'DESCRIPTION OF THE ORDER ': 'DESCRIPTION OF THE ORDER',
                'DESCRIPTION OF THE ORDER': 'DESCRIPTION OF THE ORDER',
                'VALUE IN USD ': 'VALUE IN USD',
                'VALUE IN USD': 'VALUE IN USD',
                'DATE ISSUED': 'DATE ISSUED',
                'DATE EXPIRED': 'DATE EXPIRED',
                'PO NUMBER': 'PO NUMBER',
                'CLIENT': 'CLIENT'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Remove rows where essential columns are all NaN
            essential_cols = ['PO NUMBER', 'CLIENT']
            df = df.dropna(subset=essential_cols, how='all')
            
            # Add SBU identifier
            df['SBU'] = sbu_shorthand
            
            self.log(f"  Found {len(df)} records in {os.path.basename(filepath)}")
            
            return df
            
        except Exception as e:
            self.log_error(f"Failed to read {filepath}: {str(e)}")
            return None
            
    def clean_po_data(self, df):
        """Clean and standardize PO data"""
        try:
            # Convert PO NUMBER to string and clean
            df['PO NUMBER'] = df['PO NUMBER'].astype(str).str.strip()
            df['PO NUMBER'] = df['PO NUMBER'].replace('nan', np.nan)
            
            # Clean CLIENT names
            df['CLIENT'] = df['CLIENT'].astype(str).str.strip().str.upper()
            df['CLIENT'] = df['CLIENT'].replace('NAN', np.nan)
            
            # Clean DESCRIPTION
            if 'DESCRIPTION OF THE ORDER' in df.columns:
                df['DESCRIPTION OF THE ORDER'] = df['DESCRIPTION OF THE ORDER'].astype(str).str.strip()
                df['DESCRIPTION OF THE ORDER'] = df['DESCRIPTION OF THE ORDER'].replace('nan', '')
            
            # Clean and validate VALUE IN USD
            if 'VALUE IN USD' in df.columns:
                df['VALUE IN USD'] = pd.to_numeric(df['VALUE IN USD'], errors='coerce')
                # If USD value is missing but NGN is available, try conversion
                if 'VALUE IN NGN' in df.columns:
                    ngn_rate = 1650  # Approximate USD/NGN exchange rate
                    df['VALUE IN NGN'] = pd.to_numeric(df['VALUE IN NGN'], errors='coerce')
                    mask = df['VALUE IN USD'].isna() & df['VALUE IN NGN'].notna()
                    df.loc[mask, 'VALUE IN USD'] = df.loc[mask, 'VALUE IN NGN'] / ngn_rate
            
            # Handle DATE ISSUED
            if 'DATE ISSUED' in df.columns:
                df['DATE ISSUED'] = pd.to_datetime(df['DATE ISSUED'], errors='coerce')
            
            # Handle DATE EXPIRED - if all NaN, generate expiry dates (1 year from issued)
            if 'DATE EXPIRED' in df.columns:
                df['DATE EXPIRED'] = pd.to_datetime(df['DATE EXPIRED'], errors='coerce')
                
                # If expired date is missing, set it to 1 year from issue date
                mask = df['DATE EXPIRED'].isna() & df['DATE ISSUED'].notna()
                df.loc[mask, 'DATE EXPIRED'] = df.loc[mask, 'DATE ISSUED'] + pd.DateOffset(years=1)
            
            # Remove rows with no PO NUMBER or CLIENT
            initial_count = len(df)
            df = df.dropna(subset=['PO NUMBER', 'CLIENT'])
            dropped = initial_count - len(df)
            if dropped > 0:
                self.log(f"  Removed {dropped} rows with missing PO NUMBER or CLIENT")
            
            # Remove rows with invalid USD values
            initial_count = len(df)
            df = df[df['VALUE IN USD'].notna() & (df['VALUE IN USD'] > 0)]
            dropped = initial_count - len(df)
            if dropped > 0:
                self.log(f"  Removed {dropped} rows with invalid or zero USD values")
            
            return df
            
        except Exception as e:
            self.log_error(f"Failed to clean data: {str(e)}")
            return df
            
    def load_all_po_files(self):
        """Load and combine all PO files"""
        try:
            self.log("\n" + "="*80)
            self.log("STEP 2: Loading and Cleaning PO Data Files")
            self.log("="*80)
            
            po_files = [
                ("SBU Data/2025 Purchase orders - ED&C.xlsx", "ED&C"),
                ("SBU Data/2025 Purchase orders - GCM.xlsx", "GCM"),
                ("SBU Data/2025 Purchase orders - PMC.xlsx", "PMC"),
                ("SBU Data/2025 Purchase orders - TSS.xlsx", "TCS"),  # TSS maps to TCS
                ("SBU Data/2025 Purchase orders OSS.xlsx", "OSS"),
            ]
            
            all_pos = []
            
            for filepath, sbu_code in po_files:
                if not os.path.exists(filepath):
                    self.log_error(f"File not found: {filepath}")
                    continue
                    
                df = self.read_po_file(filepath, sbu_code)
                if df is not None and len(df) > 0:
                    df_cleaned = self.clean_po_data(df)
                    all_pos.append(df_cleaned)
                    self.log(f"  ✓ Cleaned {len(df_cleaned)} valid records from {sbu_code}")
            
            if not all_pos:
                self.log_error("No PO data loaded!")
                return None
                
            # Combine all dataframes
            combined_df = pd.concat(all_pos, ignore_index=True)
            
            self.log(f"\n✓ Total records loaded: {len(combined_df)}")
            self.log(f"  Unique PO Numbers: {combined_df['PO NUMBER'].nunique()}")
            self.log(f"  Unique Clients: {combined_df['CLIENT'].nunique()}")
            self.log(f"  SBUs represented: {combined_df['SBU'].nunique()}")
            
            return combined_df
            
        except Exception as e:
            self.log_error(f"Failed to load PO files: {str(e)}")
            return None
            
    def migrate_clients(self, df):
        """Extract and migrate unique clients to database"""
        try:
            self.log("\n" + "="*80)
            self.log("STEP 3: Migrating Client Companies")
            self.log("="*80)
            
            unique_clients = df['CLIENT'].unique()
            self.log(f"Found {len(unique_clients)} unique clients")
            
            client_count = 0
            for client_name in unique_clients:
                try:
                    if pd.isna(client_name) or str(client_name).strip() == '':
                        continue
                        
                    client_name = str(client_name).strip().upper()
                    
                    # Check if client already exists
                    existing_clients = self.db.get_clients(active_only=False)
                    existing = next((c for c in existing_clients if c['name'].upper() == client_name), None)
                    
                    if existing:
                        client_id = existing['id']
                        self.log(f"  ⚠ Client already exists: {client_name} (ID: {client_id})")
                    else:
                        client_id = self.db.add_client(
                            name=client_name,
                            industry_sector="Oil & Gas",
                            contact_person="",
                            email="",
                            phone="",
                            address="",
                            country="Nigeria"
                        )
                        self.log(f"  ✓ Added client: {client_name} (ID: {client_id})")
                        client_count += 1
                    
                    self.client_mapping[client_name] = client_id
                    
                except Exception as e:
                    self.log_error(f"Failed to add client '{client_name}': {str(e)}")
                    
            self.log(f"\n✓ Successfully migrated {client_count} new clients")
            self.log(f"Total clients in mapping: {len(self.client_mapping)}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to migrate clients: {str(e)}")
            return False
            
    def migrate_purchase_orders(self, df):
        """Migrate purchase orders to database"""
        try:
            self.log("\n" + "="*80)
            self.log("STEP 4: Migrating Purchase Orders")
            self.log("="*80)
            
            po_count = 0
            skipped_count = 0
            
            for idx, row in df.iterrows():
                try:
                    # Get SBU ID
                    sbu_code = row['SBU']
                    sbu_id = self.sbu_mapping.get(sbu_code)
                    
                    if not sbu_id:
                        self.log_error(f"SBU not found for code: {sbu_code}")
                        skipped_count += 1
                        continue
                    
                    # Get Client ID
                    client_name = str(row['CLIENT']).strip().upper()
                    client_id = self.client_mapping.get(client_name)
                    
                    if not client_id:
                        self.log_error(f"Client not found: {client_name}")
                        skipped_count += 1
                        continue
                    
                    # Prepare PO data
                    po_number = str(row['PO NUMBER']).strip()
                    po_value = float(row['VALUE IN USD'])
                    
                    # Check if PO already exists
                    existing_pos = self.db.get_purchase_orders()
                    if any(po['po_number'] == po_number for po in existing_pos):
                        self.log(f"  ⚠ PO already exists: {po_number}")
                        skipped_count += 1
                        continue
                    
                    # Date handling
                    start_date = row['DATE ISSUED']
                    if pd.isna(start_date):
                        start_date = datetime.now()
                    start_date_str = start_date.strftime('%Y-%m-%d')
                    
                    expiry_date = row['DATE EXPIRED']
                    if pd.isna(expiry_date):
                        expiry_date = start_date + timedelta(days=365)
                    expiry_date_str = expiry_date.strftime('%Y-%m-%d')
                    
                    # Project description
                    project_name = str(row.get('DESCRIPTION OF THE ORDER', '')).strip()
                    if project_name == 'nan' or project_name == '':
                        project_name = f"PO {po_number}"
                    
                    # Determine status based on expiry date
                    today = datetime.now()
                    if pd.to_datetime(expiry_date_str) < today:
                        status = "Expired"
                    else:
                        status = "Active"
                    
                    # Add to database
                    po_id = self.db.add_purchase_order(
                        po_number=po_number,
                        sbu_id=sbu_id,
                        client_id=client_id,
                        po_value=po_value,
                        currency="USD",
                        start_date=start_date_str,
                        expiry_date=expiry_date_str,
                        status=status,
                        project_name=project_name[:200],  # Limit length
                        project_description="",
                        contract_type="Standard",
                        payment_terms="As per agreement",
                        risk_factor=3
                    )
                    
                    if po_count < 5:  # Log first few for verification
                        self.log(f"  ✓ Added PO: {po_number} | {client_name} | ${po_value:,.2f}")
                    
                    po_count += 1
                    
                    # Progress indicator every 50 records
                    if po_count % 50 == 0:
                        self.log(f"  Progress: {po_count} POs migrated...")
                        
                except Exception as e:
                    self.log_error(f"Failed to add PO at row {idx}: {str(e)}")
                    skipped_count += 1
                    
            self.log(f"\n✓ Successfully migrated {po_count} purchase orders")
            self.log(f"⚠ Skipped {skipped_count} records")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to migrate purchase orders: {str(e)}")
            return False
            
    def generate_summary_report(self):
        """Generate a summary report of the migration"""
        try:
            self.log("\n" + "="*80)
            self.log("MIGRATION SUMMARY REPORT")
            self.log("="*80)
            
            # Get database summary
            summary = self.db.get_total_summary()
            sbu_summary = self.db.get_sbu_summary()
            
            self.log(f"\n📊 DATABASE STATISTICS:")
            self.log(f"  Total SBUs: {len(sbu_summary)}")
            self.log(f"  Total Clients: {summary['total_clients']}")
            self.log(f"  Total Purchase Orders: {summary['total_pos']}")
            self.log(f"  Total Portfolio Value: ${summary['total_value']:,.2f}")
            self.log(f"  Average PO Value: ${summary['avg_po_value']:,.2f}")
            
            self.log(f"\n📈 PO STATUS BREAKDOWN:")
            self.log(f"  Active: {summary['active_pos']}")
            self.log(f"  Completed: {summary['completed_pos']}")
            self.log(f"  Cancelled: {summary['cancelled_pos']}")
            
            self.log(f"\n🏢 SBU BREAKDOWN:")
            for sbu in sbu_summary:
                self.log(f"  {sbu['name']}: {sbu['total_pos']} POs | ${sbu['total_value']:,.2f}")
            
            # Check for expiring POs
            expiring_pos = self.db.get_expiring_pos(days_ahead=90)
            if expiring_pos:
                self.log(f"\n⚠️  EXPIRING POs (Next 90 days): {len(expiring_pos)}")
                for po in expiring_pos[:5]:  # Show first 5
                    days = int(po['days_remaining'])
                    self.log(f"  {po['po_number']} | {po['client_name']} | {days} days remaining")
            
            # Errors
            if self.errors:
                self.log(f"\n❌ ERRORS ENCOUNTERED: {len(self.errors)}")
                for error in self.errors[:10]:  # Show first 10
                    self.log(f"  {error}")
            
            return True
            
        except Exception as e:
            self.log_error(f"Failed to generate summary: {str(e)}")
            return False
            
    def save_migration_log(self):
        """Save migration log to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"migration_log_{timestamp}.txt"
            
            with open(log_filename, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.migration_log))
                if self.errors:
                    f.write("\n\n" + "="*80 + "\n")
                    f.write("ERRORS:\n")
                    f.write("="*80 + "\n")
                    f.write("\n".join(self.errors))
            
            self.log(f"\n💾 Migration log saved to: {log_filename}")
            return log_filename
            
        except Exception as e:
            self.log_error(f"Failed to save log: {str(e)}")
            return None
            
    def run_migration(self):
        """Execute the complete migration process"""
        try:
            self.log("="*80)
            self.log("SBU PURCHASE ORDER DATA MIGRATION")
            self.log("="*80)
            self.log(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Step 0: Backup
            self.backup_database()
            
            # Step 1: Load SBU Register
            if not self.load_sbu_register():
                self.log_error("Failed to load SBU register - aborting migration")
                return False
            
            # Step 2: Load and clean PO data
            df = self.load_all_po_files()
            if df is None or len(df) == 0:
                self.log_error("No PO data loaded - aborting migration")
                return False
            
            # Step 3: Migrate clients
            if not self.migrate_clients(df):
                self.log_error("Failed to migrate clients - aborting migration")
                return False
            
            # Step 4: Migrate purchase orders
            if not self.migrate_purchase_orders(df):
                self.log_error("Purchase order migration failed")
                return False
            
            # Step 5: Generate summary
            self.generate_summary_report()
            
            # Step 6: Create final backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_backup = f"backup_after_migration_{timestamp}.db"
            shutil.copy2(self.db.db_path, final_backup)
            self.log(f"\n💾 Final database backup: {final_backup}")
            
            # Save log
            self.save_migration_log()
            
            self.log("\n" + "="*80)
            self.log("✅ MIGRATION COMPLETED SUCCESSFULLY!")
            self.log("="*80)
            self.log(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True
            
        except Exception as e:
            self.log_error(f"Migration failed: {str(e)}")
            return False


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("SBU PURCHASE ORDER DATA MIGRATION TOOL")
    print("="*80)
    
    migrator = DataMigrationManager()
    success = migrator.run_migration()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("You can now run the Streamlit app to view the data:")
        print("  streamlit run sbu_app.py")
    else:
        print("\n❌ Migration failed! Check the log file for details.")
    
    return success


if __name__ == "__main__":
    main()

