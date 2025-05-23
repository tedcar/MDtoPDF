import sys
import os

def resource_path(relative_path_in_bundle):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    In PyInstaller, relative_path_in_bundle is relative to the bundle root (_MEIPASS).
    In development, it's relative to the 'src' directory (where this utils.py is).
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        # For PyInstaller, the path is relative to the bundle root
        return os.path.join(base_path, relative_path_in_bundle)
    except Exception:
        # Not running in a bundle, determine path for development mode
        # This utils.py file is in the 'src' directory.
        # So, os.path.dirname(__file__) is the 'src' directory.
        dev_base_path = os.path.dirname(__file__) 
        # The path is constructed relative to the 'src' directory
        return os.path.join(dev_base_path, relative_path_in_bundle)

if __name__ == '__main__':
    # Example usage (for testing this function directly)
    # Assuming TimesNewRoman.ttf is in the src directory:
    test_font_path_bundle = resource_path('TimesNewRoman.ttf')
    print(f"Example path (TimesNewRoman.ttf): {test_font_path_bundle}")
    # This will print a path relative to 'src' when run in dev,
    # or relative to _MEIPASS when bundled.

    # Example for a hypothetical asset in src/assets/
    # test_asset_path = resource_path('assets/my_icon.ico')
    # print(f"Example path (assets/my_icon.ico): {test_asset_path}")
