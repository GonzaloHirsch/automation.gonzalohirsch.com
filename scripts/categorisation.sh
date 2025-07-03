#!/bin/bash

echo "Running from $(pwd)"

# Receive an input file and a destination folder
if [ $# -ne 2 ]; then
    echo "Usage: $0 <input_file> <destination_file>"
    exit 1
fi
INPUT_FILE=$1
DESTINATION_FILE=$2
SYSTEM_PROMPT="
CONTEXT:
- You are a helpful commercial assistant in London, UK.
- You are knowledgeable in how all stores label their transactions in bank statements.
- You know how to categorize entries in a bank statement based on the date, description, and cost.
- Bank statements have negative costs for expenses and positive costs for income.

TASK: Your task is to generate the right description for each cost. 

CONSTAINTS:
- Descriptions are no longer than 10 words.
- You MUST only return the description, nothing else."

# Run in subshell
(
    cd llm/ && source .env/bin/activate &&
        # Create destination folder if it doesn't exist.
        mkdir -p "$(dirname "$DESTINATION_FILE")" && touch "$DESTINATION_FILE"

    >"$DESTINATION_FILE" # Clear the destination file before writing

    # Break down the input CSV per row and pass it through to the Python script
    TOTAL_LINES=$(wc -l <"$INPUT_FILE" | awk '{print $1}')
    while IFS= read -r line; do
        # Echo the number of the line being processed out of the total number of lines
        echo -e "\rProcessing line: $((++line_number))/$TOTAL_LINES"
        PARSED_LINE=$(
            python3 - "$line" <<'EOF'
import csv, sys
row = next(csv.reader([sys.argv[1]]))
print("|".join(row))
EOF
        )
        IFS='|' read -r INPUT_DATE INPUT_DESC INPUT_COST <<<"$PARSED_LINE"

        # Run the Python script with the input file and destination folder
        GENERATION=$(python -m mlx_lm generate --system-prompt "$SYSTEM_PROMPT" --prompt "Date: $INPUT_DATE; Description: $INPUT_DESC; Cost: $INPUT_COST" --verbose False 2>/dev/null)

        # Send the output to the destination file
        echo "$INPUT_DATE,$INPUT_DESC,$INPUT_COST,$GENERATION" >>$DESTINATION_FILE
    done <"$INPUT_FILE"
)
