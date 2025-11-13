# REDDIT ACCOUNT TRACKING SHEET
# Keep track of account creation progress

| Account | Email | Reddit Username | Password | Reddit Client ID | Reddit Client Secret | Status | Notes |
|---------|-------|-----------------|----------|------------------|---------------------|--------|-------|
| Account 1 (Main) | (your main) | (your main) | (your main) | VU7nzsbqXjvdtyQ9s8UNWA | bSUUGRKY2aUd9VDxpODNowmcXsjb1w | ✅ DONE | On cooldown until 6:30 PM Nov 11 |
| Account 2 | syrai02@mailinator.com | | | | | ⏳ TODO | For: Angry + Sad |
| Account 3 | syrai03@mailinator.com | | | | | ⏳ TODO | For: Energy + Party |
| Account 4 | syrai04@mailinator.com | | | | | ⏳ TODO | For: Romantic + Peaceful |
| Account 5 | syrai05@mailinator.com | | | | | ⏳ TODO | For: Night + Nostalgic |
| Account 6 | syrai06@mailinator.com | | | | | ⏳ TODO | For: Drive + Dark |
| Account 7 | syrai07@mailinator.com | | | | | ⏳ TODO | For: Anxious + Introspective |
| Account 8 | syrai08@mailinator.com | | | | | ⏳ TODO | For: Bitter + Bored |
| Account 9 | syrai09@mailinator.com | | | | | ⏳ TODO | For: Chaotic + Confident |
| Account 10 | syrai10@mailinator.com | | | | | ⏳ TODO | For: Excited + Grateful |
| Account 11 | syrai11@mailinator.com | | | | | ⏳ TODO | For: Hopeful + Jealous |
| Account 12 | syrai12@mailinator.com | | | | | ⏳ TODO | For: Playful |

---

## WORKFLOW FOR EACH ACCOUNT:

### Step 1: Create Reddit Account
1. Go to https://reddit.com/register
2. Email: Use the email from table above
3. Username: Suggest `syrai_02`, `syrai_03`, etc.
4. Password: Create one and write it in table
5. Click verification email link from Mailinator

### Step 2: Create Reddit API App
1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app..."
3. Fill in:
   - Name: "VibeCheck Scraper Account#"
   - Type: Script
   - Description: "Music emotion mapping data collection"
   - Redirect URI: http://localhost:8080
4. Copy CLIENT_ID and CLIENT_SECRET to table

### Step 3: Update .env File
1. Open `.env.account#` file
2. Replace `YOUR_ACCOUNT#_CLIENT_ID_HERE` with actual CLIENT_ID
3. Replace `YOUR_ACCOUNT#_SECRET_HERE` with actual CLIENT_SECRET
4. Save file
5. Mark Status as ✅ DONE in table

### Step 4: Test
```bash
python smart_scrapers/scrape_angry.py 2
```

---

## QUICK TIPS:

- Create 2-3 accounts at a time, then take a break
- Use different browsers/incognito for each
- Write passwords immediately (easy to forget!)
- Check Mailinator inbox: https://www.mailinator.com/v4/public/inboxes.jsp?to=syrai##
- Update this tracking sheet as you go!

---

## PROGRESS TRACKER:
- [ ] Account 2
- [ ] Account 3
- [ ] Account 4
- [ ] Account 5
- [ ] Account 6
- [ ] Account 7
- [ ] Account 8
- [ ] Account 9
- [ ] Account 10
- [ ] Account 11
- [ ] Account 12
