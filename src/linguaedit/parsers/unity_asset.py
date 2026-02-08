"""Unity .asset parser for Unity localization tables."""

from __future__ import annotations

import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from linguaedit.parsers.po_parser import TranslationEntry


@dataclass
class UnityAssetData:
    """Data structure for Unity .asset files."""
    entries: List[TranslationEntry]
    file_path: str
    metadata: Dict[str, Any] = None
    unity_version: str = ""
    guid: str = ""


def parse_unity_asset(file_path: Union[str, Path]) -> UnityAssetData:
    """Parse Unity .asset file (YAML-based localization table)."""
    path = Path(file_path)
    entries = []
    metadata = {}
    unity_version = ""
    guid = ""
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Unity asset files often have YAML documents separated by ---
    # Split the content into documents
    documents = content.split('--- !u!')
    
    for doc in documents:
        if not doc.strip():
            continue
            
        # Add back the document separator if needed
        if not doc.startswith('!u!'):
            doc = '!u!' + doc
        
        try:
            # Parse YAML document
            data = yaml.safe_load(doc)
            if not isinstance(data, dict):
                continue
            
            # Look for localization table data
            if 'StringTable' in data:
                _parse_string_table(data['StringTable'], entries, str(path))
            elif 'AssetTable' in data:
                _parse_asset_table(data['AssetTable'], entries, str(path))
            elif 'LocalizationTable' in data:
                _parse_localization_table(data['LocalizationTable'], entries, str(path))
            
            # Extract metadata
            if 'm_Name' in data:
                metadata['name'] = data['m_Name']
            if 'm_LocaleId' in data:
                metadata['locale'] = data['m_LocaleId']
                
        except yaml.YAMLError as e:
            print(f"YAML parsing error in {path}: {e}")
            continue
        except Exception as e:
            print(f"Error parsing Unity asset document: {e}")
            continue
    
    # Try to extract Unity version from file header
    lines = content.split('\n')
    for line in lines[:5]:  # Check first few lines
        if line.startswith('%YAML') or line.startswith('%TAG'):
            continue
        if 'Unity' in line:
            unity_version = line.strip()
            break
    
    return UnityAssetData(
        entries=entries,
        file_path=str(path),
        metadata=metadata,
        unity_version=unity_version,
        guid=metadata.get('guid', '')
    )


def _parse_string_table(string_table: Dict[str, Any], entries: List[TranslationEntry], file_path: str):
    """Parse Unity StringTable structure."""
    if 'm_TableData' not in string_table:
        return
    
    table_data = string_table['m_TableData']
    if not isinstance(table_data, list):
        return
    
    for item in table_data:
        if not isinstance(item, dict):
            continue
        
        # Extract key and value
        key = item.get('m_Key', '')
        entry_data = item.get('m_Value', {})
        
        if isinstance(entry_data, dict):
            localized_string = entry_data.get('m_LocalizedValue', '')
            metadata = entry_data.get('m_Metadata', {})
            
            # Create translation entry
            entry = TranslationEntry(
                source=key,
                target=localized_string,
                context=key,
                comments=[],
                locations=[file_path],
                flags=set(),
                previous_source="",
                fuzzy=False
            )
            
            # Add metadata as comments
            if isinstance(metadata, dict):
                for meta_key, meta_value in metadata.items():
                    entry.comments.append(f"{meta_key}: {meta_value}")
            
            entries.append(entry)


def _parse_asset_table(asset_table: Dict[str, Any], entries: List[TranslationEntry], file_path: str):
    """Parse Unity AssetTable structure (for assets, not strings)."""
    # Asset tables typically contain references to other assets
    # For translation purposes, we might extract the key names
    if 'm_TableData' not in asset_table:
        return
    
    table_data = asset_table['m_TableData']
    if not isinstance(table_data, list):
        return
    
    for item in table_data:
        if not isinstance(item, dict):
            continue
        
        key = item.get('m_Key', '')
        entry_data = item.get('m_Value', {})
        
        if isinstance(entry_data, dict):
            # For assets, we might want to track the asset reference
            asset_reference = entry_data.get('m_AssetReference', {})
            asset_guid = asset_reference.get('m_AssetGUID', '') if isinstance(asset_reference, dict) else ''
            
            entry = TranslationEntry(
                source=key,
                target=key,  # Asset keys typically don't get translated
                context=key,
                comments=[f"Asset GUID: {asset_guid}"] if asset_guid else [],
                locations=[file_path],
                flags={'asset-reference'},
                previous_source="",
                fuzzy=False
            )
            
            entries.append(entry)


def _parse_localization_table(localization_table: Dict[str, Any], entries: List[TranslationEntry], file_path: str):
    """Parse generic Unity LocalizationTable structure."""
    # This is a fallback for other localization table formats
    if 'entries' in localization_table:
        table_entries = localization_table['entries']
        if isinstance(table_entries, dict):
            for key, value in table_entries.items():
                entry = TranslationEntry(
                    source=key,
                    target=str(value),
                    context=key,
                    comments=[],
                    locations=[file_path],
                    flags=set(),
                    previous_source="",
                    fuzzy=False
                )
                entries.append(entry)


def save_unity_asset(data: UnityAssetData, file_path: Union[str, Path]) -> None:
    """Save Unity asset data to file."""
    path = Path(file_path)
    
    # Read original file to preserve structure
    original_content = ""
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            original_content = f.read()
    
    # Split into documents
    documents = original_content.split('--- !u!') if original_content else []
    
    # Find and update the StringTable document
    updated_documents = []
    string_table_updated = False
    
    for i, doc in enumerate(documents):
        if not doc.strip():
            if i == 0:  # First empty document due to split
                updated_documents.append(doc)
            continue
        
        # Add back the document separator
        if not doc.startswith('!u!'):
            doc = '!u!' + doc
        
        try:
            data_dict = yaml.safe_load(doc)
            if isinstance(data_dict, dict) and 'StringTable' in data_dict:
                # Update this document with new entries
                updated_doc = _update_string_table_document(data_dict, data.entries)
                updated_documents.append('--- !u!' + updated_doc)
                string_table_updated = True
            else:
                # Keep original document
                updated_documents.append('--- !u!' + doc if i > 0 else doc)
                
        except yaml.YAMLError:
            # If YAML parsing fails, keep original
            updated_documents.append('--- !u!' + doc if i > 0 else doc)
    
    # If no StringTable was found, create a new one
    if not string_table_updated:
        new_document = _create_string_table_document(data.entries, data.metadata)
        updated_documents.append('--- !u!' + new_document)
    
    # Write back to file
    content = ''.join(updated_documents)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def _update_string_table_document(data_dict: Dict[str, Any], entries: List[TranslationEntry]) -> str:
    """Update StringTable document with new entries."""
    string_table = data_dict.get('StringTable', {})
    
    # Create new table data
    table_data = []
    for entry in entries:
        if 'asset-reference' in entry.flags:
            continue  # Skip asset references for string tables
        
        item = {
            'm_Key': entry.source,
            'm_Value': {
                'm_LocalizedValue': entry.target,
                'm_Metadata': {}
            }
        }
        
        # Add metadata from comments
        for comment in entry.comments:
            if ': ' in comment:
                key, value = comment.split(': ', 1)
                item['m_Value']['m_Metadata'][key] = value
        
        table_data.append(item)
    
    string_table['m_TableData'] = table_data
    data_dict['StringTable'] = string_table
    
    # Convert back to YAML
    return yaml.dump(data_dict, default_flow_style=False, allow_unicode=True)


def _create_string_table_document(entries: List[TranslationEntry], metadata: Dict[str, Any]) -> str:
    """Create a new StringTable document."""
    table_data = []
    for entry in entries:
        if 'asset-reference' in entry.flags:
            continue
        
        item = {
            'm_Key': entry.source,
            'm_Value': {
                'm_LocalizedValue': entry.target,
                'm_Metadata': {}
            }
        }
        table_data.append(item)
    
    document = {
        'StringTable': {
            'm_Name': metadata.get('name', 'LocalizationTable'),
            'm_LocaleId': metadata.get('locale', ''),
            'm_TableData': table_data
        }
    }
    
    return yaml.dump(document, default_flow_style=False, allow_unicode=True)


def is_unity_asset_file(file_path: Union[str, Path]) -> bool:
    """Check if file is a Unity asset file."""
    path = Path(file_path)
    
    if path.suffix != '.asset':
        return False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            first_lines = f.read(500)  # Read first 500 characters
            
        # Check for Unity asset file markers
        return ('%YAML' in first_lines or 
                '%TAG' in first_lines or 
                'StringTable' in first_lines or 
                'AssetTable' in first_lines)
    except Exception:
        return False


# Register parser functions
def get_unity_asset_parser_info():
    """Get parser information for registration."""
    return {
        'name': 'Unity Asset',
        'extensions': ['.asset'],
        'parse_func': parse_unity_asset,
        'save_func': save_unity_asset,
        'check_func': is_unity_asset_file,
        'description': 'Unity localization asset files (.asset)'
    }