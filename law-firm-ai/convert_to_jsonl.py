import json
import os

def convert_json_to_jsonl(input_file, output_file):
    """Converts a JSON file to JSONL format."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        with open(output_file, 'w', encoding='utf-8') as f:
            for item in data:
                if 'response' in item:
                    item['completion'] = item.pop('response')
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"Successfully converted {input_file} to {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {input_file}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Correctly reference the file from the root directory
    json_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'law_firm_dataset.json')
    jsonl_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'law_firm_dataset.jsonl')
    
    convert_json_to_jsonl(json_file_path, jsonl_file_path)