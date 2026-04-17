"""
Resolution Archiver Module

Archives resolved and archived errors.
Implements archival logic, retention policy, and search retrieval.

Complies with error_handling_module_workplan.md Phase: Resolution Module Implementation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json


class Archiver:
    """
    Archives resolved and archived errors.
    
    Implements:
    - Archival logic for RESOLVED/ARCHIVED errors
    - Archive to error_archive/ folder
    - Retention policy (configurable: 1 year / 3 years / forever)
    - Archive search and retrieval
    """
    
    def __init__(self, archive_path: Optional[str] = None, retention_years: int = 1):
        """
        Initialize archiver with archive path and retention policy.
        
        Breadcrumb: archive_path → retention_policy → archive_index
        
        Args:
            archive_path: Path to error_archive folder
            retention_years: Number of years to retain archived errors (0 = forever)
        """
        self.archive_path = Path(archive_path) if archive_path else Path('error_archive')
        self.retention_years = retention_years
        self.archive_index: List[Dict[str, Any]] = []
        
        # Create archive directory if it doesn't exist
        self.archive_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing archive index
        self._load_index()
    
    def _load_index(self) -> None:
        """Load archive index from JSON file."""
        index_file = self.archive_path / 'archive_index.json'
        try:
            if index_file.exists():
                with open(index_file, 'r') as f:
                    self.archive_index = json.load(f)
        except Exception as e:
            print(f"Failed to load archive index: {e}")
            self.archive_index = []
    
    def _save_index(self) -> None:
        """Save archive index to JSON file."""
        index_file = self.archive_path / 'archive_index.json'
        try:
            with open(index_file, 'w') as f:
                json.dump(self.archive_index, f, indent=2)
        except Exception as e:
            print(f"Failed to save archive index: {e}")
    
    def archive(self, error: Dict[str, Any], categorized: Dict[str, Any], 
               remediation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Archive an error.
        
        Breadcrumb: error → categorized → remediation → archive_file → update_index
        
        Args:
            error: Error dict with error_code and context
            categorized: Categorized error from Categorizer
            remediation: Remediation result from Remediator
        
        Returns:
            Dict with archival result
        """
        error_code = error.get('error_code', '')
        error_id = error.get('error_id', f"{error_code}_{datetime.now().timestamp()}")
        
        # Create archive entry
        archive_entry = {
            'error_id': error_id,
            'error_code': error_code,
            'error': error,
            'categorized': categorized,
            'remediation': remediation,
            'archived_at': datetime.now().isoformat(),
            'retention_until': self._calculate_retention_date()
        }
        
        # Save archive entry to individual file
        archive_file = self.archive_path / f"{error_id}.json"
        try:
            with open(archive_file, 'w') as f:
                json.dump(archive_entry, f, indent=2)
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to archive error: {e}"
            }
        
        # Update index
        self.archive_index.append({
            'error_id': error_id,
            'error_code': error_code,
            'archived_at': archive_entry['archived_at'],
            'retention_until': archive_entry['retention_until'],
            'file': str(archive_file)
        })
        self._save_index()
        
        return {
            'success': True,
            'error_id': error_id,
            'archived_at': archive_entry['archived_at'],
            'retention_until': archive_entry['retention_until'],
            'file': str(archive_file)
        }
    
    def _calculate_retention_date(self) -> Optional[str]:
        """
        Calculate retention expiration date.
        
        Breadcrumb: retention_years → current_date → retention_date
        
        Returns:
            ISO string of retention date, or None if retention is forever
        """
        if self.retention_years == 0:
            return None
        
        retention_date = datetime.now() + timedelta(days=self.retention_years * 365)
        return retention_date.isoformat()
    
    def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search archived errors.
        
        Breadcrumb: query → index_filter → file_load → results
        
        Args:
            query: Search criteria (error_code, date_range, etc.)
        
        Returns:
            List of matching archive entries
        """
        results = []
        
        for entry in self.archive_index:
            # Filter by error code
            if 'error_code' in query and entry['error_code'] != query['error_code']:
                continue
            
            # Filter by date range
            if 'date_from' in query:
                date_from = datetime.fromisoformat(query['date_from'])
                archived_at = datetime.fromisoformat(entry['archived_at'])
                if archived_at < date_from:
                    continue
            
            if 'date_to' in query:
                date_to = datetime.fromisoformat(query['date_to'])
                archived_at = datetime.fromisoformat(entry['archived_at'])
                if archived_at > date_to:
                    continue
            
            # Load full archive entry
            archive_file = Path(entry['file'])
            if archive_file.exists():
                try:
                    with open(archive_file, 'r') as f:
                        full_entry = json.load(f)
                        results.append(full_entry)
                except Exception as e:
                    print(f"Failed to load archive file {archive_file}: {e}")
        
        return results
    
    def retrieve(self, error_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific archived error.
        
        Breadcrumb: error_id → index_lookup → file_load → archive_entry
        
        Args:
            error_id: Error identifier
        
        Returns:
            Archive entry or None if not found
        """
        # Find in index
        for entry in self.archive_index:
            if entry['error_id'] == error_id:
                archive_file = Path(entry['file'])
                if archive_file.exists():
                    try:
                        with open(archive_file, 'r') as f:
                            return json.load(f)
                    except Exception as e:
                        print(f"Failed to load archive file {archive_file}: {e}")
        
        return None
    
    def cleanup_expired(self) -> Dict[str, Any]:
        """
        Remove expired archives based on retention policy.
        
        Breadcrumb: archive_index → retention_check → file_delete → index_update
        
        Returns:
            Dict with cleanup result
        """
        if self.retention_years == 0:
            return {
                'success': True,
                'message': 'No cleanup (retention is forever)',
                'removed': 0
            }
        
        now = datetime.now()
        removed_count = 0
        
        # Filter expired entries
        active_entries = []
        for entry in self.archive_index:
            retention_until = entry.get('retention_until')
            if retention_until:
                retention_date = datetime.fromisoformat(retention_until)
                if now > retention_date:
                    # Remove expired archive file
                    archive_file = Path(entry['file'])
                    if archive_file.exists():
                        archive_file.unlink()
                        removed_count += 1
                else:
                    active_entries.append(entry)
            else:
                active_entries.append(entry)
        
        # Update index
        self.archive_index = active_entries
        self._save_index()
        
        return {
            'success': True,
            'removed': removed_count,
            'message': f'Cleaned up {removed_count} expired archives'
        }
    
    def get_archive_stats(self) -> Dict[str, Any]:
        """
        Get archive statistics.
        
        Breadcrumb: archive_index → size_calculation → stats
        
        Returns:
            Dict with archive statistics
        """
        total_size = 0
        for entry in self.archive_index:
            archive_file = Path(entry['file'])
            if archive_file.exists():
                total_size += archive_file.stat().st_size
        
        return {
            'total_archives': len(self.archive_index),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'retention_policy': f"{self.retention_years} years" if self.retention_years > 0 else "forever",
            'archive_path': str(self.archive_path)
        }
