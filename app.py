import os
import json
import logging
import filecmp
import shutil
import tempfile

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )

def load_config():
    config_path = 'config.json'
    if not os.path.exists(config_path):
        logging.error(f"Configuration file {config_path} not found.")
        raise FileNotFoundError(f"Configuration file {config_path} not found.")
    
    #konfigurace by mela udeatl importovani nazvu a nasledne importu sitove cesty / cesty pro ukladani souboru
    
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    
    return config

def compare_directories(dir1, dir2):
    """
    Compare two directories and return True if they are identical, False otherwise.
    """
    logging.debug(f"Comparing directories: {dir1} and {dir2}")
    
    comparison = filecmp.dircmp(dir1, dir2)
    
    if comparison.diff_files or comparison.funny_files:
        logging.debug(f"Differences found in files: {comparison.diff_files} and {comparison.funny_files}")
        return False
    
    for sub_dir in comparison.subdirs.values():
        if not compare_directories(sub_dir.left, sub_dir.right):
            return False
    
    return True