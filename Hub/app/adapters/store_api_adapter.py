import json
import logging
from typing import List

import pydantic_core
import requests

from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_gateway import StoreGateway
import datetime

def convert_to_dict(data: ProcessedAgentData) -> dict:
    data_dict = data.model_dump()
    for key, value in data_dict.items():
        if isinstance(value, datetime.datetime):
            data_dict[key] = value.isoformat()
        elif isinstance(value, dict):
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, datetime.datetime):
                    value[sub_key] = sub_value.isoformat()
    return data_dict


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]) -> bool:
    
        data_to_save = [convert_to_dict(data) for data in processed_agent_data_batch]
        try:
            response = requests.post(
                f"{self.api_base_url}/processed_agent_data/",
                json=data_to_save
            )
            if response.status_code == 200:
                logging.info("Data successfully saved to the Store API.")
                return True
            else:
                logging.error(f"Failed to save data to the Store API. Response status: {response.status_code}, Response body: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while trying to save data to the Store API: {e}")
            return False
