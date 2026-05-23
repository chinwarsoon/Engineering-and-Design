import os

def estimate_tokens(text):
    # Heuristic: 1 token approx 4 characters
    return len(text) // 4

def main():
    workplan_dir = 'workplan'
    output_file = 'workplan/condensated_workplan.md'
    
    total_input_chars = 0
    total_input_files = 0
    
    condensed_content = []
    
    print(f"Scanning directory: {workplan_dir}")
    
    for root, dirs, files in os.walk(workplan_dir):
        for file in files:
            if file == 'condensated_workplan.md' or file.endswith('.pyc'):
                continue
                
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    total_input_chars += len(content)
                    total_input_files += 1
                    
                    condensed_content.append(f"## File: {file_path}\n\n")
                    condensed_content.append(content)
                    condensed_content.append("\n\n---\n\n")
            except Exception as e:
                # Skip binary or unreadable files
                pass

    final_text = "".join(condensed_content)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_text)
        
    input_tokens = total_input_chars // 4
    output_tokens = len(final_text) // 4
    
    print("\nToken Usage Report:")
    print(f"Total input files: {total_input_files}")
    print(f"Total input characters: {total_input_chars}")
    print(f"Estimated input tokens: {input_tokens}")
    print(f"Estimated output tokens (condensated file): {output_tokens}")
    print(f"Output file: {output_file}")

if __name__ == "__main__":
    main()
