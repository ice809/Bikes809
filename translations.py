TRANSLATIONS = {
    'cs': {
        'garaze': 'Garáž',
        'motobase': 'MotoBase',
        'high_fidelity_mode': 'High Fidelity Mode: On',
        'moto_storage': 'MotoBase High-Resolution Storage System',
        'back_to_garage': 'Zpět do garáže',
        'explore_archive': 'Prozkoumat Archiv',
        'database_empty': 'Database Empty',
        'no_brands': 'No brands detected in',
        'back_on_models': 'Zpět na modely',
        'archive': 'Archiv',
        'shots_in_quality': 'Snímků v plné kvalitě',
        'open_original': 'OTEVŘÍT ORIGINÁL',
        'master_asset': 'Master_Asset_',
        'no_high_res_data': 'No High-Res Data',
    },
    'en': {
        'garaze': 'Garage',
        'motobase': 'MotoBase',
        'high_fidelity_mode': 'High Fidelity Mode: On',
        'moto_storage': 'MotoBase High-Resolution Storage System',
        'back_to_garage': 'Back to Garage',
        'explore_archive': 'Explore Archive',
        'database_empty': 'Database Empty',
        'no_brands': 'No brands detected in',
        'back_on_models': 'Back to Models',
        'archive': 'Archive',
        'shots_in_quality': 'Shots in Full Quality',
        'open_original': 'OPEN ORIGINAL',
        'master_asset': 'Master_Asset_',
        'no_high_res_data': 'No High-Res Data',
    }
}

def get_translations(lang='cs'):
    """Vrátí translations pro daný jazyk."""
    return TRANSLATIONS.get(lang, TRANSLATIONS['cs'])
