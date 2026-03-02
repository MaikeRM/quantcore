import os
import sys
from typing import Any, Dict, List
from hydra import compose, initialize_config_dir
from hydra.core.global_hydra import GlobalHydra
from omegaconf import OmegaConf, DictConfig
from .validation import RootConfig
from ..exceptions import ConfigurationError

class Settings:
    _instance = None
    _config: RootConfig = None
    _omega_config: DictConfig = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _get_flatten_env_mapping(self, d: Dict, prefix: str = "") -> Dict[str, str]:
        keys = {}
        for k, v in d.items():
            # e.g., quantcore.risk.var.confidence_level
            path = f"{prefix}{k}" if prefix == "" else f"{prefix}.{k}"
            
            # create env format: QUANTCORE_RISK_VAR_CONFIDENCE_LEVEL
            # Note: we drop the first 'quantcore' to avoid QUANTCORE_QUANTCORE
            path_parts = path.split(".")
            if path_parts[0] == "quantcore":
                env_parts = path_parts[1:]
            else:
                env_parts = path_parts
                
            env_name = "QUANTCORE_" + "_".join(env_parts).upper()
            keys[env_name] = path
            
            if isinstance(v, dict) or isinstance(v, DictConfig):
                keys.update(self._get_flatten_env_mapping(v, path))
        return keys

    def _get_env_overrides(self, base_config: DictConfig) -> List[str]:
        mapping = self._get_flatten_env_mapping(base_config)
        # Add a specific alias for the requirement
        mapping["QUANTCORE_RISK_VAR_CONFIDENCE"] = "quantcore.risk.var.confidence_level"
        
        overrides = []
        for env_key, env_val in os.environ.items():
            if env_key in mapping:
                path = mapping[env_key]
                overrides.append(f"{path}={env_val}")
                
        return overrides

    def _get_cli_overrides(self) -> List[str]:
        overrides = []
        # basic parsing for simple python script executions
        for arg in sys.argv[1:]:
            if "=" in arg and not arg.startswith("-"):
                overrides.append(arg)
        return overrides

    def _load_config(self):
        # determine absolute path to config directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # quantcore/quantcore/core/utils/config/settings.py
        # root is 5 folders up
        repo_root = os.path.abspath(os.path.join(current_dir, "../../../.."))
        config_dir = os.path.join(repo_root, "config")
        
        # Fallback if library is installed
        if not os.path.exists(config_dir):
            config_dir = os.path.join(current_dir, "default_config_fallback") 
            # (In a real deploy we might package the yaml)

        if GlobalHydra.instance().is_initialized():
            GlobalHydra.instance().clear()

        # Initialize Hydra and load
        try:
            with initialize_config_dir(version_base="1.3", config_dir=config_dir):
                # We load it first without overrides to build the env map
                base_cfg = compose(config_name="quantcore/default")
                
                env_overrides = self._get_env_overrides(base_cfg)
                cli_overrides = self._get_cli_overrides()
                
                all_overrides = env_overrides + cli_overrides
                cfg = compose(config_name="quantcore/default", overrides=all_overrides)
        except Exception as e:
            raise ConfigurationError(f"Failed to load Hydra configuration: {str(e)}")

        # Convert to primitive dict for Pydantic validation
        cfg_dict = OmegaConf.to_container(cfg, resolve=True)
        
        # Hydra 1.1+ config group nesting fix:
        # If the file puts 'quantcore:' inside it but is loaded as group 'quantcore', it nests
        if "quantcore" in cfg_dict and "quantcore" in cfg_dict["quantcore"] and "version" in cfg_dict["quantcore"]["quantcore"]:
            cfg_dict = {"quantcore": cfg_dict["quantcore"]["quantcore"]}
        
        try:
            # Validate with Pydantic
            self._config = RootConfig.model_validate(cfg_dict)
        except Exception as e:
            raise ConfigurationError(
                f"Configuration validation failed: {str(e)}", 
                hint="Check if your yaml and env overrides define valid types according to the schema."
            )
            
        self._omega_config = cfg

    @property
    def config(self) -> RootConfig:
        return self._config

configuration = Settings()

def get_config() -> RootConfig:
    """Returns the validated Quantcore configuration object."""
    return configuration.config
