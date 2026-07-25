import os
import glob
import re

models_dir = "app/models"
for file in glob.glob(f"{models_dir}/*.py"):
    with open(file, "r") as f:
        content = f.read()
    
    # We want to replace Mapped[uuid.UUID] = mapped_column(..., ForeignKey(...)) 
    # with index=True if it doesn't already have it
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if "ForeignKey" in line and "index=True" not in line and "mapped_column" in line:
            # Insert index=True before the closing parenthesis of mapped_column
            line = re.sub(r'(\)\s*)$', r', index=True\1', line)
            # wait, that regex might just append it at the end of the line which might not be mapped_column.
            # a safer way is to just replace the last parenthesis on the line
            if line.endswith(")"):
                line = line[:-1] + ", index=True)"
            elif "), nullable" in line:
                line = line.replace("), nullable", "), index=True, nullable")
            else:
                # find the last parenthesis
                last_paren = line.rfind(")")
                if last_paren != -1:
                    line = line[:last_paren] + ", index=True" + line[last_paren:]
        new_lines.append(line)
        
    with open(file, "w") as f:
        f.write('\n'.join(new_lines))
