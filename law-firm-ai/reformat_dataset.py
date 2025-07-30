import json
import os
import re

def reformat_dataset(input_file, output_file):
    """
    Reformats the dataset from the original JSON format to a new JSONL format
    with 'input' and 'output' keys for model training.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)

        with open(output_file, 'w', encoding='utf-8') as f:
            for item in original_data:
                # Create the 'input' field with a prompt
                prompt = "Extract the PII from the following text:"
                input_text = f"{prompt}\n{item.get('anonymized_text', '')}"

                # Create the 'output' field from the rehydration map
                rehydration_map = item.get('rehydration_map', {})
                
                # Clean the keys in the rehydration map (e.g., "[PER_1]" -> "PER_1")
                cleaned_output = {re.sub(r'\[|\]', '', k): v for k, v in rehydration_map.items()}

                # Create the new data structure
                new_item = {
                    "input": input_text,
                    "output": cleaned_output
                }

                # Write the new item as a JSON line
                f.write(json.dumps(new_item, ensure_ascii=False) + '\n')
        
        print(f"Successfully reformatted {input_file} to {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {input_file}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Path to the original JSON dataset
    json_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'law_firm_dataset.json')
    
    # Path for the new reformatted JSONL file
    reformatted_jsonl_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reformatted_dataset.jsonl')
    
    reformat_dataset(json_file_path, reformatted_jsonl_path)