import json
import argparse
import sys
import os

# Add the parent directory to sys.path to allow importing app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.main import app

def extract_openapi(output_path):
    openapi_data = app.openapi()
    with open(output_path, 'w') as f:
        json.dump(openapi_data, f, indent=2)
    print(f"OpenAPI schema exported to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export OpenAPI schema to a file.")
    parser.add_argument("output", help="Output file path for the OpenAPI JSON")
    args = parser.parse_args()
    
    extract_openapi(args.output)
