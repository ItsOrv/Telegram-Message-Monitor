import os
import json
from dotenv import load_dotenv
import logging
from typing import Dict, Any, Union

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, filename: str = "clients.json", config: Dict[str, Any] = None):
        """
        Initialize ConfigManager with a configuration file.

        :param filename: Name of the JSON configuration file
        :param config: Optional dictionary to initialize config, if None loads from file
        """
        self.filename = filename
        self.default_config = {
            "TARGET_GROUPS": [],
            "KEYWORDS": [],
            "IGNORE_USERS": [],
            "clients": []
        }
        self.config = config if config is not None else self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from the JSON file.
        
        :return: Loaded configuration dictionary, default config if loading fails
        """
        logger.info(f"Loading config from {self.filename}")
        
        if not os.path.exists(self.filename):
            logger.warning(f"Config file {self.filename} does not exist. Creating a new one.")
            self.save_config()
            return self.default_config.copy()

        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                logger.info("Config file loaded successfully")
                return {**self.default_config, **loaded_config}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON in {self.filename}: {e}")
            return self.default_config.copy()
        except Exception as e:
            logger.error(f"Unexpected error loading config: {e}")
            return self.default_config.copy()

    def save_config(self, new_config: Dict[str, Any] = None) -> bool:
        """
        Save the current configuration to the JSON file.
        
        :param new_config: Optional new configuration to merge before saving
        :return: True if save was successful, False otherwise
        """
        logger.info("Saving config to file")
        
        if new_config:
            self.merge_config(new_config)

        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info("Config saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving config to {self.filename}: {e}")
            return False

    def update_config(self, key: str, value: Any) -> bool:
        """
        Update a specific key in the configuration and save.
        
        :param key: The configuration key to update
        :param value: The new value to set
        :return: True if update and save were successful, False otherwise
        """
        logger.info(f"Updating config key: {key}")
        
        if key not in self.config:
            logger.warning(f"Key {key} not found in config")
            return False
            
        self.config[key] = value
        return self.save_config()

    def merge_config(self, new_config: Dict[str, Any]) -> None:
        """
        Merge the new configuration with the existing configuration.
        
        :param new_config: The new configuration dictionary to merge
        """
        logger.info("Merging new configuration")
        
        for key, value in new_config.items():
            if key in self.config:
                # Append to lists without duplicates or override non-list values
                if isinstance(self.config[key], list) and isinstance(value, list):
                    self.config[key] = list(dict.fromkeys(self.config[key] + value))
                else:
                    self.config[key] = value
            else:
                self.config[key] = value

    def get_config(self, key: str = None) -> Union[Dict[str, Any], Any]:
        """
        Get the entire configuration or a specific key's value.
        
        :param key: The key to retrieve, if None returns entire config
        :return: The value of the specified key or the entire config dictionary
        """
        logger.info(f"Fetching config for key: {key if key else 'all'}")
        
        if key is None:
            return self.config
        return self.config.get(key, None)
