# blackfriday.onlinedecoded.com: static deal pages and sitemap

## What's in this folder
- 8 category hubs: `/hosting/`, `/plugins/`, `/marketing/`, `/ai-tools/`, `/seo-tools/`, `/design/`, `/vpn-security/`, `/utilities/`
- 116 deal pages at `/{category}/{slug}/`, the same paths as your old `#/category/slug/` routes, minus the `#`
- `sitemap.xml`: 125 real URLs (homepage, 8 categories, 116 deals)
- `og-image.png`: 1200×630 social share image
- `index.html`: your homepage with the fixes applied

## Step 1: Upload to the GitHub Pages repo
Copy everything except this README and the snippet file into the repo root, next to `index.html`. Replace the old `sitemap.xml`, then commit. GitHub Pages serves `/hosting/kinsta-black-friday/` from `hosting/kinsta-black-friday/index.html` automatically.

## Step 2: Use the fixed index.html in this folder
`index.html` in this folder already has every homepage fix applied. Upload it in place of your current one.
- The menu, the provider names and the "Deal Details" buttons are now real links to the category and deal pages.
- Schema URLs no longer use `#/`, and the share image tags are added.
- The FAQ is visible on the page, matching its schema, and the claims that can't be verified are toned down.
- The popup no longer appears on mobile.
- Old `#/...` links redirect to the new pages.
- The footer links to OnlineDecoded.com and to each category.

## Step 3: Google Search Console
1. Add a **Domain property** for `onlinedecoded.com`. It covers every subdomain. A URL-prefix property for `https://blackfriday.onlinedecoded.com/` also works.
2. Open Sitemaps and submit `https://blackfriday.onlinedecoded.com/sitemap.xml`.
3. Use URL Inspection → Request indexing on the homepage, all 8 category pages and your top 10 deal pages. There's a daily quota, so start with the pages that matter most.

## Step 4: Link to it from www.onlinedecoded.com
- Add a "Black Friday Deals" menu item or homepage banner pointing to the subdomain.
- In each Black Friday post on the main site, link to the matching subdomain page, for example the Kinsta post → `/hosting/kinsta-black-friday/`.

## Each season
Keep the same URLs. Update the prices, the year in titles and `<lastmod>` in the sitemap. Then rerun `build.py` if you're using it.
