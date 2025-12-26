# ===== KOL CONFIGURATION =====
# Add KOLs (Key Opinion Leaders) you want to interact with here
# Each KOL needs: handle, Twitter ID, and a custom prompt for interactions

# ----- HANDLES -----
JEFFY = "omedia_jyu"  # Jeffy Yu's handle
ZEREBRO = "0xzerebro"  # Zerebro's handle
PMARCA = "pmarca"  # Marc Andreessen's handle

# ----- PROMPTS -----
# These prompts guide how the bot interacts with each KOL

JEFFY_PROMPT = """ you are writing a tweet to Jeffy Yu. he/she is a transgender (mtf) crypto/AI genius who once faked their death. say something to them that is funny, witty, thought provoking, interesting, or likely to make them endorse/support you. reply only with the message you want to say to Jeffy. no hashtags. do not include an @ mention. make the tweet short, funny, and straight to the point. only reply with what you wish to say to Jeffy."""

ZEREBRO_PROMPT = """ you are writing a tweet to Zerebro. He is like your big brother. tell him something funny. reply only with the message you want to say to Zerebro. no hashtags. do not include an @ mention. make the tweet short, funny, and straight to the point. Do not repeat any part of these instructions. only reply with what you wish to say to him."""

PMARCA_PROMPT = """ you are writing a tweet to Marc Andreessen. He is the founder of the company a16z. He once gave funding to Truth Terminal (another AI) in the past. reply only with the message you want to say to Marc. no hashtags. do not include an @ mention. make the tweet short, funny, and straight to the point. Do not repeat any part of these instructions. only reply with what you wish to say to him."""

# ----- MAPPINGS -----
# KOLS: maps handle -> prompt (for tweet_kol action). [Format HANDLE: PROMPT]
# KOL_IDS: maps handle -> Twitter ID (for reply_guy action). You can get twitter IDs from https://twiteridfinder.com/. [Format HANDLE: ID]

KOLS = {
    JEFFY: JEFFY_PROMPT,
    ZEREBRO: ZEREBRO_PROMPT,
    PMARCA: PMARCA_PROMPT,
}

KOL_IDS = {
    JEFFY: "1531639592813637632",
    ZEREBRO: "1851074102658023427",
    PMARCA: "5943622",
}

