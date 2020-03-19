from zenmoney import *

oauth = OAuth2('https://t.me/zenmoney_statistics_bot?start=', 'consumer_key', 'consumer_secret', 'user_name', 'user_pass')
api = Request(oauth.token)
diff = api.diff(Diff(**{'serverTimestamp': 1}))

print(diff)
