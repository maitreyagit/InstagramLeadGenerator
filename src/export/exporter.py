import json
import os
import pandas as pd
from typing import List, Dict, Any
import logging

logger = logging.getLogger("instagram_scraper.exporter")

class Exporter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def export(self, data: List[Dict[str, Any]], filename: str, format_type: str = "json"):
        if not data:
            logger.warning("No data to export.")
            return

        base_path = os.path.join(self.output_dir, filename)
        
        try:
            if format_type.lower() == "json":
                path = f"{base_path}.json"
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info(f"Data exported to {path}")
                
            elif format_type.lower() in ["csv", "excel"]:
                # Convert complex types (lists, dicts) to strings for CSV/Excel
                clean_data = []
                for item in data:
                    clean_item = {}
                    for k, v in item.items():
                        if isinstance(v, (list, dict)):
                            clean_item[k] = json.dumps(v)
                        else:
                            clean_item[k] = v
                    clean_data.append(clean_item)
                    
                df = pd.DataFrame(clean_data)
                
                if format_type.lower() == "csv":
                    path = f"{base_path}.csv"
                    df.to_csv(path, index=False, encoding='utf-8')
                    logger.info(f"Data exported to {path}")
                else:
                    path = f"{base_path}.xlsx"
                    df.to_excel(path, index=False)
                    logger.info(f"Data exported to {path}")
            else:
                logger.error(f"Unsupported format type: {format_type}")
                
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
