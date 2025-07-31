#!/bin/bash

# Check if prompt is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <prompt>"
    echo "Example: $0 \"Explain quantum computing\""
    exit 1
fi

# Get the prompt from command line arguments
PROMPT="$1"

# Run claude with stream-json format and format the output in real-time
claude -p "$PROMPT" --output-format stream-json --verbose 2>&1 | \
while IFS= read -r line; do
    # Only process lines that start with {
    if [ "${line:0:1}" = "{" ]; then
        echo "$line" | jq -r '
          if .type == "assistant" and .message.content then
            .message.content[]? | 
            if .type == "text" then
              .text
            elif .type == "tool_use" then
              "\n🔧 Using tool: " + .name + " - " + .input.description + "\n"
            else
              empty
            end
          elif .type == "user" and .message.content[0].type == "tool_result" then
            "\n📊 Tool result:\n" + (.message.content[0].content // "")
          elif .type == "result" and .result then
            "\n✅ Final result: " + .result
          else
            empty
          end' 2>/dev/null
    fi
done | grep -v "^$" | tee -a claude.log