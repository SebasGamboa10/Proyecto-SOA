import sys

def save_lines_to_file(filename, lines):
  """
  Saves a list of lines to a text file.

  Args:
    filename: The name of the file to save to.
    lines: A list of strings, each representing a line in the file.
  """
  with open(filename, 'w') as f:
    f.writelines([line + '\n' for line in lines])
    print(f"Successfully saved content to {filename}")

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print("Usage: python util.py [filename] [line1 line2 line3 ...]")
    sys.exit(1)

  filename = sys.argv[1]
  lines = sys.argv[2:]

  save_lines_to_file(filename, lines)