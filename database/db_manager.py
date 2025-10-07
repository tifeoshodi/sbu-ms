"""
Database Manager for SBU/PO Dashboard
Handles all database operations using SQLite
"""

import sqlite3
import os
import shutil
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd


class DatabaseManager:
    """Manages database operations for SBU/PO system"""
    
    def __init__(self, db_path: str = "sbu_po_database.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create SBU table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sbu (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    manager TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Create Client Companies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS client_companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    industry_sector TEXT,
                    contact_person TEXT,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    country TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Create Purchase Orders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchase_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    po_number TEXT NOT NULL UNIQUE,
                    sbu_id INTEGER NOT NULL,
                    client_id INTEGER NOT NULL,
                    po_value REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    start_date DATE NOT NULL,
                    expiry_date DATE NOT NULL,
                    status TEXT DEFAULT 'Active',
                    project_name TEXT,
                    project_description TEXT,
                    contract_type TEXT,
                    payment_terms TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sbu_id) REFERENCES sbu (id),
                    FOREIGN KEY (client_id) REFERENCES client_companies (id)
                )
            """)
            
            # Create PO Status History table for tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS po_status_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    po_id INTEGER NOT NULL,
                    old_status TEXT,
                    new_status TEXT NOT NULL,
                    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (po_id) REFERENCES purchase_orders (id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_po_sbu ON purchase_orders(sbu_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_po_client ON purchase_orders(client_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_po_status ON purchase_orders(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_po_dates ON purchase_orders(start_date, expiry_date)")
            
            # Database is ready - no default data insertion
            
            conn.commit()
            
    def add_sbu(self, name: str, description: str = "", manager: str = "", 
                department: str = "", location: str = "", budget: float = 0.0) -> int:
        """Add a new SBU"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sbu (name, description, manager) VALUES (?, ?, ?)
            """, (name, description, manager))
            return cursor.lastrowid
    
    def clear_database(self):
        """Clear all data from SBUs, clients, and purchase orders"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Clear in order due to foreign key constraints
            cursor.execute("DELETE FROM po_status_history")
            cursor.execute("DELETE FROM purchase_orders")
            cursor.execute("DELETE FROM client_companies")
            cursor.execute("DELETE FROM sbu")
            conn.commit()
            
    def add_client(self, name: str, industry_sector: str = "", contact_person: str = "",
                   email: str = "", phone: str = "", address: str = "", country: str = "") -> int:
        """Add a new client company"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO client_companies 
                (name, industry_sector, contact_person, email, phone, address, country) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, industry_sector, contact_person, email, phone, address, country))
            return cursor.lastrowid
            
    def add_purchase_order(self, po_number: str, sbu_id: int, client_id: int, po_value: float,
                          currency: str, start_date: str, expiry_date: str, status: str = "Active",
                          project_name: str = "", project_description: str = "", 
                          contract_type: str = "", payment_terms: str = "") -> int:
        """Add a new purchase order"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO purchase_orders 
                (po_number, sbu_id, client_id, po_value, currency, start_date, expiry_date, 
                 status, project_name, project_description, contract_type, payment_terms) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (po_number, sbu_id, client_id, po_value, currency, start_date, expiry_date,
                  status, project_name, project_description, contract_type, payment_terms))
            po_id = cursor.lastrowid
            
            # Add to status history
            cursor.execute("""
                INSERT INTO po_status_history (po_id, new_status, notes) 
                VALUES (?, ?, ?)
            """, (po_id, status, "Initial creation"))
            
            return po_id
            
    def get_sbus(self, active_only: bool = True) -> List[Dict]:
        """Get all SBUs"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM sbu"
            if active_only:
                query += " WHERE is_active = 1"
            query += " ORDER BY name"
            
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
            
    def get_clients(self, active_only: bool = True) -> List[Dict]:
        """Get all client companies"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM client_companies"
            if active_only:
                query += " WHERE is_active = 1"
            query += " ORDER BY name"
            
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
            
    def get_purchase_orders(self, sbu_id: Optional[int] = None, 
                           status: Optional[str] = None) -> List[Dict]:
        """Get purchase orders with optional filtering"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT po.*, sbu.name as sbu_name, cc.name as client_name
                FROM purchase_orders po
                JOIN sbu ON po.sbu_id = sbu.id
                JOIN client_companies cc ON po.client_id = cc.id
            """
            
            conditions = []
            params = []
            
            if sbu_id:
                conditions.append("po.sbu_id = ?")
                params.append(sbu_id)
                
            if status:
                conditions.append("po.status = ?")
                params.append(status)
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY po.start_date DESC"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
            
    def get_sbu_summary(self) -> List[Dict]:
        """Get summary statistics for each SBU"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    sbu.id,
                    sbu.name,
                    sbu.manager,
                    COUNT(po.id) as total_pos,
                    COALESCE(SUM(po.po_value), 0) as total_value,
                    COUNT(CASE WHEN po.status = 'Active' THEN 1 END) as active_pos,
                    COUNT(CASE WHEN po.status = 'Completed' THEN 1 END) as completed_pos,
                    COUNT(CASE WHEN po.status = 'Cancelled' THEN 1 END) as cancelled_pos,
                    AVG(po.po_value) as avg_po_value
                FROM sbu
                LEFT JOIN purchase_orders po ON sbu.id = po.sbu_id
                WHERE sbu.is_active = 1
                GROUP BY sbu.id, sbu.name, sbu.manager
                ORDER BY total_value DESC
            """)
            
            return [dict(row) for row in cursor.fetchall()]
            
    def get_total_summary(self) -> Dict:
        """Get overall summary statistics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_pos,
                    COALESCE(SUM(po_value), 0) as total_value,
                    COUNT(CASE WHEN status = 'Active' THEN 1 END) as active_pos,
                    COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed_pos,
                    COUNT(CASE WHEN status = 'Cancelled' THEN 1 END) as cancelled_pos,
                    AVG(po_value) as avg_po_value,
                    COUNT(DISTINCT sbu_id) as active_sbus,
                    COUNT(DISTINCT client_id) as total_clients
                FROM purchase_orders
            """)
            
            return dict(cursor.fetchone())
            
    def update_po_status(self, po_id: int, new_status: str, notes: str = "") -> bool:
        """Update purchase order status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get current status
            cursor.execute("SELECT status FROM purchase_orders WHERE id = ?", (po_id,))
            result = cursor.fetchone()
            if not result:
                return False
                
            old_status = result[0]
            
            # Update status
            cursor.execute("""
                UPDATE purchase_orders 
                SET status = ?, last_updated = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (new_status, po_id))
            
            # Add to history
            cursor.execute("""
                INSERT INTO po_status_history (po_id, old_status, new_status, notes) 
                VALUES (?, ?, ?, ?)
            """, (po_id, old_status, new_status, notes))
            
            return True
            
    def get_analytics_data(self) -> Dict:
        """Get comprehensive analytics data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            analytics = {}
            
            # Monthly trends
            cursor.execute("""
                SELECT 
                    strftime('%Y-%m', start_date) as month,
                    COUNT(*) as pos_count,
                    SUM(po_value) as total_value
                FROM purchase_orders
                GROUP BY strftime('%Y-%m', start_date)
                ORDER BY month DESC
                LIMIT 12
            """)
            analytics['monthly_trends'] = [dict(row) for row in cursor.fetchall()]
            
            # Top clients by value
            cursor.execute("""
                SELECT 
                    cc.name,
                    COUNT(po.id) as pos_count,
                    SUM(po.po_value) as total_value
                FROM client_companies cc
                JOIN purchase_orders po ON cc.id = po.client_id
                GROUP BY cc.id, cc.name
                ORDER BY total_value DESC
                LIMIT 10
            """)
            analytics['top_clients'] = [dict(row) for row in cursor.fetchall()]
            
            # Status distribution
            cursor.execute("""
                SELECT status, COUNT(*) as count, SUM(po_value) as total_value
                FROM purchase_orders
                GROUP BY status
            """)
            analytics['status_distribution'] = [dict(row) for row in cursor.fetchall()]
            
            return analytics
            
    def export_to_dataframe(self, table_name: str) -> pd.DataFrame:
        """Export table data to pandas DataFrame"""
        with sqlite3.connect(self.db_path) as conn:
            if table_name == "purchase_orders_detailed":
                query = """
                    SELECT 
                        po.po_number,
                        sbu.name as sbu_name,
                        cc.name as client_name,
                        po.po_value,
                        po.currency,
                        po.start_date,
                        po.expiry_date,
                        po.status,
                        po.project_name,
                        po.contract_type,
                        po.payment_terms
                    FROM purchase_orders po
                    JOIN sbu ON po.sbu_id = sbu.id
                    JOIN client_companies cc ON po.client_id = cc.id
                    ORDER BY po.start_date DESC
                """
            else:
                query = f"SELECT * FROM {table_name}"
                
            return pd.read_sql_query(query, conn)
            
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """Create a backup of the database"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_sbu_po_{timestamp}.db"
            
        shutil.copy2(self.db_path, backup_path)
        return backup_path
        
    def get_expiring_pos(self, days_ahead: int = 30) -> List[Dict]:
        """Get POs expiring within specified days"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    po.po_number,
                    sbu.name as sbu_name,
                    cc.name as client_name,
                    po.po_value,
                    po.expiry_date,
                    po.status,
                    julianday(po.expiry_date) - julianday('now') as days_remaining
                FROM purchase_orders po
                JOIN sbu ON po.sbu_id = sbu.id
                JOIN client_companies cc ON po.client_id = cc.id
                WHERE po.status = 'Active'
                AND julianday(po.expiry_date) - julianday('now') <= ?
                AND julianday(po.expiry_date) - julianday('now') >= 0
                ORDER BY days_remaining ASC
            """, (days_ahead,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_client(self, client_id: int, name: str, industry_sector: str = "",
                     contact_person: str = "", email: str = "", phone: str = "",
                     address: str = "", country: str = "") -> bool:
        """Update an existing client company"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE client_companies 
                SET name = ?, industry_sector = ?, contact_person = ?, 
                    email = ?, phone = ?, address = ?, country = ?
                WHERE id = ?
            """, (name, industry_sector, contact_person, email, phone, address, country, client_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_client(self, client_id: int) -> bool:
        """Delete a client company (only if no associated POs)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check for associated POs
            cursor.execute("SELECT COUNT(*) FROM purchase_orders WHERE client_id = ?", (client_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                raise ValueError(f"Cannot delete client: {count} purchase orders are associated with this client")
            
            cursor.execute("DELETE FROM client_companies WHERE id = ?", (client_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def update_purchase_order(self, po_id: int, po_number: str, sbu_id: int, client_id: int,
                             po_value: float, currency: str, start_date: str, expiry_date: str,
                             status: str = "Active", project_name: str = "",
                             project_description: str = "", contract_type: str = "",
                             payment_terms: str = "") -> bool:
        """Update an existing purchase order"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get old status for history tracking
            cursor.execute("SELECT status FROM purchase_orders WHERE id = ?", (po_id,))
            result = cursor.fetchone()
            if not result:
                return False
            old_status = result[0]
            
            cursor.execute("""
                UPDATE purchase_orders 
                SET po_number = ?, sbu_id = ?, client_id = ?, po_value = ?, currency = ?,
                    start_date = ?, expiry_date = ?, status = ?, project_name = ?,
                    project_description = ?, contract_type = ?, payment_terms = ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (po_number, sbu_id, client_id, po_value, currency, start_date, expiry_date,
                  status, project_name, project_description, contract_type, payment_terms, po_id))
            
            # Add to status history if status changed
            if old_status != status:
                cursor.execute("""
                    INSERT INTO po_status_history (po_id, old_status, new_status, notes) 
                    VALUES (?, ?, ?, ?)
                """, (po_id, old_status, status, "Updated via edit"))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_purchase_order(self, po_id: int) -> bool:
        """Delete a purchase order"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Delete from status history first (foreign key constraint)
            cursor.execute("DELETE FROM po_status_history WHERE po_id = ?", (po_id,))
            
            # Delete the purchase order
            cursor.execute("DELETE FROM purchase_orders WHERE id = ?", (po_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_client_by_id(self, client_id: int) -> Optional[Dict]:
        """Get a specific client by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM client_companies WHERE id = ?", (client_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def get_purchase_order_by_id(self, po_id: int) -> Optional[Dict]:
        """Get a specific purchase order by ID with joined data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT po.*, sbu.name as sbu_name, cc.name as client_name
                FROM purchase_orders po
                JOIN sbu ON po.sbu_id = sbu.id
                JOIN client_companies cc ON po.client_id = cc.id
                WHERE po.id = ?
            """, (po_id,))
            result = cursor.fetchone()
            return dict(result) if result else None