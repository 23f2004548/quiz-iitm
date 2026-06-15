import sys
import json
import argparse
from app import create_app
from app.utils.ingester import validate_and_ingest_questions

def main():
    parser = argparse.ArgumentParser(description="Ingest quiz data into LinuxMaster database.")
    parser.add_argument("file_path", help="Path to the JSON data file containing questions.")
    parser.add_argument("--subject", default="Linux System Commands", help="Default subject category.")
    parser.add_argument("--topic", default="Week 1 Overview", help="Default topic category.")
    
    args = parser.parse_args()
    
    app = create_app()
    with app.app_context():
        try:
            with open(args.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                print("Error: JSON root must be a list of question objects.")
                sys.exit(1)
                
            imported, skipped = validate_and_ingest_questions(
                data, 
                default_subject=args.subject, 
                default_topic=args.topic
            )
            print(f"Ingestion complete!")
            print(f"  - Imported: {imported} questions")
            print(f"  - Skipped (duplicates): {skipped} questions")
            
        except FileNotFoundError:
            print(f"Error: File not found at '{args.file_path}'")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format - {e.message}")
            sys.exit(1)
        except Exception as e:
            print(f"Error during ingestion: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    main()
