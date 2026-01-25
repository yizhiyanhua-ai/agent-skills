# Skill Knowledge Extractor

[🇨🇳 中文](./README_CN.md)

Extract reusable knowledge patterns from conversations, documents, or work experiences to create Skills.

## Features

- Analyze conversation records (sales calls, customer service chats)
- Extract patterns from work documents and notes
- Generate Skill drafts automatically
- Support both Chinese and English

## Usage

```bash
# Analyze a conversation file
python scripts/extract_patterns.py --input chat.txt --type conversation

# Analyze a document
python scripts/extract_patterns.py --input notes.md --type document

# Output as JSON
python scripts/extract_patterns.py --input data.txt --json
```

## Pattern Types

- **Opening patterns** - Standard greetings and introductions
- **Diagnosis patterns** - Problem discovery questions
- **Objection handling** - Responses to customer concerns
- **Closing patterns** - Deal closing techniques
- **Checklist patterns** - Verification items
- **Template patterns** - Reusable document structures
- **Decision tree patterns** - Conditional logic flows
- **Procedure patterns** - Step-by-step workflows

## License

MIT
