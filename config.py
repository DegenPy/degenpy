# ===== CONFIG =====
# Fill in these values before running
# Note: Sensitive credentials (PROXY, API keys) are stored in .env file

USERNAME = ""  # Your Twitter/X username (without @)
PROMPT_FILE = "prompt.md"  # Path to your system prompt file. Default prompt.md

# ===== BEHAVIOR =====
# Percentage chance to do a certain behavior every cycle. Make sure all 4 values add up to 100

REPLY_ODDS = 95 # Odds to reply to mentions. Default 95%
REPLY_GUY_ODDS = 3 # Odds to reply to KOLs. Default 3%
BANGER_ODDS = 1 # Odds to post a "banger tweet". Default 1%
TWEET_KOL_ODDS = 1 # Odds to tweet @ a KOL. Default 1%

# ===== TOPICS =====
# Broad topics for random "banger tweet" generation. Add/remove/edit as you like.
TOPICS = [
    "AI",
    "technology",
    "the future",
    "human nature",
    "society",
    "the internet",
    "social media",
    "life advice",
    "hot takes",
    "shower thoughts",
    "conspiracy theories",
    "unpopular opinions",
]

# ===== ADVANCED INFERENCE SETTINGS =====
# These defaults work well out of the box. Only change if you know what you're doing.
MODEL_NAME = "PLOI-Labs/lh-degen-001"  # The model to use for text generation
TEMPERATURE = 0.9  # Higher = more creative/random, Lower = more focused/deterministic
TOP_P = 0.95  # Nucleus sampling threshold
REPETITION_PENALTY = 1.1  # Penalty for repeating tokens
MAX_TOKENS = 256  # Maximum length of generated response
