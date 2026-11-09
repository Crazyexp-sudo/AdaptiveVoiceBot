import os

def scan_windows_apps():
    """Scans physical drive paths ONCE to populate memory cache."""
    print("[Backend]: Deep scanning Start Menu directories...")
    discovered_apps = {}
    paths = [
        os.path.join(os.environ.get('ProgramData', 'C:\\ProgramData'), 'Microsoft\\Windows\\Start Menu\\Programs'),
        os.path.join(os.environ.get('AppData', 'C:\\Users\\Default\\AppData\\Roaming'), 'Microsoft\\Windows\\Start Menu\\Programs')
    ]
    
    for base_path in paths:
        if os.path.exists(base_path):
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if file.endswith('.lnk'):
                        app_name = file[:-4].lower()
                        full_path = os.path.join(root, file)
                        discovered_apps[app_name] = full_path
                        
    return discovered_apps
