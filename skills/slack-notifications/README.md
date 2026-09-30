# slack-notifications: setup guide

This guide gets a private Slack channel receiving updates from your jobs, with
the smallest permissions that work. Later, if you want, the agent can also read
questions from that channel and answer them. It takes about 15 minutes, and you
need no Slack admin rights unless your workspace requires approval for new apps.

## Why bother

Long jobs fail when nobody is looking. On a shared GPU cluster a run can sit in
the queue overnight, start at 7 a.m., and crash 20 seconds later. Unless someone
checks, it stays dead until they do.

The worked example in [`references/job-tracking.md`](references/job-tracking.md)
is a set of eight Slurm jobs, an LLM labelling pipeline over a 546-case cohort,
that kept dying of an intermittent GPU crash. With this skill:

- the student and their PI each got a Slack message when a job started, when its
  model server came up, and whether it survived the startup window where the
  crash usually hit;
- a failure produced an **issue report** within a minute: the state, node,
  runtime, cases done, likely cause (early vs. mid-run crash), the key error
  lines, and a suggested next step;
- hourly progress updates were posted only when something had actually changed;
- the PI could ask "how are they doing?" in the channel and get an answer from
  the supervising agent, without logging in to the cluster.

## What you'll set up

```
your jobs ──► slurm-slack-watch ──► slack-notify ──(webhook)──► #your-tracker
                                                                     │
agent session ◄── slack-inbox ◄──(bot token, read)───────────────────┘
      └──────────► slack-reply ──(bot token, chat:write)──► reply in thread
```

- **Notifications only** need steps 1–3 and 6–7: a webhook, which can only
  post into one channel.
- **Two-way** (the agent reads and answers) also needs step 4, a bot token.

## 1. Create a private channel

In Slack: **+ Add channels → Create a new channel**, name it (e.g.
`#jobs-tracker`), and set it to **Private**. Invite the people who should see
updates.

Use a private channel. The bot's read permission for private channels
(`groups:history`) only covers channels it has been invited to, so it can't
see anything else.

## 2. Create a Slack app

1. Go to <https://api.slack.com/apps> → **Create New App → From scratch**.
2. Name it (e.g. `clusterjobs`) and pick your workspace.

If Slack says the app needs admin approval, that's your workspace's policy.
Ask an admin, or use Slurm's built-in email (`--mail-type=BEGIN,END,FAIL`),
which needs no app at all.

## 3. Add an incoming webhook (for posting)

1. In the app, open **Incoming Webhooks** and switch it **On**.
2. Click **Add New Webhook to Workspace**, pick your private channel, and
   **Allow**.
3. Copy the URL (`https://hooks.slack.com/services/…`). **Treat it as a
   password**: anyone holding it can post into the channel.

## 4. (Two-way only) Add a bot token with least privilege

Under **OAuth & Permissions → Bot Token Scopes**, add exactly these:

| Scope | Grant? | What it allows |
|---|---|---|
| `groups:history` | **Yes** | Read messages in private channels the bot has been invited to |
| `chat:write` | **Yes** | Post and reply in threads, in channels the bot is in |
| `incoming-webhook` | (added by step 3) | Post through the webhook |
| `groups:write` | **No** | *Manage* private channels (create, rename, archive, add or remove members). Despite the name, this is not about writing messages. |
| `channels:history` | Only for a public channel | Read public channels the bot is in |
| `users:read`, `groups:read` | No | Not needed; member IDs go in the config instead |

Then click **Install / Reinstall to Workspace** and copy the **Bot User OAuth
Token** (`xoxb-…`).

Scope changes only take effect when you **reinstall**. Removing a scope in the
settings page does not change a token you already have. To be sure a scope is
gone, use **Revoke All OAuth Tokens** and reinstall; this also rotates the
token. Revoking removes the bot from its channels, so invite it back (step 5).

## 5. Invite the bot and collect IDs

- In the channel, type `/invite @<your app name>`.
- **Channel ID**: click the channel name; it's at the bottom of **About**.
  It starts with `C`.
- **Member IDs** of the people whose requests the agent may act on: open their
  profile → **⋮ → Copy member ID** (starts with `U`).

IDs are not secrets, so they can go in the config file and in chat.

## 6. Save the secrets privately

Paste each secret into **your own terminal**, not into an agent chat.
Anything pasted into a chat becomes part of its transcript.

```bash
# Webhook URL (paste, then Enter; -s keeps it off the screen)
read -rs URL && printf '%s\n' "$URL" > ~/.slack-webhook && chmod 600 ~/.slack-webhook && unset URL

# Bot token (two-way only)
read -rs T && printf '%s\n' "$T" > ~/.slack-bot-token && chmod 600 ~/.slack-bot-token && unset T
```

Then create the config file, which holds IDs and paths but no secrets:

```bash
mkdir -p ~/.config/slack-notifications
install -m 600 <skill-dir>/scripts/config.example ~/.config/slack-notifications/config
$EDITOR ~/.config/slack-notifications/config   # set SLACK_CHANNEL and SLACK_AUTHORISED
```

The scripts refuse to use a secret file that other users can read.

## 7. Test

```bash
S=<skill-dir>/scripts
SLACK_NOTIFY_DRYRUN=1 $S/slack-notify "dry run: nothing is posted"
$S/slack-notify "hello from the cluster"                   # should appear in the channel
SLACK_NOTIFY_DRYRUN=1 $S/slack-notify "xoxb-1234567890-abcdefghij"  # exit 3: blocked
```

## Running it

**Watch Slurm jobs** (notify-only, detached so it survives logout):

```bash
setsid nohup $S/slurm-slack-watch 123456 123457 \
  > ~/.local/state/slurm-slack-watch-$(date +%F-%H%M).log 2>&1 < /dev/null &
$S/slurm-slack-watch --dry-report 123456   # preview a finished job's report
```

Configure progress counts, extra logs and the "service is up" line in the
config file (see `config.example`). Stop the watcher with `kill <pid>`, not
`pkill -f`, which also matches the shell running it.

**Two-way**: the agent runs `slack-inbox` under its event watcher (Claude Code:
the Monitor tool) and answers with `slack-reply <thread> "…"`. This only works
while that agent session is open. Keep it in `tmux` if it has to run overnight.

## If a credential leaks

| Leaked | Someone could… | Could not… |
|---|---|---|
| Webhook URL | Post messages into that one channel | Read anything; instruct the agent (bot posts are ignored on read) |
| Bot token with the scopes above | Read the channels the bot is in, and post there | Read DMs, public channels or files; act as you; touch the cluster |

**Fix:** regenerate the webhook (Incoming Webhooks page), or revoke tokens and
reinstall (step 4). Then re-save with `read -rs`.

## Pitfalls we hit

- **`channel_not_found` on a private channel** usually means the bot isn't a
  member. Slack reports "not a member" the same way as "doesn't exist".
- **Scopes didn't change**: you have to reinstall the app (step 4).
- **`groups:write` isn't for messages.** Posting is `chat:write`.
- **The watcher went quiet**: it was started inside a session that ended. Use
  `setsid nohup`, and check it's alive with `pgrep -af slurm-slack-watch`.
- **A "test" printed nothing**: the test harness lost the output. Rerun with
  output sent to a file before blaming the code.
