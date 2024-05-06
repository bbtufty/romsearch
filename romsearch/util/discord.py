from discordwebhook import Discord

def discord_push(url,
                 name,
                 fields,
                 ):
    """Post a message to Discord"""

    discord = Discord(url=url)
    discord.post(
        embeds=[
            {
                "author": {
                    "name": name,
                    "url": "https://github.com/bbtufty/romsearch",
                },
                "fields": fields
            }
        ],
    )

    return True
